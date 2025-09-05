import { apiClient } from '@/lib/api/client';
import {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  ChangePasswordRequest,
  RefreshTokenRequest,
  ResetPasswordRequest,
  TenantSelectionResponse,
  User,
  Tenant,
} from '@/lib/types/auth';

export class AuthService {
  // Authentication endpoints
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    // For now, simulate successful login without calling backend
    // since the real backend doesn't have authentication yet
    
    const mockUser = {
      id: 'user-1',
      email: credentials.email,
      name: 'Admin User',
      firstName: 'Admin',
      lastName: 'User',
      role: 'admin' as 'admin' | 'operator' | 'viewer' | 'super_admin',
      tenantId: 'default',
      isActive: true,
      lastLogin: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    const mockTenant = {
      id: 'default',
      name: 'Abbanoa S.p.A.',
      slug: 'abbanoa',
      domain: 'abbanoa',
      logo: undefined,
      plan: 'enterprise' as 'basic' | 'professional' | 'enterprise',
      isActive: true,
      settings: {
        maxUsers: 100,
        features: ['monitoring', 'anomaly_detection', 'reporting', 'analytics'],
        customBranding: {
          primaryColor: '#2563eb',
          logo: '',
          companyName: 'Abbanoa S.p.A.'
        }
      },
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    // Generate mock tokens
    const accessToken = 'mock-access-token';
    const refreshToken = 'mock-refresh-token';
    
    // Store tokens
    // TODO: Implement proper token storage
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('tenantId', mockTenant.id);
    }
    
    return {
      success: true,
      token: accessToken,
      user: mockUser,
      tenant: mockTenant
    };
  }

  static async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (response.success) {
      // Store tokens and tenant info
      // TODO: Implement proper token storage
      /*apiClient.setAuthTokens(
        response.token,
        response.refreshToken,
        response.tenant?.id
      );*/
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
      // TODO: Implement proper token clearing
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('tenantId');
      }
    }
  }

  static async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.request<AuthResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });
    
    if (response.success) {
      // Update stored tokens
      // TODO: Implement proper token storage
      /*apiClient.setAuthTokens(
        response.token,
        response.refreshToken,
        response.tenant?.id
      );*/
    }
    
    return response;
  }

  static async resetPassword(data: ResetPasswordRequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.request<{ success: boolean; message: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    return response;
  }

  static async changePassword(data: ChangePasswordRequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.put<{ success: boolean; message: string }>('/auth/change-password', data);
    return response;
  }

  // User profile endpoints
  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response;
  }

  static async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/auth/profile', userData);
    return response;
  }

  // Tenant management endpoints
  static async getCurrentTenant(): Promise<Tenant> {
    const response = await apiClient.get<Tenant>('/tenants/current');
    return response;
  }

  static async getUserTenants(): Promise<Tenant[]> {
    try {
      const response = await apiClient.get<TenantSelectionResponse>('/auth/tenants');
      return response?.tenants || [];
    } catch (error) {
      console.error('Failed to fetch user tenants:', error);
      return [];
    }
  }

  static async switchTenant(tenantId: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/switch-tenant', { tenantId });
    
    if (response.success) {
      // Update stored tokens and tenant
      // TODO: Implement proper token storage
      /*apiClient.setAuthTokens(
        response.token,
        response.refreshToken,
        response.tenant?.id
      );*/
    }
    
    return response;
  }

  static async createTenant(tenantData: {
    name: string;
    domain: string;
    plan: string;
  }): Promise<Tenant> {
    const response = await apiClient.post<Tenant>('/tenants', tenantData);
    return response;
  }

  static async updateTenant(tenantId: string, tenantData: Partial<Tenant>): Promise<Tenant> {
    const response = await apiClient.put<Tenant>(`/tenants/${tenantId}`, tenantData);
    return response;
  }

  // Invitation endpoints
  static async inviteUser(userData: {
    email: string;
    firstName: string;
    lastName: string;
    role: string;
  }): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<{ success: boolean; message: string }>('/auth/invite', userData);
    return response;
  }

  static async acceptInvitation(token: string, userData: {
    password: string;
    firstName?: string;
    lastName?: string;
  }): Promise<AuthResponse> {
    const response = await apiClient.request<AuthResponse>('/auth/accept-invitation', {
      method: 'POST',
      body: JSON.stringify({ token, ...userData }),
    });
    
    if (response.success) {
      // Store tokens and tenant info
      // TODO: Implement proper token storage
      /*apiClient.setAuthTokens(
        response.token,
        response.refreshToken,
        response.tenant?.id
      );*/
    }
    
    return response;
  }

  // Validation endpoints
  static async validateTenantDomain(domain: string): Promise<{ available: boolean; suggestions?: string[] }> {
    const response = await apiClient.request<{ available: boolean; suggestions?: string[] }>(`/auth/validate-domain?domain=${domain}`);
    return response;
  }

  static async checkEmailExists(email: string): Promise<{ exists: boolean }> {
    const response = await apiClient.request<{ exists: boolean }>(`/auth/check-email?email=${email}`);
    return response;
  }

  // Session management
  static getStoredTokens() {
    if (typeof window !== 'undefined') {
      return {
        accessToken: localStorage.getItem('authToken'),
        refreshToken: localStorage.getItem('refreshToken'),
        tenantId: localStorage.getItem('tenantId')
      };
    }
    return null;
  }

  static isAuthenticated(): boolean {
    const tokens = AuthService.getStoredTokens();
    return !!(tokens?.accessToken && tokens?.tenantId);
  }

  static clearSession() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('tenantId');
    }
  }
} 