'use client';

import React, { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
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
  '/bypass', // Development bypass route
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
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthContext();

  const isPublicRoute = PUBLIC_ROUTES.some(route => pathname.startsWith(route));
  const isStandaloneRoute = STANDALONE_ROUTES.includes(pathname);

  useEffect(() => {
    // TEMPORARY: Development bypass - remove this in production
    if (process.env.NODE_ENV === 'development' && pathname === '/bypass') {
      console.log('🚀 Development bypass activated');
      return;
    }
    
    // TEMPORARY: MVP Demo bypass - allow specific routes without auth but WITH layout
    const mvpDemoRoutes = ['/', '/enhanced-overview', '/monitoring', '/anomalies'];
    if (process.env.NODE_ENV === 'development' && mvpDemoRoutes.includes(pathname)) {
      console.log('🎯 MVP Demo mode - bypassing auth for:', pathname);
      return;
    }
    
    if (!isLoading && !isAuthenticated && !isPublicRoute) {
      router.push('/auth/login?redirect=' + encodeURIComponent(pathname));
    }
  }, [isAuthenticated, isLoading, isPublicRoute, pathname, router]);

  // TEMPORARY: Allow bypass route
  if (pathname === '/bypass') {
    return (
      <LayoutProvider>
        <div className="min-h-screen bg-gray-50">
          <h1 className="text-center text-2xl font-bold py-8">Development Bypass Mode</h1>
          <div className="text-center space-x-4">
            <a href="/" className="text-blue-600 hover:underline">Go to Dashboard</a>
            <a href="/auth/login" className="text-blue-600 hover:underline">Go to Login</a>
          </div>
        </div>
      </LayoutProvider>
    );
  }

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
    // TEMPORARY: MVP Demo bypass - show layout for demo routes
    const mvpDemoRoutes = ['/', '/enhanced-overview', '/monitoring', '/anomalies', '/consumption', '/about'];
    if (process.env.NODE_ENV === 'development' && mvpDemoRoutes.includes(pathname)) {
      return (
        <LayoutProvider>
          {children}
        </LayoutProvider>
      );
    }
    
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