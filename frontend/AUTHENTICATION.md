# Authentication & Multi-Tenancy Implementation

This document outlines the complete authentication and multi-tenancy system implemented in the Abbanoa Dashboard frontend.

## 🔐 **Features Implemented**

### **Authentication**
- ✅ **JWT-based authentication** with automatic token refresh
- ✅ **Login/Register pages** with tenant domain support
- ✅ **Protected routes** with role-based access control
- ✅ **Session management** with automatic persistence
- ✅ **Password reset/change** functionality
- ✅ **User invitation system** support

### **Multi-Tenancy**
- ✅ **Tenant isolation** with automatic tenant context
- ✅ **Tenant switcher** for users belonging to multiple organizations
- ✅ **Organization creation** during registration
- ✅ **Tenant-scoped API requests** with automatic headers
- ✅ **Custom branding** support per tenant

### **User Management**
- ✅ **Role-based permissions** (viewer, operator, admin, super_admin)
- ✅ **User profiles** with editable information
- ✅ **Permission system** with granular access control
- ✅ **User menu** with profile and settings access

## 🏗️ **Architecture Overview**

### **Authentication Flow**
```
1. User visits protected route
2. LayoutWrapper checks authentication status
3. If not authenticated → redirect to /auth/login
4. Login form captures credentials + optional tenant domain
5. AuthService.login() calls backend API
6. Store JWT tokens + tenant info in localStorage
7. Redirect to originally requested route
8. All subsequent API calls include Authorization header
```

### **Multi-Tenant Context**
```
1. Every API request includes X-Tenant-ID header
2. Backend filters all data by tenant
3. Users can switch between tenants (if they have access)
4. Tenant information displayed in header
5. All data operations are tenant-scoped
```

## 📂 **File Structure**

```
src/
├── components/
│   ├── auth/
│   │   └── ProtectedRoute.tsx         # Route protection with role checking
│   ├── providers/
│   │   └── AuthProvider.tsx           # Authentication context provider
│   └── layout/
│       ├── TenantSwitcher.tsx         # Multi-tenant navigation
│       ├── Header.tsx                 # User menu & tenant display
│       └── LayoutWrapper.tsx          # Layout routing logic
├── lib/
│   ├── types/
│   │   ├── auth.ts                    # Authentication type definitions
│   │   └── index.ts                   # Combined type exports
│   ├── hooks/
│   │   └── useAuth.ts                 # Authentication state management
│   └── api/
│       └── client.ts                  # API client with auth support
├── services/
│   └── auth.service.ts                # Authentication API calls
└── app/
    └── auth/
        ├── login/page.tsx             # Login page
        └── register/page.tsx          # Registration page
```

## 🔧 **API Integration**

### **Expected Backend Endpoints**

```bash
# Authentication
POST   /api/v1/auth/login              # Login with credentials
POST   /api/v1/auth/register           # Register new user/tenant
POST   /api/v1/auth/logout             # Logout user
POST   /api/v1/auth/refresh            # Refresh JWT token
POST   /api/v1/auth/reset-password     # Request password reset
PUT    /api/v1/auth/change-password    # Change password
GET    /api/v1/auth/me                 # Get current user info

# Tenant Management
GET    /api/v1/tenants/current         # Get current tenant info
GET    /api/v1/auth/tenants            # Get user's available tenants
POST   /api/v1/auth/switch-tenant      # Switch active tenant
POST   /api/v1/tenants                 # Create new tenant

# User Management
PUT    /api/v1/auth/profile            # Update user profile
POST   /api/v1/auth/invite             # Invite new user
POST   /api/v1/auth/accept-invitation  # Accept invitation

# Validation
GET    /api/v1/auth/validate-domain    # Check domain availability
GET    /api/v1/auth/check-email        # Check email existence
```

### **Request Headers**
```bash
Authorization: Bearer <jwt_token>      # All authenticated requests
X-Tenant-ID: <tenant_id>              # All tenant-scoped requests
Content-Type: application/json        # All requests
```

### **Response Format**
```typescript
interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
  metadata?: {
    total?: number;
    page?: number;
    limit?: number;
    tenantId?: string;
  };
}
```

## 🎯 **Usage Examples**

### **Protecting Routes**
```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Basic protection (any authenticated user)
<ProtectedRoute>
  <DashboardContent />
</ProtectedRoute>

// Role-based protection
<ProtectedRoute requiredRole="admin">
  <AdminPanel />
</ProtectedRoute>

// Permission-based protection
<ProtectedRoute requiredPermissions={[{resource: 'users', action: 'manage'}]}>
  <UserManagement />
</ProtectedRoute>
```

### **Using Authentication Context**
```tsx
import { useAuthContext } from '@/components/providers/AuthProvider';

function MyComponent() {
  const { 
    user, 
    tenant, 
    isAuthenticated, 
    login, 
    logout, 
    switchTenant 
  } = useAuthContext();

  // Use authentication state and methods
}
```

### **Permission Checking**
```tsx
import { usePermissions } from '@/components/auth/ProtectedRoute';

function MyComponent() {
  const { hasRole, hasPermission, canAccess } = usePermissions();

  if (hasRole('admin')) {
    // Show admin features
  }

  if (hasPermission('users', 'create')) {
    // Show create user button
  }
}
```

## 🔒 **Security Features**

### **Token Management**
- **Automatic refresh**: Tokens are refreshed automatically before expiration
- **Secure storage**: Tokens stored in localStorage (consider httpOnly cookies for production)
- **Token validation**: Invalid tokens trigger automatic logout
- **CSRF protection**: API client handles CSRF tokens if needed

### **Route Protection**
- **Authentication guards**: All routes check authentication status
- **Role-based access**: Different user roles have different access levels
- **Permission system**: Granular permissions for specific actions
- **Tenant isolation**: All data operations are tenant-scoped

### **Input Validation**
- **Email validation**: Email format validation on frontend
- **Password requirements**: Can be enforced in forms
- **Domain validation**: Tenant domain format validation
- **Form sanitization**: All inputs are validated before submission

## 🎨 **User Experience**

### **Login Flow**
1. **Tenant Domain (Optional)**: Users can specify organization domain
2. **Email & Password**: Standard credential input
3. **Remember Me**: Session persistence options
4. **Forgot Password**: Password reset functionality
5. **Create Account**: Link to registration

### **Registration Flow**
1. **Organization Creation**: Option to create new organization
2. **Personal Information**: Name and contact details
3. **Credentials**: Email and password setup
4. **Tenant Setup**: Organization name and domain
5. **Immediate Access**: Automatic login after registration

### **Tenant Management**
1. **Current Tenant**: Display current organization context
2. **Tenant Switcher**: Easy switching between organizations
3. **Organization Settings**: Access to tenant configuration
4. **Create Organization**: Ability to create new organizations

## 🔄 **State Management**

### **Authentication State**
```typescript
interface AuthState {
  user: User | null;              // Current user information
  tenant: Tenant | null;          // Current tenant context
  accessToken: string | null;     // JWT access token
  refreshToken: string | null;    // JWT refresh token
  isAuthenticated: boolean;       // Authentication status
  isLoading: boolean;            // Loading state
  error: string | null;          // Error messages
}
```

### **Automatic State Persistence**
- Authentication state persists across browser sessions
- Tenant context is maintained during navigation
- Token refresh happens automatically in background
- Invalid tokens trigger graceful logout

## 🚀 **Production Considerations**

### **Security Enhancements**
- [ ] **httpOnly Cookies**: Move token storage to secure cookies
- [ ] **CSRF Protection**: Implement CSRF token validation
- [ ] **Rate Limiting**: Add login attempt rate limiting
- [ ] **Session Timeout**: Implement automatic session timeout
- [ ] **2FA Support**: Add two-factor authentication

### **Performance Optimizations**
- [ ] **Token Caching**: Optimize token refresh logic
- [ ] **Lazy Loading**: Load auth components on demand
- [ ] **Memory Management**: Clean up auth subscriptions
- [ ] **Offline Support**: Handle offline authentication scenarios

### **Monitoring & Analytics**
- [ ] **Login Tracking**: Track successful/failed login attempts
- [ ] **Session Analytics**: Monitor session duration and patterns
- [ ] **Error Logging**: Log authentication errors for debugging
- [ ] **Performance Metrics**: Track auth-related performance

## 🧪 **Testing Strategy**

### **Unit Tests** (To Implement)
- [ ] Authentication hook tests
- [ ] API service tests
- [ ] Permission utility tests
- [ ] Form validation tests

### **Integration Tests** (To Implement)
- [ ] Login/logout flow tests
- [ ] Protected route tests
- [ ] Tenant switching tests
- [ ] Token refresh tests

### **E2E Tests** (To Implement)
- [ ] Complete authentication workflows
- [ ] Multi-tenant scenarios
- [ ] Error handling scenarios
- [ ] Cross-browser compatibility

## 📝 **Configuration**

### **Environment Variables**
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000    # Backend API URL
NEXT_PUBLIC_API_VERSION=v1                        # API version
NEXT_PUBLIC_APP_NAME=Abbanoa Dashboard           # Application name
```

### **Backend Requirements**
- JWT token-based authentication
- Multi-tenant data isolation
- CORS configuration for frontend domain
- User role and permission management
- Tenant domain validation

## 🤝 **Integration Checklist**

### **Backend Integration**
- [ ] Implement authentication endpoints
- [ ] Set up JWT token generation/validation
- [ ] Configure multi-tenant data isolation
- [ ] Implement user role management
- [ ] Set up CORS for frontend domain

### **Frontend Deployment**
- [ ] Configure environment variables
- [ ] Set up domain for frontend
- [ ] Configure CDN/hosting
- [ ] Set up monitoring and logging
- [ ] Test authentication flows

This authentication system provides a solid foundation for a secure, multi-tenant web application with comprehensive user management and role-based access control. 