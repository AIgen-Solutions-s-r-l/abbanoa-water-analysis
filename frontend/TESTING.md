# Frontend Testing Guide

## Overview

This guide provides information about testing in the Abbanoa Water Analysis frontend application.

## Test Structure

Tests are organized following the protocol's naming conventions:
- **Unit tests**: `*.spec.{js,jsx,ts,tsx}`
- **Integration tests**: `*.int.{js,jsx,ts,tsx}`
- **E2E tests**: `*.e2e.{js,jsx,ts,tsx}`

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run tests with coverage in watch mode
npm run test:coverage:watch

# Run specific test types
npm run test:unit    # Unit tests only
npm run test:int     # Integration tests only
npm run test:e2e     # E2E tests only

# Run tests for CI/CD
npm run test:coverage:ci
```

## Coverage Goals

### Current Thresholds (Temporary)
- Lines: 15%
- Branches: 10%
- Functions: 10%
- Statements: 15%

### Target Thresholds
- Lines: 90%
- Branches: 80%
- Functions: 90%
- Statements: 90%

**Note**: Current thresholds are set low to allow the CI/CD pipeline to pass while tests are being incrementally added. These should be gradually increased as coverage improves.

## Coverage Reports

After running tests with coverage, you can view detailed reports:

1. **Terminal Output**: Shows coverage summary
2. **HTML Report**: Open `coverage/lcov-report/index.html` in a browser
3. **JSON Summary**: Available at `coverage/coverage-summary.json`

## Test Writing Guidelines

### 1. Follow AAA Pattern
```typescript
it('should do something', () => {
  // Arrange
  const input = 'test';
  
  // Act
  const result = functionUnderTest(input);
  
  // Assert
  expect(result).toBe('expected');
});
```

### 2. Use Descriptive Test Names
```typescript
describe('AuthService', () => {
  describe('login', () => {
    it('should successfully authenticate a user with valid credentials', async () => {
      // test implementation
    });
    
    it('should return error when credentials are invalid', async () => {
      // test implementation
    });
  });
});
```

### 3. Mock External Dependencies
```typescript
// Mock API calls
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));
```

### 4. Test User Interactions
```typescript
it('should update state when button is clicked', async () => {
  render(<Component />);
  
  const button = screen.getByRole('button', { name: /submit/i });
  fireEvent.click(button);
  
  await waitFor(() => {
    expect(screen.getByText('Success')).toBeInTheDocument();
  });
});
```

## Areas Needing Tests

Based on current coverage report, the following areas need tests:

### High Priority (Core functionality)
1. **API Routes** (`app/api/proxy/[...path]/route.ts`)
2. **Authentication Components** (`components/auth/ProtectedRoute.tsx`)
3. **Layout Components** (`components/layout/*`)
4. **Dashboard Services** (`services/dashboard.service.ts`)

### Medium Priority (Feature pages)
1. **Admin Page** (`app/admin/page.tsx`)
2. **Analytics Page** (`app/analytics/page.tsx`)
3. **Consumption Page** (`app/consumption/page.tsx`)
4. **Infrastructure Map** (`app/infrastructure-map/page.tsx`)

### Low Priority (Static/simple pages)
1. **About Page** (`app/about/page.tsx`)
2. **Settings Page** (`app/settings/page.tsx`)
3. **Profile Page** (`app/profile/page.tsx`)

## Gradual Coverage Improvement Plan

1. **Phase 1 (Current)**: 15% coverage
   - Basic tests for critical components
   - Integration tests for auth service
   - Unit tests for weather and enhanced-overview pages

2. **Phase 2**: 30% coverage
   - Add tests for all services
   - Test authentication flow components
   - Test layout components

3. **Phase 3**: 50% coverage
   - Add tests for dashboard components
   - Test remaining utility functions
   - Integration tests for API routes

4. **Phase 4**: 70% coverage
   - Test all page components
   - Add error scenario tests
   - Performance-critical path tests

5. **Phase 5**: 90% coverage (Target)
   - Complete test coverage for all components
   - Edge case testing
   - Mutation testing implementation

## CI/CD Integration

The GitHub Actions workflow automatically:
- Runs tests on push/PR to main/develop branches
- Checks coverage thresholds
- Posts coverage report as PR comment
- Archives test results and coverage reports
- Fails the build if thresholds are not met

## Best Practices

1. **Write tests alongside new features** - Don't accumulate technical debt
2. **Test behavior, not implementation** - Focus on what the component does
3. **Keep tests simple and focused** - One assertion per test when possible
4. **Use meaningful test data** - Avoid "test", "foo", "bar"
5. **Clean up after tests** - Reset mocks, clear timers, etc.

## Mutation Testing

Future implementation will use Stryker for mutation testing with a minimum score of 60%.

```bash
# Future command (not yet implemented)
npm run test:mutation
```

## Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
