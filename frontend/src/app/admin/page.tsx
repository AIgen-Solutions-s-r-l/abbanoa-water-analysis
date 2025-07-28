'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  UsersIcon,
  ActivityIcon,
  ServerIcon,
  ShieldCheckIcon,
  AlertTriangleIcon,
  SettingsIcon,
  DatabaseIcon,
  KeyIcon,
  FileTextIcon,
  DownloadIcon,
  RefreshCwIcon,
  PlusIcon,
  EditIcon,
  TrashIcon,
  CheckCircleIcon
} from 'lucide-react';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: 'active' | 'inactive';
  lastLogin: string;
}

interface SystemStatus {
  database: 'online' | 'offline' | 'maintenance';
  api: 'online' | 'offline' | 'degraded';
  sensors: number;
  alerts: number;
}

const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('users');
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [systemConfig, setSystemConfig] = useState<any>({});

  const [systemStatus] = useState<SystemStatus>({
    database: 'online',
    api: 'online',
    sensors: 156,
    alerts: 3
  });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'users') {
        const response = await fetch('/api/proxy/v1/users?limit=100');
        if (response.ok) {
          const data = await response.json();
          setUsers(data.users.map((user: any) => ({
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role,
            status: user.status,
            lastLogin: user.last_login ? new Date(user.last_login).toLocaleString('it-IT') : 'Never'
          })));
        }
      } else if (activeTab === 'logs') {
        const response = await fetch('/api/proxy/v1/audit-logs?limit=50');
        if (response.ok) {
          const data = await response.json();
          setAuditLogs(data.logs);
        }
      } else if (activeTab === 'system') {
        const response = await fetch('/api/proxy/v1/system-config');
        if (response.ok) {
          const data = await response.json();
          setSystemConfig(data);
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = (userId: string, action: 'edit' | 'delete' | 'toggle') => {
    if (action === 'toggle') {
      setUsers(users.map(user => 
        user.id === userId 
          ? { ...user, status: user.status === 'active' ? 'inactive' : 'active' }
          : user
      ));
    } else if (action === 'delete') {
      if (confirm('Are you sure you want to delete this user?')) {
        setUsers(users.filter(user => user.id !== userId));
      }
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-3">
          <ShieldCheckIcon className="h-8 w-8 text-purple-600" />
          Administration Panel
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage users, system settings, and monitor infrastructure health
        </p>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Database Status</p>
              <p className="text-xl font-bold text-green-600">Online</p>
            </div>
            <DatabaseIcon className="h-8 w-8 text-green-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">API Status</p>
              <p className="text-xl font-bold text-green-600">Operational</p>
            </div>
            <ServerIcon className="h-8 w-8 text-green-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Sensors</p>
              <p className="text-xl font-bold text-blue-600">{systemStatus.sensors}</p>
            </div>
            <ActivityIcon className="h-8 w-8 text-blue-500 opacity-50" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Active Alerts</p>
              <p className="text-xl font-bold text-orange-600">{systemStatus.alerts}</p>
            </div>
            <AlertTriangleIcon className="h-8 w-8 text-orange-500 opacity-50" />
          </div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'users', label: 'User Management', icon: UsersIcon },
          { id: 'system', label: 'System Config', icon: SettingsIcon },
          { id: 'logs', label: 'Audit Logs', icon: FileTextIcon },
          { id: 'backup', label: 'Backup & Restore', icon: DatabaseIcon }
        ].map((tab) => (
          <button
            key={tab.id}
            className={`pb-3 px-1 flex items-center gap-2 ${
              activeTab === tab.id
                ? 'border-b-2 border-purple-500 text-purple-600'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900'
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'users' && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">User Management</h2>
            <Button variant="primary" className="flex items-center gap-2">
              <PlusIcon className="h-4 w-4" />
              Add User
            </Button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {user.name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {user.email}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        user.status === 'active' 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
                      }`}>
                        {user.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {user.lastLogin}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleUserAction(user.id, 'edit')}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          <EditIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleUserAction(user.id, 'toggle')}
                          className="text-yellow-600 hover:text-yellow-900"
                        >
                          <KeyIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleUserAction(user.id, 'delete')}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === 'system' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">API Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Rate Limit (requests/min)
                </label>
                <input
                  type="number"
                  defaultValue={systemConfig.api_rate_limit?.value?.requests_per_minute || 100}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-800"
                  id="api_rate_limit"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  API Timeout (seconds)
                </label>
                <input
                  type="number"
                  defaultValue={systemConfig.api_timeout?.value?.seconds || 30}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-800"
                  id="api_timeout"
                />
              </div>
              <Button 
                variant="primary" 
                className="w-full"
                onClick={async () => {
                  const rateLimit = (document.getElementById('api_rate_limit') as HTMLInputElement).value;
                  const timeout = (document.getElementById('api_timeout') as HTMLInputElement).value;
                  
                  try {
                    await fetch('/api/proxy/v1/system-config/api_rate_limit', {
                      method: 'PUT',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        config_value: { requests_per_minute: parseInt(rateLimit) },
                        description: 'API rate limiting configuration'
                      })
                    });
                    
                    await fetch('/api/proxy/v1/system-config/api_timeout', {
                      method: 'PUT',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({
                        config_value: { seconds: parseInt(timeout) },
                        description: 'API request timeout'
                      })
                    });
                    
                    alert('API settings saved successfully!');
                  } catch (error) {
                    alert('Failed to save API settings');
                  }
                }}
              >
                Save API Settings
              </Button>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Database Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Connection Pool Size
                </label>
                <input
                  type="number"
                  defaultValue={20}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-800"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Query Timeout (ms)
                </label>
                <input
                  type="number"
                  defaultValue={5000}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-800"
                />
              </div>
              <Button variant="primary" className="w-full">Save Database Settings</Button>
            </div>
          </Card>

          <Card className="p-6 md:col-span-2">
            <h3 className="text-lg font-semibold mb-4">Sensor Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Polling Interval (seconds)
                </label>
                <input
                  type="number"
                  defaultValue={60}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-800"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Error Threshold
                </label>
                <input
                  type="number"
                  defaultValue={5}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-800"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Retry Attempts
                </label>
                <input
                  type="number"
                  defaultValue={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-800"
                />
              </div>
            </div>
            <Button variant="primary" className="mt-4">Save Sensor Settings</Button>
          </Card>
        </div>
      )}

      {activeTab === 'logs' && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Audit Logs</h2>
            <div className="flex gap-2">
              <Button variant="secondary" className="flex items-center gap-2">
                <RefreshCwIcon className="h-4 w-4" />
                Refresh
              </Button>
              <Button variant="secondary" className="flex items-center gap-2">
                <DownloadIcon className="h-4 w-4" />
                Export
              </Button>
            </div>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="text-center py-8 text-gray-500">Loading audit logs...</div>
            ) : auditLogs.length > 0 ? (
              auditLogs.map((log, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div className="flex items-center gap-4">
                    <CheckCircleIcon className={`h-5 w-5 ${log.success ? 'text-green-500' : 'text-red-500'}`} />
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">{log.action}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        by {log.user_email_address || log.user_email || 'System'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {new Date(log.created_at).toLocaleString('it-IT')}
                    </p>
                    {log.ip_address && (
                      <p className="text-xs text-gray-500">IP: {log.ip_address}</p>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">No audit logs found</div>
            )}
          </div>
        </Card>
      )}

      {activeTab === 'backup' && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Backup Management</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium mb-4">Create Backup</h3>
                <div className="space-y-4">
                  <label className="flex items-center gap-3">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-purple-600" />
                    <span className="text-sm">Database</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-purple-600" />
                    <span className="text-sm">Configuration Files</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-purple-600" />
                    <span className="text-sm">Sensor Data</span>
                  </label>
                  <Button variant="primary" className="w-full">Create Backup Now</Button>
                </div>
              </div>
              
              <div>
                <h3 className="font-medium mb-4">Scheduled Backups</h3>
                <div className="space-y-3">
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <p className="text-sm font-medium">Daily Backup</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Every day at 02:00 AM</p>
                  </div>
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <p className="text-sm font-medium">Weekly Full Backup</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Every Sunday at 03:00 AM</p>
                  </div>
                  <Button variant="secondary" className="w-full">Configure Schedule</Button>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="font-medium mb-4">Recent Backups</h3>
            <div className="space-y-3">
              {[
                { name: 'Full_Backup_2024_01_14', size: '2.3 GB', date: '2024-01-14 02:00:00', status: 'completed' },
                { name: 'Daily_Backup_2024_01_13', size: '450 MB', date: '2024-01-13 02:00:00', status: 'completed' },
                { name: 'Full_Backup_2024_01_07', size: '2.1 GB', date: '2024-01-07 03:00:00', status: 'completed' }
              ].map((backup, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{backup.name}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{backup.date} • {backup.size}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="secondary" size="sm">Restore</Button>
                    <Button variant="danger" size="sm">Delete</Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default AdminPage; 