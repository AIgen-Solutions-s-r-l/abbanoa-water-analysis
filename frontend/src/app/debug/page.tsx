'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DebugPage() {
  const router = useRouter();

  useEffect(() => {
    // Clear all authentication data
    localStorage.clear();
    sessionStorage.clear();
    
    // Clear cookies
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
    
    console.log('✅ Cleared all authentication data');
    console.log('🔗 API URL:', process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001');
    
    // Redirect to login after clearing
    setTimeout(() => {
      router.push('/auth/login');
    }, 2000);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Debug Mode</h2>
          <p className="mt-2 text-gray-600">Clearing authentication data...</p>
          
          <div className="mt-8 space-y-2">
            <p className="text-sm text-gray-500">
              API URL: {process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8001'}
            </p>
            <p className="text-sm text-gray-500">
              Protocol: {typeof window !== 'undefined' ? window.location.protocol : 'unknown'}
            </p>
          </div>
          
          <div className="mt-8">
            <p className="text-sm text-gray-600">Redirecting to login page in 2 seconds...</p>
          </div>
        </div>
      </div>
    </div>
  );
} 