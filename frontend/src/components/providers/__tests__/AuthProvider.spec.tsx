import React from 'react';
import { render, screen, renderHook } from '@testing-library/react';
import '@testing-library/jest-dom';
import { AuthProvider, useAuthContext, useAuth } from '../AuthProvider';
import { useAuth as useAuthHook } from '@/lib/hooks/useAuth';

// Mock dependencies
jest.mock('@/lib/hooks/useAuth');

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  key: jest.fn(),
  length: 0,
};
Object.defineProperty(window, 'sessionStorage', {
  value: sessionStorageMock,
  writable: true,
});

describe('AuthProvider', () => {
  const mockAuthHook = {
    isAuthenticated: false,
    isLoading: false,
    user: null,
    tenant: null,
    error: null,
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    updateProfile: jest.fn(),
    changePassword: jest.fn(),
    switchTenant: jest.fn(),
    clearError: jest.fn(),
    refreshAuth: jest.fn(),
  };

  let consoleLogSpy: jest.SpyInstance;

  beforeEach(() => {
    jest.clearAllMocks();
    consoleLogSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    (useAuthHook as jest.Mock).mockReturnValue(mockAuthHook);
    sessionStorageMock.getItem.mockReturnValue(null);
  });

  afterEach(() => {
    consoleLogSpy.mockRestore();
  });

  describe('Provider functionality', () => {
    it('should render children when used', () => {
      render(
        <AuthProvider>
          <div>Test Child</div>
        </AuthProvider>
      );

      expect(screen.getByText('Test Child')).toBeInTheDocument();
    });

    it('should provide auth context values', () => {
      const TestComponent = () => {
        const auth = useAuthContext();
        return (
          <div>
            <div>Authenticated: {auth.isAuthenticated ? 'Yes' : 'No'}</div>
            <div>Loading: {auth.isLoading ? 'Yes' : 'No'}</div>
          </div>
        );
      };

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      expect(screen.getByText('Authenticated: No')).toBeInTheDocument();
      expect(screen.getByText('Loading: No')).toBeInTheDocument();
    });

    it('should pass through all auth methods', () => {
      const TestComponent = () => {
        const auth = useAuthContext();
        
        React.useEffect(() => {
          // Call all methods to ensure they're passed through
          auth.login({ email: 'test@example.com', password: 'password' });
          auth.register({ email: 'test@example.com', password: 'password' });
          auth.logout();
          auth.updateProfile({ firstName: 'Test' });
          auth.changePassword({ currentPassword: 'old', newPassword: 'new' });
          auth.switchTenant('tenant-2');
          auth.clearError();
          auth.refreshAuth();
        }, [auth]);

        return <div>Test</div>;
      };

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      expect(mockAuthHook.login).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password' });
      expect(mockAuthHook.register).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password' });
      expect(mockAuthHook.logout).toHaveBeenCalled();
      expect(mockAuthHook.updateProfile).toHaveBeenCalledWith({ firstName: 'Test' });
      expect(mockAuthHook.changePassword).toHaveBeenCalledWith({ currentPassword: 'old', newPassword: 'new' });
      expect(mockAuthHook.switchTenant).toHaveBeenCalledWith('tenant-2');
      expect(mockAuthHook.clearError).toHaveBeenCalled();
      expect(mockAuthHook.refreshAuth).toHaveBeenCalled();
    });
  });

  describe('useAuthContext hook', () => {
    it('should throw error when used outside AuthProvider', () => {
      const { result } = renderHook(() => {
        try {
          return useAuthContext();
        } catch (error) {
          return error;
        }
      });

      expect(result.current).toEqual(
        new Error('useAuthContext must be used within AuthProvider')
      );
    });

    it('should return auth context when used within AuthProvider', () => {
      const wrapper = ({ children }: { children: React.ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      expect(result.current).toEqual(mockAuthHook);
    });
  });

  describe('useAuth alias', () => {
    it('should be an alias for useAuthContext', () => {
      expect(useAuth).toBe(useAuthContext);
    });
  });

  describe('Development auto-login', () => {
    const originalEnv = process.env.NODE_ENV;

    beforeEach(() => {
      process.env.NODE_ENV = 'development';
    });

    afterEach(() => {
      process.env.NODE_ENV = originalEnv;
    });

    it('should attempt auto-login in development mode when not authenticated', () => {
      render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      expect(consoleLogSpy).toHaveBeenCalledWith('🔧 Development auto-login...');
      expect(mockAuthHook.login).toHaveBeenCalledWith({
        email: 'admin@roccavina.com',
        password: 'admin123',
      });
      expect(sessionStorageMock.setItem).toHaveBeenCalledWith('dev_auto_login_tried', 'true');
    });

    it('should not attempt auto-login if already authenticated', () => {
      (useAuthHook as jest.Mock).mockReturnValue({
        ...mockAuthHook,
        isAuthenticated: true,
      });

      render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      expect(mockAuthHook.login).not.toHaveBeenCalled();
    });

    it('should not attempt auto-login if loading', () => {
      (useAuthHook as jest.Mock).mockReturnValue({
        ...mockAuthHook,
        isLoading: true,
      });

      render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      expect(mockAuthHook.login).not.toHaveBeenCalled();
    });

    it('should not attempt auto-login if already tried in session', () => {
      sessionStorageMock.getItem.mockReturnValue('true');

      render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      expect(mockAuthHook.login).not.toHaveBeenCalled();
    });

    it('should handle auto-login errors gracefully', async () => {
      const mockError = new Error('Login failed');
      mockAuthHook.login.mockRejectedValue(mockError);

      render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      // Wait for the async operation
      await new Promise(resolve => setTimeout(resolve, 0));

      expect(consoleLogSpy).toHaveBeenCalledWith('🔧 Dev auto-login skipped:', mockError);
    });

    it('should not attempt auto-login in production mode', () => {
      process.env.NODE_ENV = 'production';

      render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      expect(mockAuthHook.login).not.toHaveBeenCalled();
    });
  });

  describe('Auth state changes', () => {
    it('should update when auth state changes', () => {
      const { rerender } = render(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      // Update the mock to return authenticated state
      (useAuthHook as jest.Mock).mockReturnValue({
        ...mockAuthHook,
        isAuthenticated: true,
        user: { id: '1', email: 'test@example.com', role: 'admin' },
        tenant: { id: 'tenant-1', name: 'Test Tenant' },
      });

      rerender(
        <AuthProvider>
          <div>Test</div>
        </AuthProvider>
      );

      // The component should re-render with new auth state
      const TestComponent = () => {
        const auth = useAuthContext();
        return <div>Authenticated: {auth.isAuthenticated ? 'Yes' : 'No'}</div>;
      };

      const { container } = render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      expect(container.textContent).toContain('Authenticated: Yes');
    });
  });
});
