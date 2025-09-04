import { AuthService } from '../auth.service';
import { apiClient } from '@/lib/api/client';
import {
  LoginRequest,
  RegisterRequest,
  ChangePasswordRequest,
  RefreshTokenRequest,
  ResetPasswordRequest,
} from '@/lib/types/auth';

// Mock API client
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    request: jest.fn(),
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock: Storage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  key: jest.fn(),
  length: 0,
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true,
});

describe('AuthService Integration Tests', () => {
  let consoleWarnSpy: jest.SpyInstance;
  let consoleErrorSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.clearAllMocks();
    consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation(() => {});
    consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    (localStorageMock.getItem as jest.Mock).mockReturnValue(null);
  });

  afterEach(() => {
    consoleWarnSpy.mockRestore();
    consoleErrorSpy.mockRestore();
  });

  describe('Authentication Flow', () => {
    describe('login', () => {
      it('should successfully authenticate a user', async () => {
        // Arrange
        const credentials: LoginRequest = {
          email: 'test@example.com',
          password: 'password123',
          tenantDomain: 'test-tenant',
        };

        // Act
        const result = await AuthService.login(credentials);

        // Assert
        expect(result.success).toBe(true);
        expect(result.token).toBe('mock-access-token');
        expect(result.user?.email).toBe(credentials.email);
        expect(result.tenant?.name).toBe('Abbanoa S.p.A.');
        
        // Verify tokens are stored
        expect(localStorageMock.setItem).toHaveBeenCalledWith('authToken', 'mock-access-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('refreshToken', 'mock-refresh-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('tenantId', 'default');
      });

      it('should set correct user properties on login', async () => {
        // Arrange
        const credentials: LoginRequest = {
          email: 'admin@example.com',
          password: 'admin123',
        };

        // Act
        const result = await AuthService.login(credentials);

        // Assert
        expect(result.user).toMatchObject({
          email: 'admin@example.com',
          name: 'Admin User',
          firstName: 'Admin',
          lastName: 'User',
          role: 'admin',
          isActive: true,
        });
      });

      it('should set correct tenant properties on login', async () => {
        // Arrange
        const credentials: LoginRequest = {
          email: 'user@example.com',
          password: 'password',
        };

        // Act
        const result = await AuthService.login(credentials);

        // Assert
        expect(result.tenant).toMatchObject({
          name: 'Abbanoa S.p.A.',
          slug: 'abbanoa',
          domain: 'abbanoa',
          plan: 'enterprise',
          isActive: true,
        });
        expect(result.tenant?.settings?.features).toContain('monitoring');
        expect(result.tenant?.settings?.features).toContain('anomaly_detection');
      });
    });

    describe('logout', () => {
      it('should clear session on successful logout', async () => {
        // Arrange
        (apiClient.post as jest.Mock).mockResolvedValue({ success: true });

        // Act
        await AuthService.logout();

        // Assert
        expect(apiClient.post).toHaveBeenCalledWith('/auth/logout');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('authToken');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('tenantId');
      });

      it('should clear session even if logout request fails', async () => {
        // Arrange
        (apiClient.post as jest.Mock).mockRejectedValue(new Error('Network error'));

        // Act
        await AuthService.logout();

        // Assert
        expect(consoleWarnSpy).toHaveBeenCalledWith('Logout request failed:', expect.any(Error));
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('authToken');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('tenantId');
      });
    });

    describe('register', () => {
      it('should register a new user', async () => {
        // Arrange
        const userData: RegisterRequest = {
          email: 'newuser@example.com',
          password: 'password123',
          firstName: 'New',
          lastName: 'User',
          tenantDomain: 'new-tenant',
        };

        const mockResponse = {
          success: true,
          token: 'new-access-token',
          refreshToken: 'new-refresh-token',
          user: {
            id: 'new-user-id',
            email: userData.email,
            firstName: userData.firstName,
            lastName: userData.lastName,
          },
          tenant: {
            id: 'new-tenant-id',
            name: 'New Tenant',
          },
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.register(userData);

        // Assert
        expect(apiClient.request).toHaveBeenCalledWith('/auth/register', {
          method: 'POST',
          body: JSON.stringify(userData),
        });
        expect(result).toEqual(mockResponse);
      });

      it('should handle registration failure', async () => {
        // Arrange
        const userData: RegisterRequest = {
          email: 'existing@example.com',
          password: 'password123',
        };

        const mockError = {
          success: false,
          error: 'Email already exists',
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockError);

        // Act
        const result = await AuthService.register(userData);

        // Assert
        expect(result.success).toBe(false);
        expect(result.error).toBe('Email already exists');
      });
    });
  });

  describe('Token Management', () => {
    describe('refreshToken', () => {
      it('should refresh authentication token', async () => {
        // Arrange
        const refreshToken = 'old-refresh-token';
        const mockResponse = {
          success: true,
          token: 'new-access-token',
          refreshToken: 'new-refresh-token',
          user: { id: 'user-1' },
          tenant: { id: 'tenant-1' },
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.refreshToken(refreshToken);

        // Assert
        expect(apiClient.request).toHaveBeenCalledWith('/auth/refresh', {
          method: 'POST',
          body: JSON.stringify({ refreshToken }),
        });
        expect(result).toEqual(mockResponse);
      });

      it('should handle token refresh failure', async () => {
        // Arrange
        const refreshToken = 'invalid-token';
        const mockError = {
          success: false,
          error: 'Invalid refresh token',
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockError);

        // Act
        const result = await AuthService.refreshToken(refreshToken);

        // Assert
        expect(result.success).toBe(false);
        expect(result.error).toBe('Invalid refresh token');
      });
    });

    describe('getStoredTokens', () => {
      it('should retrieve stored tokens', () => {
        // Arrange
        (localStorageMock.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'authToken') return 'stored-access-token';
          if (key === 'refreshToken') return 'stored-refresh-token';
          if (key === 'tenantId') return 'stored-tenant-id';
          return null;
        });

        // Act
        const tokens = AuthService.getStoredTokens();

        // Assert
        expect(tokens).toEqual({
          accessToken: 'stored-access-token',
          refreshToken: 'stored-refresh-token',
          tenantId: 'stored-tenant-id',
        });
      });

      it('should return null values when tokens are not stored', () => {
        // Arrange
        (localStorageMock.getItem as jest.Mock).mockReturnValue(null);

        // Act
        const tokens = AuthService.getStoredTokens();

        // Assert
        expect(tokens).toEqual({
          accessToken: null,
          refreshToken: null,
          tenantId: null,
        });
      });
    });
  });

  describe('User Profile Management', () => {
    describe('getCurrentUser', () => {
      it('should fetch current user profile', async () => {
        // Arrange
        const mockUser = {
          id: 'user-1',
          email: 'user@example.com',
          firstName: 'John',
          lastName: 'Doe',
          role: 'operator',
        };

        (apiClient.get as jest.Mock).mockResolvedValue(mockUser);

        // Act
        const result = await AuthService.getCurrentUser();

        // Assert
        expect(apiClient.get).toHaveBeenCalledWith('/auth/me');
        expect(result).toEqual(mockUser);
      });
    });

    describe('updateProfile', () => {
      it('should update user profile', async () => {
        // Arrange
        const updates = {
          firstName: 'Jane',
          lastName: 'Smith',
        };

        const mockUpdatedUser = {
          id: 'user-1',
          email: 'user@example.com',
          firstName: 'Jane',
          lastName: 'Smith',
          role: 'operator',
        };

        (apiClient.put as jest.Mock).mockResolvedValue(mockUpdatedUser);

        // Act
        const result = await AuthService.updateProfile(updates);

        // Assert
        expect(apiClient.put).toHaveBeenCalledWith('/auth/profile', updates);
        expect(result).toEqual(mockUpdatedUser);
      });
    });

    describe('changePassword', () => {
      it('should change user password', async () => {
        // Arrange
        const passwordData: ChangePasswordRequest = {
          currentPassword: 'oldPassword123',
          newPassword: 'newPassword456',
        };

        const mockResponse = {
          success: true,
          message: 'Password changed successfully',
        };

        (apiClient.put as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.changePassword(passwordData);

        // Assert
        expect(apiClient.put).toHaveBeenCalledWith('/auth/change-password', passwordData);
        expect(result).toEqual(mockResponse);
      });

      it('should handle password change failure', async () => {
        // Arrange
        const passwordData: ChangePasswordRequest = {
          currentPassword: 'wrongPassword',
          newPassword: 'newPassword456',
        };

        const mockError = {
          success: false,
          message: 'Current password is incorrect',
        };

        (apiClient.put as jest.Mock).mockResolvedValue(mockError);

        // Act
        const result = await AuthService.changePassword(passwordData);

        // Assert
        expect(result.success).toBe(false);
        expect(result.message).toBe('Current password is incorrect');
      });
    });
  });

  describe('Tenant Management', () => {
    describe('getCurrentTenant', () => {
      it('should fetch current tenant', async () => {
        // Arrange
        const mockTenant = {
          id: 'tenant-1',
          name: 'Test Tenant',
          domain: 'test-tenant',
          plan: 'professional',
        };

        (apiClient.get as jest.Mock).mockResolvedValue(mockTenant);

        // Act
        const result = await AuthService.getCurrentTenant();

        // Assert
        expect(apiClient.get).toHaveBeenCalledWith('/tenants/current');
        expect(result).toEqual(mockTenant);
      });
    });

    describe('getUserTenants', () => {
      it('should fetch user tenants', async () => {
        // Arrange
        const mockResponse = {
          tenants: [
            { id: 'tenant-1', name: 'Tenant 1' },
            { id: 'tenant-2', name: 'Tenant 2' },
          ],
        };

        (apiClient.get as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.getUserTenants();

        // Assert
        expect(apiClient.get).toHaveBeenCalledWith('/auth/tenants');
        expect(result).toEqual(mockResponse.tenants);
      });

      it('should return empty array on error', async () => {
        // Arrange
        (apiClient.get as jest.Mock).mockRejectedValue(new Error('Network error'));

        // Act
        const result = await AuthService.getUserTenants();

        // Assert
        expect(consoleErrorSpy).toHaveBeenCalledWith('Failed to fetch user tenants:', expect.any(Error));
        expect(result).toEqual([]);
      });
    });

    describe('switchTenant', () => {
      it('should switch to a different tenant', async () => {
        // Arrange
        const tenantId = 'tenant-2';
        const mockResponse = {
          success: true,
          token: 'new-tenant-token',
          refreshToken: 'new-tenant-refresh',
          user: { id: 'user-1' },
          tenant: { id: 'tenant-2', name: 'Tenant 2' },
        };

        (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.switchTenant(tenantId);

        // Assert
        expect(apiClient.post).toHaveBeenCalledWith('/auth/switch-tenant', { tenantId });
        expect(result).toEqual(mockResponse);
      });
    });

    describe('createTenant', () => {
      it('should create a new tenant', async () => {
        // Arrange
        const tenantData = {
          name: 'New Tenant',
          domain: 'new-tenant',
          plan: 'basic',
        };

        const mockTenant = {
          id: 'new-tenant-id',
          ...tenantData,
        };

        (apiClient.post as jest.Mock).mockResolvedValue(mockTenant);

        // Act
        const result = await AuthService.createTenant(tenantData);

        // Assert
        expect(apiClient.post).toHaveBeenCalledWith('/tenants', tenantData);
        expect(result).toEqual(mockTenant);
      });
    });
  });

  describe('Session Management', () => {
    describe('isAuthenticated', () => {
      it('should return true when user is authenticated', () => {
        // Arrange
        (localStorageMock.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'authToken') return 'valid-token';
          if (key === 'tenantId') return 'tenant-id';
          return null;
        });

        // Act
        const isAuth = AuthService.isAuthenticated();

        // Assert
        expect(isAuth).toBe(true);
      });

      it('should return false when access token is missing', () => {
        // Arrange
        (localStorageMock.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'tenantId') return 'tenant-id';
          return null;
        });

        // Act
        const isAuth = AuthService.isAuthenticated();

        // Assert
        expect(isAuth).toBe(false);
      });

      it('should return false when tenant ID is missing', () => {
        // Arrange
        (localStorageMock.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'authToken') return 'valid-token';
          return null;
        });

        // Act
        const isAuth = AuthService.isAuthenticated();

        // Assert
        expect(isAuth).toBe(false);
      });
    });

    describe('clearSession', () => {
      it('should clear all session data', () => {
        // Act
        AuthService.clearSession();

        // Assert
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('authToken');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('refreshToken');
        expect(localStorageMock.removeItem).toHaveBeenCalledWith('tenantId');
      });
    });
  });

  describe('Password Reset', () => {
    describe('resetPassword', () => {
      it('should request password reset', async () => {
        // Arrange
        const resetData: ResetPasswordRequest = {
          email: 'user@example.com',
        };

        const mockResponse = {
          success: true,
          message: 'Password reset email sent',
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.resetPassword(resetData);

        // Assert
        expect(apiClient.request).toHaveBeenCalledWith('/auth/reset-password', {
          method: 'POST',
          body: JSON.stringify(resetData),
        });
        expect(result).toEqual(mockResponse);
      });

      it('should handle reset password with token', async () => {
        // Arrange
        const resetData: ResetPasswordRequest = {
          token: 'reset-token',
          newPassword: 'newPassword123',
        };

        const mockResponse = {
          success: true,
          message: 'Password reset successfully',
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.resetPassword(resetData);

        // Assert
        expect(apiClient.request).toHaveBeenCalledWith('/auth/reset-password', {
          method: 'POST',
          body: JSON.stringify(resetData),
        });
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('User Invitations', () => {
    describe('inviteUser', () => {
      it('should invite a new user', async () => {
        // Arrange
        const inviteData = {
          email: 'newuser@example.com',
          firstName: 'New',
          lastName: 'User',
          role: 'viewer',
        };

        const mockResponse = {
          success: true,
          message: 'Invitation sent successfully',
        };

        (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.inviteUser(inviteData);

        // Assert
        expect(apiClient.post).toHaveBeenCalledWith('/auth/invite', inviteData);
        expect(result).toEqual(mockResponse);
      });
    });

    describe('acceptInvitation', () => {
      it('should accept user invitation', async () => {
        // Arrange
        const token = 'invitation-token';
        const userData = {
          password: 'password123',
          firstName: 'John',
          lastName: 'Doe',
        };

        const mockResponse = {
          success: true,
          token: 'access-token',
          refreshToken: 'refresh-token',
          user: {
            id: 'new-user-id',
            email: 'john@example.com',
            firstName: 'John',
            lastName: 'Doe',
          },
          tenant: {
            id: 'tenant-id',
            name: 'Test Tenant',
          },
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.acceptInvitation(token, userData);

        // Assert
        expect(apiClient.request).toHaveBeenCalledWith('/auth/accept-invitation', {
          method: 'POST',
          body: JSON.stringify({ token, ...userData }),
        });
        expect(result).toEqual(mockResponse);
      });
    });
  });

  describe('Validation', () => {
    describe('validateTenantDomain', () => {
      it('should validate available domain', async () => {
        // Arrange
        const domain = 'new-domain';
        const mockResponse = {
          available: true,
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.validateTenantDomain(domain);

        // Assert
        expect(apiClient.request).toHaveBeenCalledWith(`/auth/validate-domain?domain=${domain}`);
        expect(result.available).toBe(true);
      });

      it('should return suggestions for unavailable domain', async () => {
        // Arrange
        const domain = 'taken-domain';
        const mockResponse = {
          available: false,
          suggestions: ['taken-domain-1', 'taken-domain-2', 'my-taken-domain'],
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.validateTenantDomain(domain);

        // Assert
        expect(result.available).toBe(false);
        expect(result.suggestions).toEqual(['taken-domain-1', 'taken-domain-2', 'my-taken-domain']);
      });
    });

    describe('checkEmailExists', () => {
      it('should check if email exists', async () => {
        // Arrange
        const email = 'existing@example.com';
        const mockResponse = {
          exists: true,
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.checkEmailExists(email);

        // Assert
        expect(apiClient.request).toHaveBeenCalledWith(`/auth/check-email?email=${email}`);
        expect(result.exists).toBe(true);
      });

      it('should return false for non-existing email', async () => {
        // Arrange
        const email = 'new@example.com';
        const mockResponse = {
          exists: false,
        };

        (apiClient.request as jest.Mock).mockResolvedValue(mockResponse);

        // Act
        const result = await AuthService.checkEmailExists(email);

        // Assert
        expect(result.exists).toBe(false);
      });
    });
  });
});
