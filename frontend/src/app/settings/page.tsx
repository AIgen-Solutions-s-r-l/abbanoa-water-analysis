'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  BellIcon,
  GlobeIcon,
  MoonIcon,
  SunIcon,
  VolumeIcon,
  ShieldIcon,
  DatabaseIcon,
  ClockIcon,
  MailIcon,
  SmartphoneIcon,
  WifiIcon,
  SaveIcon
} from 'lucide-react';

interface Settings {
  notifications: {
    email: boolean;
    sms: boolean;
    push: boolean;
    alertTypes: {
      leaks: boolean;
      pressure: boolean;
      quality: boolean;
      maintenance: boolean;
    };
  };
  display: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    dateFormat: string;
    units: 'metric' | 'imperial';
  };
  system: {
    autoRefresh: boolean;
    refreshInterval: number;
    dataRetention: number;
    debugMode: boolean;
  };
}

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('notifications');
  const [hasChanges, setHasChanges] = useState(false);
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState<Settings>({
    notifications: {
      email: true,
      sms: false,
      push: true,
      alertTypes: {
        leaks: true,
        pressure: true,
        quality: true,
        maintenance: false
      }
    },
    display: {
      theme: 'auto',
      language: 'it',
      dateFormat: 'DD/MM/YYYY',
      units: 'metric'
    },
    system: {
      autoRefresh: true,
      refreshInterval: 30,
      dataRetention: 90,
      debugMode: false
    }
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/proxy/v1/profile/settings');
      if (response.ok) {
        const data = await response.json();
        setSettings({
          notifications: {
            email: data.notifications_email ?? true,
            sms: data.notifications_sms ?? false,
            push: data.notifications_push ?? true,
            alertTypes: {
              leaks: data.alert_types_leaks ?? true,
              pressure: data.alert_types_pressure ?? true,
              quality: data.alert_types_quality ?? true,
              maintenance: data.alert_types_maintenance ?? false
            }
          },
          display: {
            theme: (data.theme as 'light' | 'dark' | 'auto') ?? 'auto',
            language: data.language ?? 'it',
            dateFormat: data.date_format ?? 'DD/MM/YYYY',
            units: (data.units as 'metric' | 'imperial') ?? 'metric'
          },
          system: {
            autoRefresh: data.auto_refresh ?? true,
            refreshInterval: data.refresh_interval ?? 30,
            dataRetention: data.data_retention_days ?? 90,
            debugMode: data.debug_mode ?? false
          }
        });
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = (category: keyof Settings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
    setHasChanges(true);
  };

  const updateAlertType = (type: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        alertTypes: {
          ...prev.notifications.alertTypes,
          [type]: value
        }
      }
    }));
    setHasChanges(true);
  };

  const handleSave = async () => {
    try {
      const payload = {
        notifications_email: settings.notifications.email,
        notifications_sms: settings.notifications.sms,
        notifications_push: settings.notifications.push,
        alert_types_leaks: settings.notifications.alertTypes.leaks,
        alert_types_pressure: settings.notifications.alertTypes.pressure,
        alert_types_quality: settings.notifications.alertTypes.quality,
        alert_types_maintenance: settings.notifications.alertTypes.maintenance,
        theme: settings.display.theme,
        language: settings.display.language,
        date_format: settings.display.dateFormat,
        units: settings.display.units,
        auto_refresh: settings.system.autoRefresh,
        refresh_interval: settings.system.refreshInterval,
        data_retention_days: settings.system.dataRetention,
        debug_mode: settings.system.debugMode
      };

      const response = await fetch('/api/proxy/v1/profile/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        setHasChanges(false);
        alert('Settings saved successfully!');
      } else {
        alert('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Customize your dashboard experience and preferences
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
        {[
          { id: 'notifications', label: 'Notifications', icon: BellIcon },
          { id: 'display', label: 'Display', icon: SunIcon },
          { id: 'system', label: 'System', icon: DatabaseIcon },
          { id: 'security', label: 'Security', icon: ShieldIcon }
        ].map((tab) => (
          <button
            key={tab.id}
            className={`pb-3 px-1 flex items-center gap-2 ${
              activeTab === tab.id
                ? 'border-b-2 border-blue-500 text-blue-600'
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
      {activeTab === 'notifications' && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Notification Preferences</h2>
            
            <div className="space-y-6">
              {/* Notification Channels */}
              <div>
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-4">
                  Notification Channels
                </h3>
                <div className="space-y-3">
                  <label className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <MailIcon className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">Email Notifications</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Receive alerts via email
                        </p>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.notifications.email}
                      onChange={(e) => updateSettings('notifications', 'email', e.target.checked)}
                      className="h-5 w-5 text-blue-600"
                    />
                  </label>

                  <label className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <SmartphoneIcon className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">SMS Notifications</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Get text messages for critical alerts
                        </p>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.notifications.sms}
                      onChange={(e) => updateSettings('notifications', 'sms', e.target.checked)}
                      className="h-5 w-5 text-blue-600"
                    />
                  </label>

                  <label className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <BellIcon className="h-5 w-5 text-gray-500" />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-gray-100">Push Notifications</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Browser notifications for real-time alerts
                        </p>
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={settings.notifications.push}
                      onChange={(e) => updateSettings('notifications', 'push', e.target.checked)}
                      className="h-5 w-5 text-blue-600"
                    />
                  </label>
                </div>
              </div>

              {/* Alert Types */}
              <div>
                <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-4">
                  Alert Types
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(settings.notifications.alertTypes).map(([type, enabled]) => (
                    <label key={type} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <input
                        type="checkbox"
                        checked={enabled}
                        onChange={(e) => updateAlertType(type, e.target.checked)}
                        className="h-4 w-4 text-blue-600"
                      />
                      <span className="capitalize text-gray-700 dark:text-gray-300">
                        {type} Alerts
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'display' && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Display Settings</h2>
            
            <div className="space-y-6">
              {/* Theme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Theme
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: 'light', label: 'Light', icon: SunIcon },
                    { value: 'dark', label: 'Dark', icon: MoonIcon },
                    { value: 'auto', label: 'Auto', icon: ClockIcon }
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => updateSettings('display', 'theme', option.value)}
                      className={`p-3 rounded-lg border-2 transition-colors ${
                        settings.display.theme === option.value
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700'
                      }`}
                    >
                      <option.icon className="h-6 w-6 mx-auto mb-1" />
                      <p className="text-sm font-medium">{option.label}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Language */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Language
                </label>
                <select
                  value={settings.display.language}
                  onChange={(e) => updateSettings('display', 'language', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                >
                  <option value="it">Italiano</option>
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                </select>
              </div>

              {/* Date Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Date Format
                </label>
                <select
                  value={settings.display.dateFormat}
                  onChange={(e) => updateSettings('display', 'dateFormat', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                >
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>

              {/* Units */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Units
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => updateSettings('display', 'units', 'metric')}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      settings.display.units === 'metric'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <p className="font-medium">Metric</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">L/s, bar, °C</p>
                  </button>
                  <button
                    onClick={() => updateSettings('display', 'units', 'imperial')}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      settings.display.units === 'imperial'
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <p className="font-medium">Imperial</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">GPM, PSI, °F</p>
                  </button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'system' && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">System Settings</h2>
            
            <div className="space-y-6">
              {/* Auto Refresh */}
              <div>
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Auto Refresh</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Automatically update dashboard data
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.system.autoRefresh}
                    onChange={(e) => updateSettings('system', 'autoRefresh', e.target.checked)}
                    className="h-5 w-5 text-blue-600"
                  />
                </label>
              </div>

              {/* Refresh Interval */}
              {settings.system.autoRefresh && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Refresh Interval (seconds)
                  </label>
                  <input
                    type="number"
                    value={settings.system.refreshInterval}
                    onChange={(e) => updateSettings('system', 'refreshInterval', parseInt(e.target.value))}
                    min="10"
                    max="300"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                  />
                </div>
              )}

              {/* Data Retention */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Data Retention (days)
                </label>
                <select
                  value={settings.system.dataRetention}
                  onChange={(e) => updateSettings('system', 'dataRetention', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-800"
                >
                  <option value={30}>30 days</option>
                  <option value={60}>60 days</option>
                  <option value={90}>90 days</option>
                  <option value={180}>180 days</option>
                  <option value={365}>1 year</option>
                </select>
              </div>

              {/* Debug Mode */}
              <div>
                <label className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Debug Mode</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Show additional technical information
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings.system.debugMode}
                    onChange={(e) => updateSettings('system', 'debugMode', e.target.checked)}
                    className="h-5 w-5 text-blue-600"
                  />
                </label>
              </div>
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-6">Security Settings</h2>
            
            <div className="space-y-6">
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  For security reasons, some settings can only be changed by administrators.
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Two-Factor Authentication</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Currently enabled</p>
                  </div>
                  <Button variant="secondary" size="sm">
                    Configure
                  </Button>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">Session Timeout</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">30 minutes</p>
                  </div>
                  <Button variant="secondary" size="sm">
                    Change
                  </Button>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">API Access</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Manage API keys</p>
                  </div>
                  <Button variant="secondary" size="sm">
                    Manage
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Save Button */}
      {hasChanges && (
        <div className="fixed bottom-8 right-8">
          <Button
            onClick={handleSave}
            variant="primary"
            className="flex items-center gap-2 shadow-lg"
          >
            <SaveIcon className="h-4 w-4" />
            Save Changes
          </Button>
        </div>
      )}
    </div>
  );
};

export default SettingsPage; 