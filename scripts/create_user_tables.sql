-- User Management and Settings Database Schema
-- For Abbanoa Water Infrastructure System

-- Create users table
CREATE TABLE IF NOT EXISTS water_infrastructure.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('super_admin', 'admin', 'engineer', 'operator', 'viewer')),
    department VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    bio TEXT,
    avatar_url VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    last_login TIMESTAMP WITH TIME ZONE,
    last_password_change TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES water_infrastructure.users(id),
    updated_by UUID REFERENCES water_infrastructure.users(id)
);

-- Create user permissions table
CREATE TABLE IF NOT EXISTS water_infrastructure.user_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES water_infrastructure.users(id) ON DELETE CASCADE,
    permission VARCHAR(100) NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by UUID REFERENCES water_infrastructure.users(id),
    UNIQUE(user_id, permission)
);

-- Create user settings table
CREATE TABLE IF NOT EXISTS water_infrastructure.user_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES water_infrastructure.users(id) ON DELETE CASCADE,
    -- Notification settings
    notifications_email BOOLEAN DEFAULT TRUE,
    notifications_sms BOOLEAN DEFAULT FALSE,
    notifications_push BOOLEAN DEFAULT TRUE,
    alert_types_leaks BOOLEAN DEFAULT TRUE,
    alert_types_pressure BOOLEAN DEFAULT TRUE,
    alert_types_quality BOOLEAN DEFAULT TRUE,
    alert_types_maintenance BOOLEAN DEFAULT FALSE,
    -- Display settings
    theme VARCHAR(20) DEFAULT 'auto' CHECK (theme IN ('light', 'dark', 'auto')),
    language VARCHAR(10) DEFAULT 'it' CHECK (language IN ('it', 'en', 'es', 'fr')),
    date_format VARCHAR(20) DEFAULT 'DD/MM/YYYY',
    units VARCHAR(20) DEFAULT 'metric' CHECK (units IN ('metric', 'imperial')),
    -- System settings
    auto_refresh BOOLEAN DEFAULT TRUE,
    refresh_interval INTEGER DEFAULT 30 CHECK (refresh_interval >= 10 AND refresh_interval <= 300),
    data_retention_days INTEGER DEFAULT 90,
    debug_mode BOOLEAN DEFAULT FALSE,
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create audit logs table
CREATE TABLE IF NOT EXISTS water_infrastructure.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES water_infrastructure.users(id),
    user_email VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create system configuration table
CREATE TABLE IF NOT EXISTS water_infrastructure.system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_key VARCHAR(255) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(100),
    is_sensitive BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES water_infrastructure.users(id)
);

-- Create sessions table for authentication
CREATE TABLE IF NOT EXISTS water_infrastructure.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES water_infrastructure.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create API keys table
CREATE TABLE IF NOT EXISTS water_infrastructure.api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES water_infrastructure.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    permissions JSONB DEFAULT '[]'::jsonb,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES water_infrastructure.users(id)
);

-- Create backup history table
CREATE TABLE IF NOT EXISTS water_infrastructure.backup_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_name VARCHAR(255) NOT NULL,
    backup_type VARCHAR(50) NOT NULL CHECK (backup_type IN ('full', 'incremental', 'differential')),
    backup_size BIGINT,
    backup_path TEXT,
    includes_database BOOLEAN DEFAULT TRUE,
    includes_config BOOLEAN DEFAULT TRUE,
    includes_sensor_data BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_by UUID REFERENCES water_infrastructure.users(id)
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON water_infrastructure.users(email);
CREATE INDEX idx_users_role ON water_infrastructure.users(role);
CREATE INDEX idx_users_status ON water_infrastructure.users(status);
CREATE INDEX idx_audit_logs_user_id ON water_infrastructure.audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON water_infrastructure.audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON water_infrastructure.audit_logs(action);
CREATE INDEX idx_sessions_token ON water_infrastructure.user_sessions(token_hash);
CREATE INDEX idx_sessions_expires ON water_infrastructure.user_sessions(expires_at);
CREATE INDEX idx_api_keys_hash ON water_infrastructure.api_keys(key_hash);

-- Create update trigger for updated_at timestamps
CREATE OR REPLACE FUNCTION water_infrastructure.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON water_infrastructure.users
    FOR EACH ROW EXECUTE FUNCTION water_infrastructure.update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON water_infrastructure.user_settings
    FOR EACH ROW EXECUTE FUNCTION water_infrastructure.update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON water_infrastructure.system_config
    FOR EACH ROW EXECUTE FUNCTION water_infrastructure.update_updated_at_column();

-- Insert default system configuration
INSERT INTO water_infrastructure.system_config (config_key, config_value, description, category) VALUES
    ('api_rate_limit', '{"requests_per_minute": 100}'::jsonb, 'API rate limiting configuration', 'api'),
    ('api_timeout', '{"seconds": 30}'::jsonb, 'API request timeout', 'api'),
    ('db_connection_pool', '{"size": 20}'::jsonb, 'Database connection pool size', 'database'),
    ('db_query_timeout', '{"milliseconds": 5000}'::jsonb, 'Database query timeout', 'database'),
    ('sensor_polling_interval', '{"seconds": 60}'::jsonb, 'Sensor data polling interval', 'sensors'),
    ('sensor_error_threshold', '{"count": 5}'::jsonb, 'Number of errors before sensor marked as offline', 'sensors'),
    ('sensor_retry_attempts', '{"count": 3}'::jsonb, 'Number of retry attempts for failed sensor reads', 'sensors'),
    ('backup_schedule', '{"daily": "02:00", "weekly": "Sunday 03:00"}'::jsonb, 'Automated backup schedule', 'backup'),
    ('session_timeout', '{"minutes": 30}'::jsonb, 'User session timeout', 'security'),
    ('password_policy', '{"min_length": 8, "require_uppercase": true, "require_lowercase": true, "require_numbers": true, "require_special": true}'::jsonb, 'Password complexity requirements', 'security')
ON CONFLICT (config_key) DO NOTHING;

-- Insert a default admin user (password: Admin123!)
-- Note: In production, change this password immediately
INSERT INTO water_infrastructure.users (
    email, 
    name, 
    password_hash, 
    role, 
    department,
    phone,
    location,
    bio,
    status
) VALUES (
    'admin@roccavina.it',
    'System Administrator',
    -- This is a bcrypt hash of 'Admin123!' - CHANGE IN PRODUCTION
    '$2b$12$LQKVLgb5r.f3YG3Y9XZpCu.Vb7kH.fVxYYqP6Xt9ZMGVpF.hKcQNO',
    'super_admin',
    'IT Department',
    '+39 070 000 0000',
    'Cagliari, Sardinia',
    'System administrator account',
    'active'
) ON CONFLICT (email) DO NOTHING;

-- Grant all permissions to admin user
INSERT INTO water_infrastructure.user_permissions (user_id, permission)
SELECT id, permission
FROM water_infrastructure.users, 
    (VALUES 
        ('view_dashboard'),
        ('manage_sensors'),
        ('generate_reports'),
        ('control_pumps'),
        ('manage_users'),
        ('manage_settings'),
        ('view_audit_logs'),
        ('manage_backups')
    ) AS perms(permission)
WHERE email = 'admin@roccavina.it'
ON CONFLICT (user_id, permission) DO NOTHING;

-- Create default settings for admin user
INSERT INTO water_infrastructure.user_settings (user_id)
SELECT id FROM water_infrastructure.users WHERE email = 'admin@roccavina.it'
ON CONFLICT (user_id) DO NOTHING;

-- Add some sample users for demo
INSERT INTO water_infrastructure.users (email, name, password_hash, role, department, phone, location, bio, status, last_login) VALUES
    ('giovanni.rossi@roccavina.it', 'Giovanni Rossi', '$2b$12$LQKVLgb5r.f3YG3Y9XZpCu.Vb7kH.fVxYYqP6Xt9ZMGVpF.hKcQNO', 'admin', 'Operations & Maintenance', '+39 070 123 4567', 'Cagliari, Sardinia', 'Experienced water infrastructure engineer with over 10 years in the field.', 'active', '2024-01-15 10:30:00+01'),
    ('maria.bianchi@roccavina.it', 'Maria Bianchi', '$2b$12$LQKVLgb5r.f3YG3Y9XZpCu.Vb7kH.fVxYYqP6Xt9ZMGVpF.hKcQNO', 'operator', 'Operations & Maintenance', '+39 070 123 4568', 'Sassari, Sardinia', 'Skilled operator specializing in pump station management.', 'active', '2024-01-15 09:45:00+01'),
    ('luigi.verdi@roccavina.it', 'Luigi Verdi', '$2b$12$LQKVLgb5r.f3YG3Y9XZpCu.Vb7kH.fVxYYqP6Xt9ZMGVpF.hKcQNO', 'engineer', 'Engineering', '+39 070 123 4569', 'Nuoro, Sardinia', 'Water quality specialist focused on treatment optimization.', 'inactive', '2024-01-10 15:20:00+01'),
    ('anna.russo@roccavina.it', 'Anna Russo', '$2b$12$LQKVLgb5r.f3YG3Y9XZpCu.Vb7kH.fVxYYqP6Xt9ZMGVpF.hKcQNO', 'viewer', 'Quality Control', '+39 070 123 4570', 'Oristano, Sardinia', 'Quality assurance analyst monitoring water standards.', 'active', '2024-01-15 11:00:00+01')
ON CONFLICT (email) DO NOTHING;

-- Grant appropriate permissions to sample users
INSERT INTO water_infrastructure.user_permissions (user_id, permission)
SELECT u.id, p.permission
FROM water_infrastructure.users u
CROSS JOIN (
    VALUES 
        ('giovanni.rossi@roccavina.it', 'view_dashboard'),
        ('giovanni.rossi@roccavina.it', 'manage_sensors'),
        ('giovanni.rossi@roccavina.it', 'generate_reports'),
        ('giovanni.rossi@roccavina.it', 'control_pumps'),
        ('maria.bianchi@roccavina.it', 'view_dashboard'),
        ('maria.bianchi@roccavina.it', 'control_pumps'),
        ('luigi.verdi@roccavina.it', 'view_dashboard'),
        ('luigi.verdi@roccavina.it', 'manage_sensors'),
        ('luigi.verdi@roccavina.it', 'generate_reports'),
        ('anna.russo@roccavina.it', 'view_dashboard')
) AS p(email, permission)
WHERE u.email = p.email
ON CONFLICT (user_id, permission) DO NOTHING;

-- Create settings for all sample users
INSERT INTO water_infrastructure.user_settings (user_id)
SELECT id FROM water_infrastructure.users WHERE email IN (
    'giovanni.rossi@roccavina.it',
    'maria.bianchi@roccavina.it', 
    'luigi.verdi@roccavina.it',
    'anna.russo@roccavina.it'
)
ON CONFLICT (user_id) DO NOTHING; 