import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { useRouter } from 'next/navigation';
import { ProtectedRoute, withAuth, usePermissions } from '../ProtectedRoute';
import { useAuthContext } from '@/components/providers/AuthProvider';

// Mock dependencies
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/components/providers/AuthProvider', () => ({
  useAuthContext: jest.fn(),
}));

describe('ProtectedRoute', () => {
  const mockPush = jest.fn();
  const mockBack = jest.fn();
  const mockRouter = {
    push: mockPush,
    back: mockBack,
  };

  const defaultAuthContext = {
    isAuthenticated: true,
    isLoading: false,
    user: {
      id: 'user-1',
      email: 'test@example.com',
      role: 'admin',
    },
    tenant: {
      id: 'tenant-1',
      name: 'Test Tenant',
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useAuthContext as jest.Mock).mockReturnValue(defaultAuthContext);
  });

  describe('Loading state', () => {
    it('should show loading screen when isLoading is true', () => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isLoading: true,
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });

  describe('Authentication check', () => {
    it('should redirect to login when not authenticated', () => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        isAuthenticated: false,
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      // The test environment has window.location.pathname as '/'
      expect(mockPush).toHaveBeenCalledWith('/auth/login?redirect=%2F');
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should show content when authenticated', () => {
      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
      expect(mockPush).not.toHaveBeenCalled();
    });

    it('should show unauthorized screen when user is missing', () => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        user: null,
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Access Denied')).toBeInTheDocument();
      expect(screen.getByText(/User or organization information is missing/)).toBeInTheDocument();
    });

    it('should show unauthorized screen when tenant is missing', () => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        tenant: null,
      });

      render(
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Access Denied')).toBeInTheDocument();
      expect(screen.getByText(/User or organization information is missing/)).toBeInTheDocument();
    });
  });

  describe('Role-based access control', () => {
    it('should allow access when user has required role', () => {
      render(
        <ProtectedRoute requiredRole="operator">
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('should deny access when user lacks required role', () => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        user: {
          ...defaultAuthContext.user,
          role: 'viewer',
        },
      });

      render(
        <ProtectedRoute requiredRole="admin">
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Access Denied')).toBeInTheDocument();
      expect(screen.getByText(/This page requires admin access. You currently have viewer access/)).toBeInTheDocument();
    });

    it('should show custom fallback when provided and access denied', () => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        user: {
          ...defaultAuthContext.user,
          role: 'viewer',
        },
      });

      render(
        <ProtectedRoute 
          requiredRole="admin"
          fallback={<div>Custom Unauthorized Message</div>}
        >
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Custom Unauthorized Message')).toBeInTheDocument();
      expect(screen.queryByText('Access Denied')).not.toBeInTheDocument();
    });

    it('should respect role hierarchy', () => {
      const testCases = [
        { userRole: 'super_admin', requiredRole: 'admin', shouldAllow: true },
        { userRole: 'admin', requiredRole: 'operator', shouldAllow: true },
        { userRole: 'operator', requiredRole: 'viewer', shouldAllow: true },
        { userRole: 'viewer', requiredRole: 'operator', shouldAllow: false },
        { userRole: 'operator', requiredRole: 'admin', shouldAllow: false },
      ];

      testCases.forEach(({ userRole, requiredRole, shouldAllow }) => {
        (useAuthContext as jest.Mock).mockReturnValue({
          ...defaultAuthContext,
          user: {
            ...defaultAuthContext.user,
            role: userRole,
          },
        });

        const { rerender } = render(
          <ProtectedRoute requiredRole={requiredRole as any}>
            <div>Protected Content</div>
          </ProtectedRoute>
        );

        if (shouldAllow) {
          expect(screen.getByText('Protected Content')).toBeInTheDocument();
        } else {
          expect(screen.getByText('Access Denied')).toBeInTheDocument();
        }

        rerender(<></>); // Clean up for next iteration
      });
    });
  });

  describe('Permission-based access control', () => {
    it('should allow super_admin all permissions', () => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        user: {
          ...defaultAuthContext.user,
          role: 'super_admin',
        },
      });

      render(
        <ProtectedRoute requiredPermissions={[{ resource: 'system', action: 'manage' }]}>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Protected Content')).toBeInTheDocument();
    });

    it('should deny admin system management permission', () => {
      render(
        <ProtectedRoute requiredPermissions={[{ resource: 'system', action: 'manage' }]}>
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      expect(screen.getByText('Access Denied')).toBeInTheDocument();
      expect(screen.getByText(/You don't have the required permissions/)).toBeInTheDocument();
    });
  });

  describe('UnauthorizedScreen interactions', () => {
    beforeEach(() => {
      (useAuthContext as jest.Mock).mockReturnValue({
        ...defaultAuthContext,
        user: {
          ...defaultAuthContext.user,
          role: 'viewer',
        },
      });
    });

    it('should navigate back when Go Back button is clicked', () => {
      render(
        <ProtectedRoute requiredRole="admin">
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      const goBackButton = screen.getByText('Go Back');
      fireEvent.click(goBackButton);

      expect(mockBack).toHaveBeenCalled();
    });

    it('should navigate to home when Go Home button is clicked', () => {
      render(
        <ProtectedRoute requiredRole="admin">
          <div>Protected Content</div>
        </ProtectedRoute>
      );

      const goHomeButton = screen.getByText('Go Home');
      fireEvent.click(goHomeButton);

      expect(mockPush).toHaveBeenCalledWith('/');
    });
  });
});

describe('withAuth HOC', () => {
  const mockPush = jest.fn();
  const mockRouter = { push: mockPush, back: jest.fn() };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useAuthContext as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { id: 'user-1', role: 'admin' },
      tenant: { id: 'tenant-1' },
    });
  });

  it('should wrap component with ProtectedRoute', () => {
    const TestComponent = () => <div>Test Component</div>;
    const ProtectedComponent = withAuth(TestComponent);

    render(<ProtectedComponent />);

    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });

  it('should pass requiredRole to ProtectedRoute', () => {
    const TestComponent = () => <div>Test Component</div>;
    const ProtectedComponent = withAuth(TestComponent, 'super_admin');

    (useAuthContext as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      isLoading: false,
      user: { id: 'user-1', role: 'admin' },
      tenant: { id: 'tenant-1' },
    });

    render(<ProtectedComponent />);

    expect(screen.getByText('Access Denied')).toBeInTheDocument();
  });

  it('should pass props to wrapped component', () => {
    interface TestProps {
      message: string;
    }
    const TestComponent = ({ message }: TestProps) => <div>{message}</div>;
    const ProtectedComponent = withAuth(TestComponent);

    render(<ProtectedComponent message="Hello World" />);

    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});

describe('usePermissions hook', () => {
  const TestComponent = () => {
    const { hasRole, hasPermission, canAccess, userRole } = usePermissions();
    
    return (
      <div>
        <div>User Role: {userRole}</div>
        <div>Has Admin Role: {hasRole('admin') ? 'Yes' : 'No'}</div>
        <div>Has Super Admin Role: {hasRole('super_admin') ? 'Yes' : 'No'}</div>
        <div>Can Manage System: {hasPermission('system', 'manage') ? 'Yes' : 'No'}</div>
        <div>Can Access Admin: {canAccess('admin') ? 'Yes' : 'No'}</div>
      </div>
    );
  };

  it('should return correct permissions for admin user', () => {
    (useAuthContext as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      user: { id: 'user-1', role: 'admin' },
    });

    render(<TestComponent />);

    expect(screen.getByText('User Role: admin')).toBeInTheDocument();
    expect(screen.getByText('Has Admin Role: Yes')).toBeInTheDocument();
    expect(screen.getByText('Has Super Admin Role: No')).toBeInTheDocument();
    expect(screen.getByText('Can Manage System: No')).toBeInTheDocument();
    expect(screen.getByText('Can Access Admin: Yes')).toBeInTheDocument();
  });

  it('should return false for all checks when not authenticated', () => {
    (useAuthContext as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
    });

    render(<TestComponent />);

    expect(screen.getByText('User Role:')).toBeInTheDocument();
    expect(screen.getByText('Has Admin Role: No')).toBeInTheDocument();
    expect(screen.getByText('Has Super Admin Role: No')).toBeInTheDocument();
    expect(screen.getByText('Can Manage System: No')).toBeInTheDocument();
    expect(screen.getByText('Can Access Admin: No')).toBeInTheDocument();
  });

  it('should return correct permissions for super_admin user', () => {
    (useAuthContext as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      user: { id: 'user-1', role: 'super_admin' },
    });

    render(<TestComponent />);

    expect(screen.getByText('User Role: super_admin')).toBeInTheDocument();
    expect(screen.getByText('Has Admin Role: Yes')).toBeInTheDocument();
    expect(screen.getByText('Has Super Admin Role: Yes')).toBeInTheDocument();
    expect(screen.getByText('Can Manage System: Yes')).toBeInTheDocument();
  });

  it('should check combined role and permission requirements', () => {
    const TestComponentWithCombined = () => {
      const { canAccess } = usePermissions();
      const canAccessWithBoth = canAccess('admin', [{ resource: 'users', action: 'write' }]);
      
      return <div>Can Access With Both: {canAccessWithBoth ? 'Yes' : 'No'}</div>;
    };

    (useAuthContext as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      user: { id: 'user-1', role: 'admin' },
    });

    render(<TestComponentWithCombined />);

    expect(screen.getByText('Can Access With Both: Yes')).toBeInTheDocument();
  });
});