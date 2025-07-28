from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import asyncpg
import bcrypt
import secrets
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")

# Pydantic models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: str
    department: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None

class UserSettings(BaseModel):
    notifications_email: Optional[bool] = None
    notifications_sms: Optional[bool] = None
    notifications_push: Optional[bool] = None
    alert_types_leaks: Optional[bool] = None
    alert_types_pressure: Optional[bool] = None
    alert_types_quality: Optional[bool] = None
    alert_types_maintenance: Optional[bool] = None
    theme: Optional[str] = None
    language: Optional[str] = None
    date_format: Optional[str] = None
    units: Optional[str] = None
    auto_refresh: Optional[bool] = None
    refresh_interval: Optional[int] = None
    data_retention_days: Optional[int] = None
    debug_mode: Optional[bool] = None

class SystemConfig(BaseModel):
    config_value: dict
    description: Optional[str] = None

# Dependency to get database connection
async def get_db_pool(request: Request):
    return request.app.state.pool

# Helper functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

async def log_audit(pool: asyncpg.Pool, user_id: Optional[str], action: str, 
                   entity_type: Optional[str] = None, entity_id: Optional[str] = None,
                   old_values: Optional[dict] = None, new_values: Optional[dict] = None,
                   ip_address: Optional[str] = None, success: bool = True, 
                   error_message: Optional[str] = None):
    """Log an audit entry"""
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO water_infrastructure.audit_logs 
                (user_id, action, entity_type, entity_id, old_values, new_values, 
                 ip_address, success, error_message)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, user_id, action, entity_type, entity_id, 
                old_values, new_values, ip_address, success, error_message)
    except Exception as e:
        logger.error(f"Failed to log audit: {e}")

# Authentication endpoints
@router.post("/auth/login")
async def login(
    credentials: UserLogin,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """User login endpoint"""
    async with pool.acquire() as conn:
        # Get user by email
        user = await conn.fetchrow("""
            SELECT id, email, name, password_hash, role, status, failed_login_attempts, locked_until
            FROM water_infrastructure.users
            WHERE email = $1
        """, credentials.email)
        
        if not user:
            await log_audit(pool, None, "Login Failed - User Not Found", 
                          ip_address=request.client.host, success=False)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if account is locked
        if user['locked_until'] and user['locked_until'] > datetime.now(timezone.utc):
            await log_audit(pool, user['id'], "Login Failed - Account Locked", 
                          ip_address=request.client.host, success=False)
            raise HTTPException(status_code=401, detail="Account is locked")
        
        # Check if account is active
        if user['status'] != 'active':
            await log_audit(pool, user['id'], "Login Failed - Account Inactive", 
                          ip_address=request.client.host, success=False)
            raise HTTPException(status_code=401, detail="Account is not active")
        
        # Verify password
        if not verify_password(credentials.password, user['password_hash']):
            # Increment failed attempts
            failed_attempts = user['failed_login_attempts'] + 1
            locked_until = None
            
            # Lock account after 5 failed attempts
            if failed_attempts >= 5:
                locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            
            await conn.execute("""
                UPDATE water_infrastructure.users 
                SET failed_login_attempts = $1, locked_until = $2
                WHERE id = $3
            """, failed_attempts, locked_until, user['id'])
            
            await log_audit(pool, user['id'], "Login Failed - Invalid Password", 
                          ip_address=request.client.host, success=False)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Login successful - reset failed attempts and update last login
        await conn.execute("""
            UPDATE water_infrastructure.users 
            SET failed_login_attempts = 0, locked_until = NULL, last_login = $1
            WHERE id = $2
        """, datetime.now(timezone.utc), user['id'])
        
        # Create session
        token = generate_token()
        token_hash = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
        
        await conn.execute("""
            INSERT INTO water_infrastructure.user_sessions 
            (user_id, token_hash, expires_at, ip_address, user_agent)
            VALUES ($1, $2, $3, $4, $5)
        """, user['id'], token_hash, expires_at, request.client.host, 
            request.headers.get('user-agent'))
        
        # Get permissions
        permissions = await conn.fetch("""
            SELECT permission FROM water_infrastructure.user_permissions
            WHERE user_id = $1
        """, user['id'])
        
        await log_audit(pool, user['id'], "User Login", 
                       ip_address=request.client.host, success=True)
        
        return {
            "token": token,
            "user": {
                "id": str(user['id']),
                "email": user['email'],
                "name": user['name'],
                "role": user['role'],
                "permissions": [p['permission'] for p in permissions]
            }
        }

# User management endpoints
@router.get("/users")
async def get_users(
    pool: asyncpg.Pool = Depends(get_db_pool),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get list of users"""
    query = """
        SELECT id, email, name, role, department, phone, location, 
               status, last_login, created_at
        FROM water_infrastructure.users
        WHERE 1=1
    """
    params = []
    param_count = 0
    
    if role:
        param_count += 1
        query += f" AND role = ${param_count}"
        params.append(role)
    
    if status:
        param_count += 1
        query += f" AND status = ${param_count}"
        params.append(status)
    
    query += f" ORDER BY created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
    params.extend([limit, offset])
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        
        users = []
        for row in rows:
            user_dict = dict(row)
            user_dict['id'] = str(user_dict['id'])
            users.append(user_dict)
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM water_infrastructure.users WHERE 1=1"
        if role:
            count_query += f" AND role = '{role}'"
        if status:
            count_query += f" AND status = '{status}'"
        
        total = await conn.fetchval(count_query)
        
        return {
            "users": users,
            "total": total,
            "limit": limit,
            "offset": offset
        }

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Get user details"""
    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT id, email, name, role, department, phone, location, bio,
                   status, two_factor_enabled, last_login, created_at
            FROM water_infrastructure.users
            WHERE id = $1
        """, uuid.UUID(user_id))
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get permissions
        permissions = await conn.fetch("""
            SELECT permission FROM water_infrastructure.user_permissions
            WHERE user_id = $1
        """, uuid.UUID(user_id))
        
        user_dict = dict(user)
        user_dict['id'] = str(user_dict['id'])
        user_dict['permissions'] = [p['permission'] for p in permissions]
        
        return user_dict

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Create a new user"""
    async with pool.acquire() as conn:
        # Check if email already exists
        exists = await conn.fetchval("""
            SELECT EXISTS(SELECT 1 FROM water_infrastructure.users WHERE email = $1)
        """, user_data.email)
        
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        try:
            # Create user
            user_id = await conn.fetchval("""
                INSERT INTO water_infrastructure.users 
                (email, name, password_hash, role, department, phone, location, bio)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, user_data.email, user_data.name, password_hash, user_data.role,
                user_data.department, user_data.phone, user_data.location, user_data.bio)
            
            # Create default settings
            await conn.execute("""
                INSERT INTO water_infrastructure.user_settings (user_id)
                VALUES ($1)
            """, user_id)
            
            # Grant default permissions based on role
            default_permissions = {
                'viewer': ['view_dashboard'],
                'operator': ['view_dashboard', 'control_pumps'],
                'engineer': ['view_dashboard', 'manage_sensors', 'generate_reports'],
                'admin': ['view_dashboard', 'manage_sensors', 'generate_reports', 'control_pumps'],
                'super_admin': ['view_dashboard', 'manage_sensors', 'generate_reports', 
                               'control_pumps', 'manage_users', 'manage_settings', 
                               'view_audit_logs', 'manage_backups']
            }
            
            permissions = default_permissions.get(user_data.role, ['view_dashboard'])
            for permission in permissions:
                await conn.execute("""
                    INSERT INTO water_infrastructure.user_permissions (user_id, permission)
                    VALUES ($1, $2)
                """, user_id, permission)
            
            await log_audit(pool, None, "User Created", "user", str(user_id),
                          new_values={"email": user_data.email, "role": user_data.role},
                          ip_address=request.client.host)
            
            return {"id": str(user_id), "email": user_data.email, "name": user_data.name}
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(status_code=500, detail="Failed to create user")

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Update user details"""
    async with pool.acquire() as conn:
        # Get current user data
        current_user = await conn.fetchrow("""
            SELECT * FROM water_infrastructure.users WHERE id = $1
        """, uuid.UUID(user_id))
        
        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build update query
        updates = []
        params = []
        param_count = 0
        
        update_dict = user_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                param_count += 1
                updates.append(f"{field} = ${param_count}")
                params.append(value)
        
        if not updates:
            return {"message": "No updates provided"}
        
        param_count += 1
        params.append(uuid.UUID(user_id))
        
        query = f"""
            UPDATE water_infrastructure.users 
            SET {', '.join(updates)}
            WHERE id = ${param_count}
        """
        
        await conn.execute(query, *params)
        
        await log_audit(pool, user_id, "User Updated", "user", user_id,
                       old_values={k: current_user[k] for k in update_dict.keys()},
                       new_values=update_dict,
                       ip_address=request.client.host)
        
        return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Delete a user"""
    async with pool.acquire() as conn:
        # Check if user exists
        exists = await conn.fetchval("""
            SELECT EXISTS(SELECT 1 FROM water_infrastructure.users WHERE id = $1)
        """, uuid.UUID(user_id))
        
        if not exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Soft delete - just change status
        await conn.execute("""
            UPDATE water_infrastructure.users 
            SET status = 'suspended'
            WHERE id = $1
        """, uuid.UUID(user_id))
        
        await log_audit(pool, user_id, "User Deleted", "user", user_id,
                       ip_address=request.client.host)
        
        return {"message": "User deleted successfully"}

# Settings endpoints
@router.get("/users/{user_id}/settings")
async def get_user_settings(
    user_id: str,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Get user settings"""
    async with pool.acquire() as conn:
        settings = await conn.fetchrow("""
            SELECT * FROM water_infrastructure.user_settings
            WHERE user_id = $1
        """, uuid.UUID(user_id))
        
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        settings_dict = dict(settings)
        settings_dict['id'] = str(settings_dict['id'])
        settings_dict['user_id'] = str(settings_dict['user_id'])
        
        return settings_dict

@router.put("/users/{user_id}/settings")
async def update_user_settings(
    user_id: str,
    settings_data: UserSettings,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Update user settings"""
    async with pool.acquire() as conn:
        # Check if settings exist
        exists = await conn.fetchval("""
            SELECT EXISTS(SELECT 1 FROM water_infrastructure.user_settings WHERE user_id = $1)
        """, uuid.UUID(user_id))
        
        if not exists:
            # Create settings if they don't exist
            await conn.execute("""
                INSERT INTO water_infrastructure.user_settings (user_id)
                VALUES ($1)
            """, uuid.UUID(user_id))
        
        # Build update query
        updates = []
        params = []
        param_count = 0
        
        update_dict = settings_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                param_count += 1
                updates.append(f"{field} = ${param_count}")
                params.append(value)
        
        if updates:
            param_count += 1
            params.append(uuid.UUID(user_id))
            
            query = f"""
                UPDATE water_infrastructure.user_settings 
                SET {', '.join(updates)}
                WHERE user_id = ${param_count}
            """
            
            await conn.execute(query, *params)
        
        await log_audit(pool, user_id, "Settings Updated", "user_settings", user_id,
                       new_values=update_dict,
                       ip_address=request.client.host)
        
        return {"message": "Settings updated successfully"}

# Audit log endpoints
@router.get("/audit-logs")
async def get_audit_logs(
    pool: asyncpg.Pool = Depends(get_db_pool),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get audit logs"""
    query = """
        SELECT l.*, u.name as user_name, u.email as user_email_address
        FROM water_infrastructure.audit_logs l
        LEFT JOIN water_infrastructure.users u ON l.user_id = u.id
        WHERE 1=1
    """
    params = []
    param_count = 0
    
    if user_id:
        param_count += 1
        query += f" AND l.user_id = ${param_count}"
        params.append(uuid.UUID(user_id))
    
    if action:
        param_count += 1
        query += f" AND l.action = ${param_count}"
        params.append(action)
    
    if start_date:
        param_count += 1
        query += f" AND l.created_at >= ${param_count}"
        params.append(start_date)
    
    if end_date:
        param_count += 1
        query += f" AND l.created_at <= ${param_count}"
        params.append(end_date)
    
    query += f" ORDER BY l.created_at DESC LIMIT ${param_count + 1} OFFSET ${param_count + 2}"
    params.extend([limit, offset])
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)
        
        logs = []
        for row in rows:
            log_dict = dict(row)
            if log_dict['id']:
                log_dict['id'] = str(log_dict['id'])
            if log_dict['user_id']:
                log_dict['user_id'] = str(log_dict['user_id'])
            logs.append(log_dict)
        
        return {
            "logs": logs,
            "limit": limit,
            "offset": offset
        }

# System configuration endpoints
@router.get("/system-config")
async def get_system_config(
    pool: asyncpg.Pool = Depends(get_db_pool),
    category: Optional[str] = Query(None)
):
    """Get system configuration"""
    query = """
        SELECT config_key, config_value, description, category
        FROM water_infrastructure.system_config
        WHERE is_sensitive = FALSE
    """
    
    if category:
        query += f" AND category = '{category}'"
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        
        config = {}
        for row in rows:
            config[row['config_key']] = {
                "value": row['config_value'],
                "description": row['description'],
                "category": row['category']
            }
        
        return config

@router.put("/system-config/{config_key}")
async def update_system_config(
    config_key: str,
    config_data: SystemConfig,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Update system configuration"""
    async with pool.acquire() as conn:
        # Get current value
        current = await conn.fetchrow("""
            SELECT config_value FROM water_infrastructure.system_config
            WHERE config_key = $1
        """, config_key)
        
        if not current:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Update config
        await conn.execute("""
            UPDATE water_infrastructure.system_config
            SET config_value = $1, description = $2, updated_at = $3
            WHERE config_key = $4
        """, config_data.config_value, config_data.description, 
            datetime.now(timezone.utc), config_key)
        
        await log_audit(pool, None, "System Config Updated", "system_config", config_key,
                       old_values={"value": current['config_value']},
                       new_values={"value": config_data.config_value},
                       ip_address=request.client.host)
        
        return {"message": "Configuration updated successfully"}

# User profile endpoints (for current user)
@router.get("/profile")
async def get_current_user_profile(
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Get current user profile (mock for demo)"""
    # In production, this would get the user from the session token
    # For demo, return Giovanni Rossi
    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT id, email, name, role, department, phone, location, bio,
                   status, two_factor_enabled, last_login, created_at
            FROM water_infrastructure.users
            WHERE email = 'giovanni.rossi@abbanoa.it'
        """)
        
        if user:
            permissions = await conn.fetch("""
                SELECT permission FROM water_infrastructure.user_permissions
                WHERE user_id = $1
            """, user['id'])
            
            user_dict = dict(user)
            user_dict['id'] = str(user_dict['id'])
            user_dict['permissions'] = [p['permission'] for p in permissions]
            
            return user_dict
        
        # Fallback
        return {
            "id": "demo-user",
            "email": "giovanni.rossi@abbanoa.it",
            "name": "Giovanni Rossi",
            "role": "admin",
            "permissions": ["view_dashboard", "manage_sensors", "generate_reports", "control_pumps"]
        }

@router.put("/profile")
async def update_current_user_profile(
    user_data: UserUpdate,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Update current user profile (mock for demo)"""
    # In production, this would update the current user from session
    return {"message": "Profile updated successfully (demo mode)"}

@router.get("/profile/settings")
async def get_current_user_settings(
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Get current user settings (mock for demo)"""
    # In production, this would get settings for the current user
    async with pool.acquire() as conn:
        user = await conn.fetchrow("""
            SELECT id FROM water_infrastructure.users
            WHERE email = 'giovanni.rossi@abbanoa.it'
        """)
        
        if user:
            settings = await conn.fetchrow("""
                SELECT * FROM water_infrastructure.user_settings
                WHERE user_id = $1
            """, user['id'])
            
            if settings:
                settings_dict = dict(settings)
                settings_dict['id'] = str(settings_dict['id'])
                settings_dict['user_id'] = str(settings_dict['user_id'])
                return settings_dict
    
    # Fallback
    return {
        "notifications_email": True,
        "notifications_sms": False,
        "notifications_push": True,
        "theme": "auto",
        "language": "it",
        "date_format": "DD/MM/YYYY",
        "units": "metric",
        "auto_refresh": True,
        "refresh_interval": 30
    }

@router.put("/profile/settings")
async def update_current_user_settings(
    settings_data: UserSettings,
    request: Request,
    pool: asyncpg.Pool = Depends(get_db_pool)
):
    """Update current user settings (mock for demo)"""
    # In production, this would update settings for the current user
    return {"message": "Settings updated successfully (demo mode)"} 