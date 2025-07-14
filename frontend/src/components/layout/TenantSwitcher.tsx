'use client';

import React, { useState } from 'react';
import { useAuthContext } from '@/components/providers/AuthProvider';
import { useTenants } from '@/lib/hooks/useAuth';
import { Button } from '@/components/ui/Button';

export function TenantSwitcher() {
  const [isOpen, setIsOpen] = useState(false);
  const { tenant, switchTenant, isLoading } = useAuthContext();
  const { tenants, loading: tenantsLoading } = useTenants();

  const handleTenantSwitch = async (tenantId: string) => {
    if (tenantId === tenant?.id) {
      setIsOpen(false);
      return;
    }

    try {
      await switchTenant(tenantId);
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to switch tenant:', error);
    }
  };

  if (!tenant) {
    return null;
  }

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 max-w-xs truncate"
        disabled={isLoading}
      >
        <div className="flex items-center space-x-2">
          {/* Tenant Avatar/Logo */}
          <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
            <span className="text-xs font-medium text-white">
              {tenant.name.charAt(0).toUpperCase()}
            </span>
          </div>
          
          {/* Tenant Name */}
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
            {tenant.name}
          </span>
          
          {/* Dropdown Arrow */}
          <svg 
            className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </Button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Menu */}
          <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-20">
            <div className="py-1">
              {/* Current Tenant Header */}
              <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Current Organization
                </p>
                <div className="flex items-center space-x-2 mt-1">
                  <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
                    <span className="text-sm font-medium text-white">
                      {tenant.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {tenant.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {tenant.domain} • {tenant.plan}
                    </p>
                  </div>
                </div>
              </div>

              {/* Available Tenants */}
              {tenantsLoading ? (
                <div className="px-4 py-3">
                  <div className="animate-pulse flex space-x-2">
                    <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    <div className="flex-1 space-y-1">
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                      <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  {tenants.filter(t => t.id !== tenant.id).length > 0 && (
                    <>
                      <div className="px-4 py-2">
                        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                          Switch To
                        </p>
                      </div>
                      
                      {tenants
                        .filter(t => t.id !== tenant.id)
                        .map((availableTenant) => (
                          <button
                            key={availableTenant.id}
                            onClick={() => handleTenantSwitch(availableTenant.id)}
                            className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                            disabled={isLoading}
                          >
                            <div className="w-8 h-8 bg-gray-600 rounded flex items-center justify-center">
                              <span className="text-sm font-medium text-white">
                                {availableTenant.name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {availableTenant.name}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {availableTenant.domain} • {availableTenant.plan}
                              </p>
                            </div>
                          </button>
                        ))}
                    </>
                  )}
                </>
              )}

              {/* Actions */}
              <div className="border-t border-gray-200 dark:border-gray-700 py-1">
                <button
                  onClick={() => {
                    setIsOpen(false);
                    // Navigate to tenant settings
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <span>Organization Settings</span>
                </button>
                
                <button
                  onClick={() => {
                    setIsOpen(false);
                    // Navigate to create new tenant
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Create Organization</span>
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
} 