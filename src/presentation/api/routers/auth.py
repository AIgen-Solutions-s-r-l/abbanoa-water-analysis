
from fastapi import APIRouter
from src.schemas.auth import User, Tenant, LoginResponse, UserTenant
from datetime import datetime

router = APIRouter()

@router.get("/auth/me")
async def get_current_user():
    """Mock endpoint to get current user."""
    return {
        "success": True,
        "data": {
            "id": "user-1",
            "email": "admin@abbanoa.com",
            "firstName": "Admin",
            "lastName": "User",
            "role": "admin",
            "tenantId": "default",
            "isActive": True,
            "lastLogin": datetime.now().isoformat(),
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
    }


@router.get("/tenants/current")
async def get_current_tenant():
    """Mock endpoint to get current tenant."""
    return {
        "success": True,
        "data": {
            "id": "default",
            "name": "Abbanoa S.p.A.",
            "domain": "abbanoa",
            "logo": None,
            "plan": "enterprise",
            "isActive": True,
            "settings": {
                "maxUsers": 100,
                "features": ["monitoring", "anomaly_detection", "reporting", "analytics"],
                "customBranding": {
                    "primaryColor": "#2563eb",
                    "logo": "",
                    "companyName": "Abbanoa S.p.A."
                }
            },
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
    }


@router.post("/auth/login")
async def login():
    """Mock login endpoint."""
    return {
        "success": True,
        "data": {
            "user": {
                "id": "user-1",
                "email": "admin@abbanoa.com",
                "firstName": "Admin",
                "lastName": "User",
                "role": "admin",
                "tenantId": "default",
                "isActive": True,
                "lastLogin": datetime.now().isoformat(),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            },
            "tenant": {
                "id": "default",
                "name": "Abbanoa S.p.A.",
                "domain": "abbanoa",
                "logo": None,
                "plan": "enterprise",
                "isActive": True,
                "settings": {
                    "maxUsers": 100,
                    "features": ["monitoring", "anomaly_detection", "reporting", "analytics"],
                    "customBranding": {
                        "primaryColor": "#2563eb",
                        "logo": "",
                        "companyName": "Abbanoa S.p.A."
                    }
                },
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            },
            "accessToken": "mock-access-token",
            "refreshToken": "mock-refresh-token",
            "expiresIn": 86400
        }
    }


@router.get("/auth/tenants")
async def get_user_tenants():
    """Mock endpoint to get user tenants."""
    return {
        "success": True,
        "data": [{
            "id": "default",
            "name": "Abbanoa S.p.A.",
            "domain": "abbanoa",
            "logo": None,
            "plan": "enterprise",
            "isActive": True,
            "userRole": "admin",
            "joinedAt": datetime.now().isoformat()
        }]
    }
