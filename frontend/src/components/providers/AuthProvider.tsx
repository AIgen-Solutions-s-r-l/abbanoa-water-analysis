'use client';

import React, { createContext, useContext } from 'react';
import { useAuth as useAuthHook } from '@/lib/hooks/useAuth';
import type { AuthState, User, Tenant, LoginRequest, RegisterRequest, AuthResponse, ChangePasswordRequest } from '@/lib/types/auth';

interface AuthContextValue extends AuthState {
  login: (credentials: LoginRequest) => Promise<AuthResponse>;
  register: (userData: RegisterRequest) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<User>;
  changePassword: (passwordData: ChangePasswordRequest) => Promise<any>;
  switchTenant: (tenantId: string) => Promise<AuthResponse>;
  clearError: () => void;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function useAuthContext() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }
  return context;
}

// Alias for backward compatibility
export const useAuth = useAuthContext;

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const auth = useAuthHook();
  
  // DEVELOPMENT MODE: If running locally, auto-login
  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development' && !auth.isAuthenticated && !auth.isLoading) {
      const devLogin = async () => {
        try {
          console.log('🔧 Development auto-login...');
          await auth.login({ 
            email: 'admin@abbanoa.com', 
            password: 'admin123' 
          });
        } catch (error) {
          console.log('🔧 Dev auto-login skipped:', error);
        }
      };
      
      // Only try once
      const hasTriedAutoLogin = sessionStorage.getItem('dev_auto_login_tried');
      if (!hasTriedAutoLogin) {
        sessionStorage.setItem('dev_auto_login_tried', 'true');
        devLogin();
      }
    }
  }, [auth.isAuthenticated, auth.isLoading]);

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
} 