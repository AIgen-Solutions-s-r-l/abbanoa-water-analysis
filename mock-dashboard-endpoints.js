// Temporary public endpoints for dashboard testing
// Add these to your server.js file temporarily

// Public dashboard metrics (no auth required for testing)
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

// Public anomalies endpoint (no auth required for testing)
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
      },
      {
        id: 'anomaly_3',
        deviceId: 'sensor_112',
        type: 'consumption',
        severity: 'low',
        description: 'Higher than average consumption',
        timestamp: new Date(Date.now() - 10800000).toISOString(),
        resolved: true,
        tenantId: 'tenant_1',
        resolvedBy: 'operator@abbanoa.com',
        resolvedAt: new Date(Date.now() - 3600000).toISOString()
      }
    ]
  });
}); 