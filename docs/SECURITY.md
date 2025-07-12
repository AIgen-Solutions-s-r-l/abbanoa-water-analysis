# Security Guide

This document outlines security practices, configurations, and procedures for the Abbanoa Water Infrastructure Analytics Platform.

## Security Overview

The platform implements defense-in-depth security with multiple layers:

- **Application Security**: JWT authentication, input validation, secure coding practices
- **Infrastructure Security**: Network isolation, encrypted communications, access controls
- **Data Security**: Encryption at rest and in transit, data anonymization, audit logging
- **Operational Security**: Monitoring, incident response, security updates

## Authentication & Authorization

### JWT Authentication

The platform uses JSON Web Tokens (JWT) for stateless authentication:

```python
# JWT Configuration
JWT_SECRET_KEY = "your-secret-key-here"  # Use strong random key
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME = 3600  # 1 hour
JWT_REFRESH_EXPIRATION = 86400  # 24 hours
```

**Best Practices**:
- Use cryptographically secure random keys (minimum 256 bits)
- Rotate JWT secrets regularly (monthly)
- Implement token refresh mechanism
- Set appropriate expiration times

### Role-Based Access Control (RBAC)

User roles and permissions:

```python
# User Roles
ROLES = {
    "admin": {
        "permissions": ["read", "write", "delete", "admin"],
        "description": "Full system access"
    },
    "operator": {
        "permissions": ["read", "write"],
        "description": "Operational access to data and dashboards"
    },
    "analyst": {
        "permissions": ["read"],
        "description": "Read-only access for analysis"
    },
    "viewer": {
        "permissions": ["read_dashboard"],
        "description": "Dashboard viewing only"
    }
}
```

### API Key Management

For service-to-service authentication:

```bash
# Generate API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Store in environment
export API_KEY="your-generated-api-key"
```

**Best Practices**:
- Generate unique API keys per service
- Rotate API keys quarterly
- Monitor API key usage
- Revoke unused or compromised keys

## Data Security

### Encryption at Rest

**Database Encryption**:
```sql
-- PostgreSQL encryption
CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(10),
    encrypted_data BYTEA,  -- Store sensitive data encrypted
    created_at TIMESTAMP DEFAULT NOW()
);
```

**File Encryption**:
```bash
# Encrypt sensitive configuration files
gpg --symmetric --cipher-algo AES256 config/production.env
```

### Encryption in Transit

**HTTPS Configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.curator.aigensolutions.it;
    
    ssl_certificate /etc/ssl/certs/domain.crt;
    ssl_certificate_key /etc/ssl/private/domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

**Database TLS**:
```python
# PostgreSQL connection with TLS
DATABASE_URL = "postgresql://user:pass@host:5432/db?sslmode=require"
```

### Data Anonymization

For analytics and non-production environments:

```python
def anonymize_sensor_data(df):
    """Anonymize sensitive data for analytics."""
    # Hash node IDs
    df['node_id'] = df['node_id'].apply(
        lambda x: hashlib.sha256(x.encode()).hexdigest()[:8]
    )
    
    # Add noise to precise location data
    df['latitude'] += np.random.normal(0, 0.001, len(df))
    df['longitude'] += np.random.normal(0, 0.001, len(df))
    
    return df
```

## Network Security

### Firewall Configuration

**iptables rules**:
```bash
# Allow essential services only
iptables -A INPUT -p tcp --dport 22 -j ACCEPT    # SSH
iptables -A INPUT -p tcp --dport 80 -j ACCEPT    # HTTP
iptables -A INPUT -p tcp --dport 443 -j ACCEPT   # HTTPS
iptables -A INPUT -p tcp --dport 8000 -j ACCEPT  # API (internal)
iptables -A INPUT -j DROP  # Drop all other traffic
```

**Docker network isolation**:
```yaml
# docker-compose.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

services:
  dashboard:
    networks:
      - frontend
  api:
    networks:
      - frontend
      - backend
  database:
    networks:
      - backend  # Only internal access
```

### VPN and Private Networks

For production deployments:

```bash
# Configure private network access
# Use Google Cloud VPN or similar for secure access
gcloud compute vpn-tunnels create abbanoa-tunnel \
  --peer-address=YOUR_OFFICE_IP \
  --shared-secret=YOUR_SHARED_SECRET \
  --target-vpn-gateway=abbanoa-gateway
```

## Input Validation & Sanitization

### API Input Validation

```python
from pydantic import BaseModel, validator
from typing import List, Optional

class SensorReadingRequest(BaseModel):
    node_id: str
    timestamp: datetime
    flow_rate: float
    pressure: float
    temperature: float
    
    @validator('node_id')
    def validate_node_id(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Node ID must be 6 digits')
        return v
    
    @validator('flow_rate', 'pressure', 'temperature')
    def validate_measurements(cls, v):
        if v < 0 or v > 1000:  # Reasonable bounds
            raise ValueError('Measurement out of valid range')
        return v
```

### SQL Injection Prevention

**Use parameterized queries**:
```python
# Good - Parameterized query
cursor.execute(
    "SELECT * FROM sensor_readings WHERE node_id = %s AND timestamp > %s",
    (node_id, start_time)
)

# Bad - String formatting (vulnerable)
cursor.execute(
    f"SELECT * FROM sensor_readings WHERE node_id = '{node_id}'"
)
```

### Cross-Site Scripting (XSS) Prevention

For dashboard components:
```python
import html

def safe_display_value(value):
    """Escape HTML to prevent XSS."""
    return html.escape(str(value))

# In Streamlit
st.write(safe_display_value(user_input))
```

## Audit Logging

### Security Event Logging

```python
import structlog

security_logger = structlog.get_logger("security")

def log_authentication_event(user_id, event_type, success, ip_address):
    """Log authentication events for security monitoring."""
    security_logger.info(
        "authentication_event",
        user_id=user_id,
        event_type=event_type,  # login, logout, token_refresh
        success=success,
        ip_address=ip_address,
        timestamp=datetime.utcnow(),
        service="api"
    )

def log_data_access_event(user_id, resource, action, ip_address):
    """Log data access for compliance."""
    security_logger.info(
        "data_access_event",
        user_id=user_id,
        resource=resource,
        action=action,  # read, write, delete
        ip_address=ip_address,
        timestamp=datetime.utcnow()
    )
```

### Log Monitoring

Monitor security logs for suspicious activity:

```bash
# Monitor failed login attempts
grep "authentication_event.*success.*false" /var/log/abbanoa/security.log

# Monitor unusual data access patterns
grep "data_access_event" /var/log/abbanoa/security.log | \
  awk '{print $5}' | sort | uniq -c | sort -nr
```

## Vulnerability Management

### Security Scanning

**Dependency scanning**:
```bash
# Check for known vulnerabilities
safety check
pip-audit

# Update vulnerable packages
poetry update
```

**Static code analysis**:
```bash
# Security-focused linting
bandit -r src/
semgrep --config=auto src/
```

**Container scanning**:
```bash
# Scan Docker images
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image abbanoa/dashboard:latest
```

### Security Updates

**Automated updates**:
```bash
# Set up automated security updates
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades
systemctl enable unattended-upgrades
```

**Manual update process**:
```bash
# Update base system
apt update && apt upgrade -y

# Update Python dependencies
poetry update

# Rebuild containers with latest base images
docker-compose build --pull --no-cache
```

## Secrets Management

### Environment Variables

```bash
# Store secrets in environment variables
export BIGQUERY_PRIVATE_KEY="$(cat /path/to/private-key.json)"
export DATABASE_PASSWORD="$(openssl rand -base64 32)"
export JWT_SECRET_KEY="$(openssl rand -base64 64)"
```

### Secret Rotation

**Database credentials**:
```bash
#!/bin/bash
# rotate_db_password.sh

NEW_PASSWORD=$(openssl rand -base64 32)
OLD_PASSWORD=$DATABASE_PASSWORD

# Update database
psql -c "ALTER USER abbanoa_user PASSWORD '$NEW_PASSWORD';"

# Update environment
export DATABASE_PASSWORD=$NEW_PASSWORD

# Restart services
docker-compose restart api processing
```

### Key Management

**Google Cloud KMS integration**:
```python
from google.cloud import kms

def encrypt_sensitive_data(data, key_name):
    """Encrypt data using Google Cloud KMS."""
    client = kms.KeyManagementServiceClient()
    
    response = client.encrypt(
        request={
            "name": key_name,
            "plaintext": data.encode("utf-8")
        }
    )
    
    return response.ciphertext
```

## Security Monitoring

### Intrusion Detection

**Log analysis**:
```bash
# Monitor for brute force attacks
tail -f /var/log/nginx/access.log | \
  grep -E "POST /auth/token.*401|403" | \
  awk '{print $1}' | sort | uniq -c | sort -nr
```

**Automated alerting**:
```python
def check_security_alerts():
    """Check for security events requiring immediate attention."""
    
    # Check for multiple failed logins
    failed_logins = count_failed_logins_last_hour()
    if failed_logins > 10:
        send_security_alert("Multiple failed login attempts detected")
    
    # Check for unusual data access patterns
    unusual_access = detect_unusual_access_patterns()
    if unusual_access:
        send_security_alert("Unusual data access pattern detected")
    
    # Check for resource exhaustion attacks
    if check_resource_usage() > 90:
        send_security_alert("High resource usage - possible DoS attack")
```

### Security Metrics

Track security-related metrics:

```python
SECURITY_METRICS = {
    "failed_login_attempts": 0,
    "successful_logins": 0,
    "api_requests_blocked": 0,
    "data_access_violations": 0,
    "security_scan_alerts": 0
}
```

## Incident Response

### Security Incident Procedure

1. **Detection**: Automated monitoring or manual discovery
2. **Analysis**: Assess scope and impact
3. **Containment**: Isolate affected systems
4. **Eradication**: Remove threat and vulnerabilities
5. **Recovery**: Restore normal operations
6. **Lessons Learned**: Document and improve

### Emergency Response

**Immediate response commands**:
```bash
# Isolate compromised service
docker-compose stop [service_name]

# Block suspicious IP
iptables -I INPUT -s [suspicious_ip] -j DROP

# Rotate all authentication tokens
python scripts/emergency_token_rotation.py

# Enable additional logging
export LOG_LEVEL=DEBUG
docker-compose restart api
```

### Security Contacts

- **Security Team**: security@abbanoa.it
- **Emergency Response**: +39 xxx xxx xxxx (24/7)
- **Google Cloud Security**: [Support Console](https://cloud.google.com/support)

## Compliance & Regulations

### GDPR Compliance

**Data protection measures**:
- Data minimization (collect only necessary data)
- Purpose limitation (use data only for stated purposes)
- Storage limitation (retain data only as long as necessary)
- Accuracy (keep data accurate and up to date)
- Security (implement appropriate technical measures)

**User rights implementation**:
```python
def handle_data_subject_request(user_id, request_type):
    """Handle GDPR data subject requests."""
    
    if request_type == "access":
        return export_user_data(user_id)
    elif request_type == "rectification":
        return update_user_data(user_id)
    elif request_type == "erasure":
        return delete_user_data(user_id)
    elif request_type == "portability":
        return export_user_data_portable(user_id)
```

### Industry Standards

**ISO 27001 alignment**:
- Information security management system
- Risk assessment and treatment
- Regular security reviews and audits
- Continuous improvement process

## Security Checklist

### Development Security

- [ ] Input validation on all user inputs
- [ ] Parameterized database queries
- [ ] Security headers in HTTP responses
- [ ] Secure session management
- [ ] Error handling doesn't leak information
- [ ] Security testing in CI/CD pipeline

### Infrastructure Security

- [ ] Network segmentation implemented
- [ ] Firewall rules configured
- [ ] TLS/SSL certificates valid and up to date
- [ ] Operating system patches current
- [ ] Container images scanned for vulnerabilities
- [ ] Backup encryption enabled

### Operational Security

- [ ] Security monitoring active
- [ ] Incident response plan documented
- [ ] Staff security training completed
- [ ] Access reviews conducted quarterly
- [ ] Security metrics tracked and reported
- [ ] Vulnerability scanning automated

---

*This security guide should be reviewed quarterly and updated as threats evolve. Last updated: July 2025*