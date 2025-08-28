# 🔐 Mock Authentication Backend

This is a simple Express.js server that provides mock authentication for testing the Abbanoa Dashboard frontend.

## 🚀 Quick Start

```bash
npm install
npm start
```

The server will run on `http://localhost:8001`

## 📋 Test Credentials

| Email | Password | Role | Description |
|-------|----------|------|-------------|
| `admin@abbanoa.com` | `admin123` | `admin` | Full administrative access |
| `operator@abbanoa.com` | `operator123` | `operator` | Water system operator |
| `super@abbanoa.com` | `super123` | `super_admin` | Super administrator |

## 🏢 Organizations

| Name | Domain | Plan | Features |
|------|--------|------|----------|
| Abbanoa S.p.A. | `abbanoa` | Enterprise | All features enabled |
| Test Organization | `test-org` | Professional | Basic features |

## 🛠️ Available Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/register` - Register new user (returns info about test credentials)
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user info

### Tenants
- `GET /api/v1/tenants/current` - Get current tenant
- `GET /api/v1/auth/tenants` - Get available tenants

### Dashboard Data
- `GET /api/v1/dashboard/metrics` - Get system metrics
- `GET /api/v1/monitoring/status` - Get monitoring status
- `GET /api/v1/anomalies` - Get anomaly data

### Validation
- `GET /api/v1/auth/validate-domain` - Check domain availability
- `GET /api/v1/auth/check-email` - Check email existence

## 🧪 Testing the Frontend

1. Make sure this backend is running on port 8001
2. Start the frontend on port 3000
3. Visit `http://localhost:3000`
4. Use any of the test credentials to login
5. Explore the dashboard features

## 🔧 Configuration

- **Port**: 8001 (to avoid conflict with existing backend on 8000)
- **JWT Secret**: `mock-jwt-secret-key-for-testing`
- **Token Expiry**: 24 hours
- **CORS**: Enabled for all origins

---

**Note**: This is a mock server for development/testing only. Do not use in production!
