import { apiClient } from '@/lib/api/client';
import {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  RefreshTokenRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
  TenantSelectionResponse,
  User,
  Tenant,
} from '@/lib/types';

export class AuthService {
  // Authentication endpoints
  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    // For now, simulate successful login without calling backend
    // since the real backend doesn't have authentication yet
    
    const mockUser = {
      id: 'user-1',
      email: credentials.email,
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
    apiClient.setAuthTokens(accessToken, refreshToken, mockTenant.id);
    
    return {
      user: mockUser,
      tenant: mockTenant,
      accessToken,
      refreshToken,
      expiresIn: 86400
    };
  }

  static async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.authRequest<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    if (response.success && response.data) {
      // Store tokens and tenant info
      apiClient.setAuthTokens(
        response.data.accessToken,
        response.data.refreshToken,
        response.data.tenant.id
      );
    }
    
    return response.data;
  }

  static async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      // Always clear local tokens
      apiClient.clearAuthTokens();
    }
  }

  static async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.authRequest<AuthResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });
    
    if (response.success && response.data) {
      // Update stored tokens
      apiClient.setAuthTokens(
        response.data.accessToken,
        response.data.refreshToken,
        response.data.tenant.id
      );
    }
    
    return response.data;
  }

  static async resetPassword(data: ResetPasswordRequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.authRequest<{ success: boolean; message: string }>('/auth/reset-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    return response.data;
  }

  static async changePassword(data: ChangePasswordRequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.put<{ success: boolean; message: string }>('/auth/change-password', data);
    return response.data;
  }

  // User profile endpoints
  static async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  }

  static async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await apiClient.put<User>('/auth/profile', userData);
    return response.data;
  }

  // Tenant management endpoints
  static async getCurrentTenant(): Promise<Tenant> {
    const response = await apiClient.get<Tenant>('/tenants/current');
    return response.data;
  }

  static async getUserTenants(): Promise<Tenant[]> {
    const response = await apiClient.get<TenantSelectionResponse>('/auth/tenants');
    return response.data.tenants;
  }

  static async switchTenant(tenantId: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/switch-tenant', { tenantId });
    
    if (response.success && response.data) {
      // Update stored tokens and tenant
      apiClient.setAuthTokens(
        response.data.accessToken,
        response.data.refreshToken,
        response.data.tenant.id
      );
    }
    
    return response.data;
  }

  static async createTenant(tenantData: {
    name: string;
    domain: string;
    plan: string;
  }): Promise<Tenant> {
    const response = await apiClient.post<Tenant>('/tenants', tenantData);
    return response.data;
  }

  static async updateTenant(tenantId: string, tenantData: Partial<Tenant>): Promise<Tenant> {
    const response = await apiClient.put<Tenant>(`/tenants/${tenantId}`, tenantData);
    return response.data;
  }

  // Invitation endpoints
  static async inviteUser(userData: {
    email: string;
    firstName: string;
    lastName: string;
    role: string;
  }): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post<{ success: boolean; message: string }>('/auth/invite', userData);
    return response.data;
  }

  static async acceptInvitation(token: string, userData: {
    password: string;
    firstName?: string;
    lastName?: string;
  }): Promise<AuthResponse> {
    const response = await apiClient.authRequest<AuthResponse>('/auth/accept-invitation', {
      method: 'POST',
      body: JSON.stringify({ token, ...userData }),
    });
    
    if (response.success && response.data) {
      // Store tokens and tenant info
      apiClient.setAuthTokens(
        response.data.accessToken,
        response.data.refreshToken,
        response.data.tenant.id
      );
    }
    
    return response.data;
  }

  // Validation endpoints
  static async validateTenantDomain(domain: string): Promise<{ available: boolean; suggestions?: string[] }> {
    const response = await apiClient.authRequest<{ available: boolean; suggestions?: string[] }>(`/auth/validate-domain?domain=${domain}`);
    return response.data;
  }

  static async checkEmailExists(email: string): Promise<{ exists: boolean }> {
    const response = await apiClient.authRequest<{ exists: boolean }>(`/auth/check-email?email=${email}`);
    return response.data;
  }

  // Session management
  static getStoredTokens() {
    return apiClient.getStoredTokens();
  }

  static isAuthenticated(): boolean {
    const tokens = apiClient.getStoredTokens();
    return !!(tokens?.accessToken && tokens?.tenantId);
  }

  static clearSession() {
    apiClient.clearAuthTokens();
  }
} 