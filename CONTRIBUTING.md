# Contributing to Abbanoa Water Infrastructure Analytics Platform

Thank you for your interest in contributing to the Abbanoa Water Infrastructure Analytics Platform! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and professional environment. All contributions should focus on improving water infrastructure monitoring capabilities.

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Git
- Google Cloud SDK (for BigQuery access)
- Poetry for dependency management

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/abbanoa/water-infrastructure.git
   cd water-infrastructure
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   poetry shell
   ```

3. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run tests**:
   ```bash
   pytest tests/
   ```

## Development Workflow

### Branch Naming Conventions

- **Features**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-fix`
- **Documentation**: `docs/description-of-change`
- **Hotfixes**: `hotfix/critical-issue-description`

### Commit Message Guidelines

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(api): add anomaly detection endpoint
fix(dashboard): resolve data loading timeout issue
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following coding standards
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Run quality checks** (see Code Quality section)
6. **Submit pull request** with clear description

#### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No security vulnerabilities introduced
```

## Code Quality Standards

### Code Formatting

We use several tools to maintain code quality:

```bash
# Format code
black .
isort .

# Check style
flake8 .
pylint src/

# Type checking
mypy src/

# Security scanning
bandit -r src/
safety check
```

### Testing Requirements

- **Unit tests**: Required for all new functions and classes
- **Integration tests**: Required for API endpoints and database operations
- **Coverage**: Minimum 85% code coverage
- **Performance tests**: Required for critical paths

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

### Code Style Guidelines

#### Python Style

- **PEP 8 compliance**: Follow Python Enhancement Proposal 8
- **Line length**: Maximum 120 characters
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Required for all public functions

#### Example Function

```python
from typing import List, Optional
from datetime import datetime

def calculate_network_efficiency(
    node_ids: List[str],
    start_time: datetime,
    end_time: Optional[datetime] = None
) -> float:
    """Calculate network efficiency for given nodes.
    
    Args:
        node_ids: List of monitoring node identifiers
        start_time: Start of analysis period
        end_time: End of analysis period, defaults to now
        
    Returns:
        Network efficiency score between 0.0 and 1.0
        
    Raises:
        ValueError: If node_ids is empty or invalid time range
    """
    # Implementation here
    pass
```

#### Database Guidelines

- **Migrations**: Use Alembic for database schema changes
- **Queries**: Use parameterized queries to prevent SQL injection
- **Transactions**: Wrap related operations in transactions
- **Indexes**: Add appropriate indexes for query performance

#### API Guidelines

- **RESTful design**: Follow REST principles
- **Versioning**: Use URL versioning (e.g., `/api/v1/`)
- **Error handling**: Return appropriate HTTP status codes
- **Documentation**: Use OpenAPI/Swagger specifications
- **Authentication**: Implement proper JWT validation

## Architecture Guidelines

### Domain-Driven Design

The project follows DDD principles:

- **Entities**: Core business objects with identity
- **Value Objects**: Immutable objects without identity
- **Aggregates**: Consistency boundaries for entities
- **Services**: Domain logic that doesn't belong to entities
- **Repositories**: Data access abstraction

### Layer Separation

```
src/
├── domain/          # Core business logic
├── application/     # Use cases and application services
├── infrastructure/  # External services and data access
└── presentation/    # User interfaces (API, UI)
```

### Dependency Rules

- **Inward dependencies only**: Inner layers never depend on outer layers
- **Dependency injection**: Use DI container for managing dependencies
- **Interface segregation**: Define interfaces for external dependencies

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests with external dependencies
├── e2e/           # End-to-end user scenarios
└── performance/   # Load and performance tests
```

### Test Naming

```python
def test_should_calculate_efficiency_when_valid_data_provided():
    """Test that efficiency calculation works with valid input data."""
    # Arrange
    # Act
    # Assert
```

### Test Data

- **Factory Boy**: Use for creating test objects
- **Fixtures**: Use pytest fixtures for common setup
- **Test Database**: Use separate test database
- **Mock External Services**: Mock BigQuery, Redis, etc.

## Documentation Standards

### Code Documentation

- **Docstrings**: Required for all public classes and functions
- **Type hints**: Required for all function parameters and returns
- **Comments**: Explain complex business logic, not implementation details
- **Architecture Decision Records**: Document significant architectural choices

### User Documentation

- **README**: Keep updated with current installation and usage
- **API Documentation**: Maintain OpenAPI specifications
- **Changelog**: Document all changes affecting users
- **Migration Guides**: Provide upgrade instructions

## Security Guidelines

### General Security

- **No secrets in code**: Use environment variables or secret management
- **Input validation**: Validate all user inputs
- **SQL injection**: Use parameterized queries
- **Authentication**: Implement proper JWT validation
- **Authorization**: Check user permissions for all operations

### Data Security

- **Encryption at rest**: Sensitive data must be encrypted
- **Encryption in transit**: Use HTTPS/TLS for all communications
- **Data anonymization**: Remove PII from analytics datasets
- **Audit logging**: Log all data access and modifications

## Performance Guidelines

### Database Performance

- **Query optimization**: Use EXPLAIN to analyze query performance
- **Indexing**: Add indexes for frequently queried columns
- **Connection pooling**: Use connection pools for database access
- **Batch operations**: Use bulk operations for multiple records

### API Performance

- **Response times**: Target <50ms for simple queries
- **Caching**: Use Redis for frequently accessed data
- **Pagination**: Implement pagination for large datasets
- **Rate limiting**: Implement rate limiting to prevent abuse

### Monitoring

- **Metrics**: Monitor response times, error rates, resource usage
- **Alerting**: Set up alerts for performance degradation
- **Profiling**: Use profiling tools to identify bottlenecks

## Release Process

### Version Numbering

We use semantic versioning (SemVer):
- **MAJOR**: Incompatible API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. **Update version** in pyproject.toml
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite** and ensure all tests pass
4. **Update documentation** if needed
5. **Create release tag** and push to repository
6. **Deploy to staging** and perform smoke tests
7. **Deploy to production** with monitoring

### Hotfix Process

For critical production issues:

1. **Create hotfix branch** from main
2. **Apply minimal fix** with tests
3. **Fast-track review** with minimal approvals
4. **Deploy immediately** after testing
5. **Backport to develop** branch

## Getting Help

### Resources

- **Documentation**: [docs/](./docs/) directory
- **Architecture**: [docs/ARCHITECTURE_COMPLETE.md](./docs/ARCHITECTURE_COMPLETE.md)
- **API Reference**: [docs/API_REFERENCE.md](./docs/API_REFERENCE.md)

### Communication

- **GitHub Issues**: For bug reports and feature requests
- **Pull Request Reviews**: For code discussions
- **Team Chat**: For quick questions and coordination
- **Technical Support**: tech-support@abbanoa.it

### Code Review Process

- **Automated checks**: All PRs must pass CI/CD pipeline
- **Peer review**: At least one team member must review
- **Domain expert review**: For domain-specific changes
- **Security review**: For security-related changes

## Recognition

Contributors who make significant improvements to the platform may be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for major contributions
- **Team acknowledgments** in presentations

Thank you for contributing to improving water infrastructure monitoring in Sardinia!

---

*This contributing guide is subject to updates. Please check the latest version before starting work.*