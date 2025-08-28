const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const app = express();
const PORT = process.env.PORT || 8001;
const JWT_SECRET = 'mock-jwt-secret-key-for-testing';

// Middleware
app.use(cors());
app.use(express.json());

// Mock Database
const mockUsers = [
  {
    id: 'user_1',
    email: 'admin@abbanoa.com',
    password: bcrypt.hashSync('admin123', 10), // Password: admin123
    firstName: 'Admin',
    lastName: 'User',
    role: 'admin',
    tenantId: 'tenant_1',
    isActive: true,
    lastLogin: new Date().toISOString(),
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: new Date().toISOString()
  },
  {
    id: 'user_2',
    email: 'operator@abbanoa.com',
    password: bcrypt.hashSync('operator123', 10), // Password: operator123
    firstName: 'Water',
    lastName: 'Operator',
    role: 'operator',
    tenantId: 'tenant_1',
    isActive: true,
    lastLogin: new Date().toISOString(),
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: new Date().toISOString()
  },
  {
    id: 'user_3',
    email: 'super@abbanoa.com',
    password: bcrypt.hashSync('super123', 10), // Password: super123
    firstName: 'Super',
    lastName: 'Admin',
    role: 'super_admin',
    tenantId: 'tenant_1',
    isActive: true,
    lastLogin: new Date().toISOString(),
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: new Date().toISOString()
  }
];

const mockTenants = [
  {
    id: 'tenant_1',
    name: 'Abbanoa S.p.A.',
    domain: 'abbanoa',
    logo: null,
    plan: 'enterprise',
    isActive: true,
    settings: {
      maxUsers: 100,
      features: ['monitoring', 'anomaly_detection', 'reporting', 'analytics'],
      customBranding: {
        primaryColor: '#2563eb',
        logo: '',
        companyName: 'Abbanoa S.p.A.'
      }
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: new Date().toISOString()
  },
  {
    id: 'tenant_2',
    name: 'Test Organization',
    domain: 'test-org',
    logo: null,
    plan: 'professional',
    isActive: true,
    settings: {
      maxUsers: 50,
      features: ['monitoring', 'reporting'],
      customBranding: {
        primaryColor: '#059669',
        logo: '',
        companyName: 'Test Organization'
      }
    },
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: new Date().toISOString()
  }
];

// Helper functions
function generateToken(user, tenant) {
  return jwt.sign({ 
    userId: user.id, 
    tenantId: tenant.id,
    role: user.role,
    email: user.email 
  }, JWT_SECRET, { expiresIn: '24h' });
}

function generateRefreshToken(user, tenant) {
  return jwt.sign({ 
    userId: user.id, 
    tenantId: tenant.id,
    type: 'refresh'
  }, JWT_SECRET, { expiresIn: '7d' });
}

function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

function findUserByEmail(email) {
  return mockUsers.find(user => user.email === email);
}

function findUserById(id) {
  return mockUsers.find(user => user.id === id);
}

function findTenantById(id) {
  return mockTenants.find(tenant => tenant.id === id);
}

// Middleware to check authentication
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({
      success: false,
      error: 'Access token required'
    });
  }

  const decoded = verifyToken(token);
  if (!decoded || decoded.type === 'refresh') {
    return res.status(401).json({
      success: false,
      error: 'Invalid or expired token'
    });
  }

  req.user = decoded;
  next();
}

// Routes

// Health check
app.get('/api/v1/health', (req, res) => {
  res.json({
    success: true,
    data: {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'mock-auth-backend'
    }
  });
});

// Authentication routes
app.post('/api/v1/auth/login', async (req, res) => {
  try {
    console.log('🔐 Login attempt:', req.body.email);
    
    const { email, password, tenantDomain } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        success: false,
        error: 'Email and password are required'
      });
    }

    const user = findUserByEmail(email);
    if (!user) {
      return res.status(401).json({
        success: false,
        error: 'Invalid credentials'
      });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        error: 'Invalid credentials'
      });
    }

    const tenant = findTenantById(user.tenantId);
    if (!tenant) {
      return res.status(404).json({
        success: false,
        error: 'Tenant not found'
      });
    }

    // Check tenant domain if provided
    if (tenantDomain && tenant.domain !== tenantDomain) {
      return res.status(401).json({
        success: false,
        error: 'Invalid tenant domain'
      });
    }

    const accessToken = generateToken(user, tenant);
    const refreshToken = generateRefreshToken(user, tenant);

    // Update last login
    user.lastLogin = new Date().toISOString();

    const response = {
      user: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        tenantId: user.tenantId,
        isActive: user.isActive,
        lastLogin: user.lastLogin,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt
      },
      tenant,
      accessToken,
      refreshToken,
      expiresIn: 86400 // 24 hours
    };

    console.log('✅ Login successful for:', email);

    res.json({
      success: true,
      data: response
    });
  } catch (error) {
    console.error('❌ Login error:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

app.post('/api/v1/auth/register', async (req, res) => {
  try {
    const { email, password, firstName, lastName, tenantName, tenantDomain } = req.body;

    if (!email || !password || !firstName || !lastName) {
      return res.status(400).json({
        success: false,
        error: 'All fields are required'
      });
    }

    // Check if user already exists
    const existingUser = findUserByEmail(email);
    if (existingUser) {
      return res.status(409).json({
        success: false,
        error: 'User already exists'
      });
    }

    // For mock purposes, just return success but don't actually create user
    res.status(201).json({
      success: true,
      data: {
        message: 'Registration successful! Please login with the predefined admin credentials.',
        availableCredentials: [
          { email: 'admin@abbanoa.com', password: 'admin123', role: 'admin' },
          { email: 'operator@abbanoa.com', password: 'operator123', role: 'operator' },
          { email: 'super@abbanoa.com', password: 'super123', role: 'super_admin' }
        ]
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

app.post('/api/v1/auth/refresh', (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        error: 'Refresh token required'
      });
    }

    const decoded = verifyToken(refreshToken);
    if (!decoded || decoded.type !== 'refresh') {
      return res.status(401).json({
        success: false,
        error: 'Invalid refresh token'
      });
    }

    const user = findUserById(decoded.userId);
    const tenant = findTenantById(decoded.tenantId);

    if (!user || !tenant) {
      return res.status(404).json({
        success: false,
        error: 'User or tenant not found'
      });
    }

    const newAccessToken = generateToken(user, tenant);
    const newRefreshToken = generateRefreshToken(user, tenant);

    res.json({
      success: true,
      data: {
        accessToken: newAccessToken,
        refreshToken: newRefreshToken,
        expiresIn: 86400
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

app.post('/api/v1/auth/logout', authenticateToken, (req, res) => {
  res.json({
    success: true,
    data: { message: 'Logged out successfully' }
  });
});

// User info routes
app.get('/api/v1/auth/me', authenticateToken, (req, res) => {
  try {
    const user = findUserById(req.user.userId);
    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    res.json({
      success: true,
      data: {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        tenantId: user.tenantId,
        isActive: user.isActive,
        lastLogin: user.lastLogin,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// Tenant routes
app.get('/api/v1/tenants/current', authenticateToken, (req, res) => {
  try {
    const tenant = findTenantById(req.user.tenantId);
    if (!tenant) {
      return res.status(404).json({
        success: false,
        error: 'Tenant not found'
      });
    }

    res.json({
      success: true,
      data: tenant
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

app.get('/api/v1/auth/tenants', authenticateToken, (req, res) => {
  try {
    // For mock purposes, return all tenants (in real app, filter by user access)
    res.json({
      success: true,
      data: {
        tenants: mockTenants
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// Mock dashboard data routes
app.get('/api/v1/dashboard/metrics', authenticateToken, (req, res) => {
  res.json({
    success: true,
    data: {
      totalConsumption: 1250000,
      activeConnections: 3847,
      anomalies: 12,
      lastUpdate: new Date().toISOString(),
      tenantId: req.user.tenantId || 'tenant_1'
    }
  });
});

// Dashboard summary endpoint for enhanced overview
app.get('/api/v1/dashboard/summary', (req, res) => {
  res.json({
    success: true,
    data: {
      overview: {
        totalConsumption: 1250000,
        activeConnections: 3847,
        anomalies: 12,
        efficiency: 87.5,
        lastUpdate: new Date().toISOString()
      },
      metrics: {
        flowRate: {
          current: 245.8,
          average: 238.2,
          trend: 'stable'
        },
        pressure: {
          current: 3.2,
          average: 3.1,
          trend: 'stable'
        },
        quality: {
          ph: 7.2,
          chlorine: 1.8,
          turbidity: 0.5
        }
      },
      alerts: [
        {
          id: 'alert_001',
          type: 'pressure',
          severity: 'warning',
          message: 'Low pressure detected in Zone 2',
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          resolved: false
        },
        {
          id: 'alert_002',
          type: 'flow',
          severity: 'info',
          message: 'Unusual flow pattern in Industrial District',
          timestamp: new Date(Date.now() - 7200000).toISOString(),
          resolved: true
        }
      ],
      zones: [
        {
          id: 'zone_001',
          name: 'Central Business District',
          status: 'optimal',
          pressure: 3.2,
          flowRate: 45.2,
          nodeCount: 15
        },
        {
          id: 'zone_002',
          name: 'Residential North',
          status: 'warning',
          pressure: 2.8,
          flowRate: 52.1,
          nodeCount: 23
        },
        {
          id: 'zone_003',
          name: 'Industrial District',
          status: 'optimal',
          pressure: 3.5,
          flowRate: 78.3,
          nodeCount: 8
        },
        {
          id: 'zone_004',
          name: 'Residential Area',
          status: 'critical',
          pressure: 2.2,
          flowRate: 41.2,
          nodeCount: 31
        },
        {
          id: 'zone_005',
          name: 'Distribution Network',
          status: 'optimal',
          pressure: 3.0,
          flowRate: 89.7,
          nodeCount: 42
        }
      ]
    }
  });
});

// Mock pressure zones endpoint
app.get('/api/v1/pressure/zones', (req, res) => {
  res.json({
    success: true,
    zones: [
      {
        zone: 'ZONE_001',
        zoneName: 'Central Business District',
        minPressure: 2.8,
        avgPressure: 3.2,
        maxPressure: 3.8,
        nodeCount: 15,
        status: 'optimal'
      },
      {
        zone: 'ZONE_002',
        zoneName: 'Residential North',
        minPressure: 2.1,
        avgPressure: 2.8,
        maxPressure: 3.2,
        nodeCount: 23,
        status: 'warning'
      },
      {
        zone: 'ZONE_003',
        zoneName: 'Industrial District',
        minPressure: 3.0,
        avgPressure: 3.5,
        maxPressure: 4.0,
        nodeCount: 8,
        status: 'optimal'
      },
      {
        zone: 'ZONE_004',
        zoneName: 'Residential Area',
        minPressure: 1.8,
        avgPressure: 2.2,
        maxPressure: 2.6,
        nodeCount: 31,
        status: 'critical'
      },
      {
        zone: 'ZONE_005',
        zoneName: 'Distribution Network',
        minPressure: 2.5,
        avgPressure: 3.0,
        maxPressure: 3.5,
        nodeCount: 42,
        status: 'optimal'
      }
    ]
  });
});

// Mock nodes endpoint
app.get('/api/v1/nodes', (req, res) => {
  res.json([
    {
      node_id: 'NODE_211_001',
      node_name: 'Central Business Sensor 1',
      pressure: 3.2,
      flow_rate: 45.2,
      temperature: 18.5,
      status: 'active',
      last_reading: new Date().toISOString()
    },
    {
      node_id: 'NODE_211_002',
      node_name: 'Central Business Sensor 2',
      pressure: 3.5,
      flow_rate: 38.7,
      temperature: 19.1,
      status: 'active',
      last_reading: new Date().toISOString()
    },
    {
      node_id: 'NODE_215_001',
      node_name: 'Residential North Sensor 1',
      pressure: 2.8,
      flow_rate: 52.1,
      temperature: 17.8,
      status: 'active',
      last_reading: new Date().toISOString()
    },
    {
      node_id: 'NODE_273_001',
      node_name: 'Industrial Sensor 1',
      pressure: 3.8,
      flow_rate: 78.3,
      temperature: 20.2,
      status: 'active',
      last_reading: new Date().toISOString()
    },
    {
      node_id: 'NODE_281_001',
      node_name: 'Industrial Sensor 2',
      pressure: 3.6,
      flow_rate: 65.4,
      temperature: 19.8,
      status: 'active',
      last_reading: new Date().toISOString()
    },
    {
      node_id: 'NODE_287_001',
      node_name: 'Residential Area Sensor 1',
      pressure: 2.2,
      flow_rate: 41.2,
      temperature: 18.9,
      status: 'active',
      last_reading: new Date().toISOString()
    },
    {
      node_id: 'NODE_288_001',
      node_name: 'Residential Area Sensor 2',
      pressure: 1.8,
      flow_rate: 35.6,
      temperature: 18.2,
      status: 'active',
      last_reading: new Date().toISOString()
    },
    {
      node_id: 'DIST_001',
      node_name: 'Distribution Network Sensor 1',
      pressure: 3.0,
      flow_rate: 89.7,
      temperature: 19.5,
      status: 'active',
      last_reading: new Date().toISOString()
    }
  ]);
});

app.get('/api/v1/monitoring/status', authenticateToken, (req, res) => {
  res.json({
    success: true,
    data: {
      status: 'operational',
      uptime: '99.9%',
      activeAlerts: 2,
      lastUpdate: new Date().toISOString()
    }
  });
});

app.get('/api/v1/anomalies', authenticateToken, (req, res) => {
  res.json({
    success: true,
    data: [
      {
        id: 'anomaly_1',
        deviceId: 'sensor_001',
        type: 'pressure',
        severity: 'high',
        description: 'Pressure drop detected in main pipeline',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        resolved: false,
        tenantId: req.user.tenantId || 'tenant_1'
      },
      {
        id: 'anomaly_2',
        deviceId: 'sensor_045',
        type: 'flow',
        severity: 'medium',
        description: 'Unusual flow pattern detected',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        resolved: false,
        tenantId: req.user.tenantId || 'tenant_1'
      },
      {
        id: 'anomaly_3',
        deviceId: 'sensor_112',
        type: 'consumption',
        severity: 'low',
        description: 'Higher than average consumption',
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        resolved: true,
        tenantId: req.user.tenantId || 'tenant_1',
        resolvedBy: 'operator@abbanoa.com',
        resolvedAt: new Date(Date.now() - 3600000).toISOString()
      }
    ]
  });
});

// Validation routes
app.get('/api/v1/auth/validate-domain', (req, res) => {
  const { domain } = req.query;
  const exists = mockTenants.some(tenant => tenant.domain === domain);
  
  res.json({
    success: true,
    data: {
      available: !exists,
      suggestions: exists ? [`${domain}-1`, `${domain}-org`, `new-${domain}`] : []
    }
  });
});

app.get('/api/v1/auth/check-email', (req, res) => {
  const { email } = req.query;
  const exists = mockUsers.some(user => user.email === email);
  
  res.json({
    success: true,
    data: { exists }
  });
});

// Error handling
app.use((req, res) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found'
  });
});

app.use((error, req, res, next) => {
  console.error('Server error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Temporary public endpoints for testing (no auth required)
app.get('/api/v1/public/dashboard/metrics', (req, res) => {
  res.json({
    success: true,
    data: {
      totalConsumption: 1250000,
      activeConnections: 3847,
      anomalies: 12,
      lastUpdate: new Date().toISOString(),
      tenantId: 'tenant_1'
    }
  });
});

app.get('/api/v1/public/anomalies', (req, res) => {
  res.json({
    success: true,
    data: [
      {
        id: 'anomaly_1',
        deviceId: 'sensor_001',
        type: 'pressure',
        severity: 'high',
        description: 'Pressure drop detected in main pipeline',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        resolved: false,
        tenantId: 'tenant_1'
      },
      {
        id: 'anomaly_2',
        deviceId: 'sensor_045',
        type: 'flow',
        severity: 'medium',
        description: 'Unusual flow pattern detected',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        resolved: false,
        tenantId: 'tenant_1'
      }
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log('🚀 Mock Authentication Backend running on port', PORT);
  console.log('\n📋 Available Test Credentials:');
  console.log('┌─────────────────────────┬─────────────────┬──────────────┐');
  console.log('│ Email                   │ Password        │ Role         │');
  console.log('├─────────────────────────┼─────────────────┼──────────────┤');
  console.log('│ admin@abbanoa.com       │ admin123        │ admin        │');
  console.log('│ operator@abbanoa.com    │ operator123     │ operator     │');
  console.log('│ super@abbanoa.com       │ super123        │ super_admin  │');
  console.log('└─────────────────────────┴─────────────────┴──────────────┘');
  console.log('\n🌐 Frontend should be running on: http://localhost:3000');
  console.log('🔧 Backend API available at: http://localhost:' + PORT + '/api/v1');
  console.log('\n✅ Ready for testing!');
}); 