'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { useAuthContext } from '@/components/providers/AuthProvider';
import { LayoutProvider } from './LayoutProvider';

interface LayoutWrapperProps {
  children: React.ReactNode;
}

// Pages that don't require authentication
const PUBLIC_ROUTES = [
  '/auth/login',
  '/auth/register',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/auth/accept-invitation',
  '/test', // Test page without auth
];

// Pages that should not use the main layout (even if authenticated)
const STANDALONE_ROUTES = [
  ...PUBLIC_ROUTES,
  '/auth/logout',
];

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

export function LayoutWrapper({ children }: LayoutWrapperProps) {
  const pathname = usePathname();
  const { isAuthenticated, isLoading } = useAuthContext();

  const isPublicRoute = PUBLIC_ROUTES.includes(pathname);
  const isStandaloneRoute = STANDALONE_ROUTES.includes(pathname);

  // Show loading screen while authentication is being checked
  if (isLoading) {
    return <LoadingScreen />;
  }

  // For standalone routes (auth pages), render without main layout
  if (isStandaloneRoute) {
    return <>{children}</>;
  }

  // For protected routes, redirect to login if not authenticated
  if (!isAuthenticated) {
    // This will be handled by the ProtectedRoute component
    // But we provide a fallback loading screen
    return <LoadingScreen />;
  }

  // For authenticated users, use the main layout
  return (
    <LayoutProvider>
      {children}
    </LayoutProvider>
  );
} 