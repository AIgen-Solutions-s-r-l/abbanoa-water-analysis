
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class User(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    role: str
    tenantId: str
    isActive: bool
    lastLogin: str
    createdAt: str
    updatedAt: str

class CustomBranding(BaseModel):
    primaryColor: str
    logo: str
    companyName: str

class TenantSettings(BaseModel):
    maxUsers: int
    features: List[str]
    customBranding: CustomBranding

class Tenant(BaseModel):
    id: str
    name: str
    domain: str
    logo: Optional[str] = None
    plan: str
    isActive: bool
    settings: TenantSettings
    createdAt: str
    updatedAt: str

class LoginResponse(BaseModel):
    user: User
    tenant: Tenant
    accessToken: str
    refreshToken: str
    expiresIn: int

class UserTenant(BaseModel):
    id: str
    name: str
    domain: str
    logo: Optional[str] = None
    plan: str
    isActive: bool
    userRole: str
    joinedAt: str
