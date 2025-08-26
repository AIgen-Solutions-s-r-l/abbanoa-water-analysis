import { apiClient } from '@/lib/api/client';
import {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  ChangePasswordRequest,
  User,
  Tenant,
} from '@/lib/types/auth';

export class AuthService {
  // Authentication endpoints
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    // For now, simulate successful login without calling backend
    // since the real backend doesn't have authentication yet
    
    const mockUser: User = {
      id: '1',
      email: credentials.email,
      name: 'Admin User',
      role: 'admin',
      tenantId: '1',
    };
    
    const mockTenant: Tenant = {
      id: '1', 
      name: 'Abbanoa Water',
      slug: 'abbanoa',
    };
    
    // Generate mock tokens
    const accessToken = 'mock-access-token';
    const refreshToken = 'mock-refresh-token';
    
    // Store tokens in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('tenantId', mockTenant.id);
    }
    
    return {
      success: true,
      user: mockUser,
      tenant: mockTenant,
      token: accessToken,
    };
  }

  static async register(userData: RegisterRequest): Promise<AuthResponse> {
    // Mock registration for now
    const mockUser: User = {
      id: '2',
      email: userData.email,
      name: userData.name,
      role: 'operator',
      tenantId: '1',
    };
    
    const mockTenant: Tenant = {
      id: '1',
      name: userData.tenantName || 'Default Organization',
      slug: 'default',
    };
    
    const response: AuthResponse = {
      success: true,
      user: mockUser,
      tenant: mockTenant,
      token: 'mock-access-token',
    };
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', 'mock-access-token');
      localStorage.setItem('tenantId', mockTenant.id);
    }
    
    return response;
  }

  static async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      // Always clear local tokens
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('tenantId');
      }
    }
  }

  static async refreshToken(refreshToken: string): Promise<AuthResponse> {
    // Mock refresh for now
    return {
      success: true,
      token: 'mock-new-access-token',
    };
  }

  static async resetPassword(email: string): Promise<{ success: boolean; message: string }> {
    // Mock implementation
    return {
      success: true,
      message: 'Password reset email sent',
    };
  }

  static async changePassword(data: ChangePasswordRequest): Promise<{ success: boolean; message: string }> {
    // Mock implementation
    return {
      success: true,
      message: 'Password changed successfully',
    };
  }

  static async getCurrentUser(): Promise<User> {
    // Mock implementation
    return {
      id: '1',
      email: 'admin@abbanoa.it',
      name: 'Admin User',
      role: 'admin',
      tenantId: '1',
    };
  }

  static async updateProfile(data: Partial<User>): Promise<User> {
    // Mock implementation
    const currentUser = await this.getCurrentUser();
    return {
      ...currentUser,
      ...data,
    };
  }

  static async switchTenant(tenantId: string): Promise<AuthResponse> {
    // Mock implementation
    const mockTenant: Tenant = {
      id: tenantId,
      name: 'New Tenant',
      slug: 'new-tenant',
    };
    
    if (typeof window !== 'undefined') {
      localStorage.setItem('tenantId', tenantId);
    }
    
    return {
      success: true,
      tenant: mockTenant,
    };
  }

  static async getAvailableTenants(): Promise<Tenant[]> {
    // Mock implementation
    return [
      {
        id: '1',
        name: 'Abbanoa Water',
        slug: 'abbanoa',
      },
      {
        id: '2',
        name: 'Test Organization',
        slug: 'test-org',
      },
    ];
  }
}