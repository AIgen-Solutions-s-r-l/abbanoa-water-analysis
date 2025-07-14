'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuthContext } from '@/components/providers/AuthProvider';
import { UserRole, ProtectedRouteProps } from '@/lib/types';

function LoadingScreen() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
      </div>
    </div>
  );
}

function UnauthorizedScreen({ message }: { message: string }) {
  const router = useRouter();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center max-w-md mx-auto">
        <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-red-100 dark:bg-red-900">
          <svg className="h-6 w-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h2 className="mt-4 text-xl font-bold text-gray-900 dark:text-white">
          Access Denied
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          {message}
        </p>
        <div className="mt-6 space-x-3">
          <button
            onClick={() => router.back()}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
          >
            Go Back
          </button>
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Go Home
          </button>
        </div>
      </div>
    </div>
  );
}

export function ProtectedRoute({ 
  children, 
  requiredRole, 
  requiredPermissions,
  fallback 
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user, tenant } = useAuthContext();
  const router = useRouter();

  // Show loading screen while authentication is being checked
  if (isLoading) {
    return <LoadingScreen />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    const currentPath = window.location.pathname;
    router.push(`/auth/login?redirect=${encodeURIComponent(currentPath)}`);
    return <LoadingScreen />;
  }

  // Check if user or tenant is missing
  if (!user || !tenant) {
    return <UnauthorizedScreen message="User or organization information is missing. Please try logging in again." />;
  }

  // Check role-based access
  if (requiredRole && !hasRequiredRole(user.role, requiredRole)) {
    const message = `This page requires ${requiredRole} access. You currently have ${user.role} access.`;
    return fallback || <UnauthorizedScreen message={message} />;
  }

  // Check permission-based access
  if (requiredPermissions && !hasRequiredPermissions(user, requiredPermissions)) {
    const message = "You don't have the required permissions to access this page.";
    return fallback || <UnauthorizedScreen message={message} />;
  }

  // User is authenticated and authorized
  return <>{children}</>;
}

// Helper function to check role hierarchy
function hasRequiredRole(userRole: UserRole, requiredRole: UserRole): boolean {
  const roleHierarchy: Record<UserRole, number> = {
    viewer: 1,
    operator: 2,
    admin: 3,
    super_admin: 4,
  };

  return roleHierarchy[userRole] >= roleHierarchy[requiredRole];
}

// Helper function to check permissions (simplified)
function hasRequiredPermissions(user: any, requiredPermissions: any[]): boolean {
  // This is a simplified implementation
  // In a real app, you'd check against actual user permissions
  
  // Super admins have all permissions
  if (user.role === 'super_admin') {
    return true;
  }

  // Admins have most permissions except super admin actions
  if (user.role === 'admin') {
    return !requiredPermissions.some(p => p.resource === 'system' && p.action === 'manage');
  }

  // Basic permission checking for other roles
  // This would be more sophisticated in a real application
  return true;
}

// Higher-order component for role-based protection
export function withAuth<T extends object>(
  Component: React.ComponentType<T>,
  requiredRole?: UserRole,
  requiredPermissions?: any[]
) {
  return function AuthenticatedComponent(props: T) {
    return (
      <ProtectedRoute 
        requiredRole={requiredRole}
        requiredPermissions={requiredPermissions}
      >
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

// Hook for checking permissions in components
export function usePermissions() {
  const { user, isAuthenticated } = useAuthContext();

  const hasRole = (role: UserRole) => {
    if (!isAuthenticated || !user) return false;
    return hasRequiredRole(user.role, role);
  };

  const hasPermission = (resource: string, action: string) => {
    if (!isAuthenticated || !user) return false;
    // Simplified permission check
    return hasRequiredPermissions(user, [{ resource, action }]);
  };

  const canAccess = (requiredRole?: UserRole, requiredPermissions?: any[]) => {
    if (!isAuthenticated || !user) return false;
    
    if (requiredRole && !hasRequiredRole(user.role, requiredRole)) {
      return false;
    }
    
    if (requiredPermissions && !hasRequiredPermissions(user, requiredPermissions)) {
      return false;
    }
    
    return true;
  };

  return {
    hasRole,
    hasPermission,
    canAccess,
    userRole: user?.role,
  };
} 