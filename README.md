# Abbanoa Water Infrastructure Monitoring System

A comprehensive water infrastructure monitoring and analysis system built using Domain-Driven Design (DDD) and clean architecture principles.

## 🏗️ Architecture Overview

This project follows Domain-Driven Design with clean architecture, organizing code into distinct layers:

```
src/
├── domain/           # Core business logic and entities
├── application/      # Use cases and application services
├── infrastructure/   # External services and data persistence
└── presentation/     # User interfaces (Web, CLI, API)
```

### Key Architectural Principles

- **Domain-Driven Design**: Core business logic is isolated in the domain layer
- **Clean Architecture**: Dependencies flow inward (presentation → application → domain)
- **Repository Pattern**: Data access is abstracted behind interfaces
- **Dependency Injection**: Loose coupling between components
- **Event-Driven**: Domain events for decoupled communication

## 🚀 Features

- **Real-time Monitoring**: Track water flow, pressure, and temperature across the network
- **Anomaly Detection**: Statistical analysis to identify unusual patterns
- **Consumption Analysis**: Hourly, daily, weekly, and monthly consumption patterns
- **Network Efficiency**: Calculate water loss and identify potential leakage zones
- **Multiple Interfaces**: Web dashboard, CLI tools, and REST API

## 📋 Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Google Cloud SDK (for BigQuery integration)
- Docker (optional, for containerized deployment)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/AIgen-Solutions-s-r-l/abbanoa-water-analysis.git
cd abbanoa-water-analysis
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Configure BigQuery credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

## 🎯 Quick Start

### Web Dashboard

Launch the interactive Streamlit dashboard:

```bash
poetry run streamlit run src/presentation/web/dashboard.py
```

Access the dashboard at `http://localhost:8501`

### CLI Usage

The CLI provides various commands for data management and analysis:

```bash
# Normalize sensor data
poetry run python -m src.presentation.cli.main normalize data/sensors.csv -o normalized_data

# Detect anomalies
poetry run python -m src.presentation.cli.main detect-anomalies --hours 24

# Analyze consumption patterns
poetry run python -m src.presentation.cli.main analyze-consumption --node-id NODE_ID --pattern daily

# Calculate network efficiency
poetry run python -m src.presentation.cli.main calculate-efficiency --network-id NETWORK_ID
```

### REST API

Start the FastAPI server:

```bash
poetry run uvicorn src.presentation.api.app:app --reload
```

API documentation available at `http://localhost:8000/docs`

## 📁 Project Structure

```
.
├── src/
│   ├── domain/               # Core business domain
│   │   ├── entities/         # Domain entities (SensorReading, MonitoringNode, etc.)
│   │   ├── value_objects/    # Value objects (Measurements, Location, etc.)
│   │   ├── events/           # Domain events
│   │   ├── exceptions/       # Domain-specific exceptions
│   │   └── services/         # Domain services
│   │
│   ├── application/          # Application layer
│   │   ├── use_cases/        # Business use cases
│   │   ├── interfaces/       # Repository and service interfaces
│   │   └── dto/              # Data transfer objects
│   │
│   ├── infrastructure/       # Infrastructure layer
│   │   ├── repositories/     # Repository implementations
│   │   ├── persistence/      # Database configurations
│   │   ├── external_services/# Third-party integrations
│   │   └── normalization/    # Data normalization services
│   │
│   └── presentation/         # Presentation layer
│       ├── web/              # Streamlit dashboard
│       ├── cli/              # Command-line interface
│       └── api/              # REST API
│
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
│
├── docs/                     # Documentation
├── scripts/                  # Utility scripts
└── config/                   # Configuration files
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test categories
poetry run pytest tests/unit
poetry run pytest tests/integration
```

## 🔧 Development

### Setting up pre-commit hooks:

```bash
poetry run pre-commit install
```

### Code formatting and linting:

```bash
# Format code
poetry run black src tests

# Sort imports
poetry run isort src tests

# Run linters
poetry run flake8 src tests
poetry run mypy src

# Run all checks
make quality
```

### Building documentation:

```bash
poetry run sphinx-build -b html docs docs/_build/html
```

## 📊 Data Model

### Core Entities

- **SensorReading**: Time-series measurements from sensors
- **MonitoringNode**: Physical locations with sensors
- **WaterNetwork**: Collection of interconnected nodes

### Key Measurements

- **Flow Rate** (L/s): Instantaneous water flow
- **Pressure** (bar): Water pressure in the pipes
- **Temperature** (°C): Water temperature
- **Volume** (m³): Total water volume

## 🚢 Deployment

### Docker

Build and run using Docker:

```bash
docker build -t abbanoa-water-infrastructure .
docker run -p 8501:8501 -p 8000:8000 abbanoa-water-infrastructure
```

### Google Cloud Platform

Deploy to GCP App Engine:

```bash
gcloud app deploy
```

## 📈 Monitoring

The system provides several monitoring capabilities:

- Real-time dashboard with key metrics
- Anomaly alerts via email/SMS
- Daily/weekly/monthly reports
- BigQuery views for custom analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

We follow conventional commits:

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test updates
- `chore`: Build/config updates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Architecture**: Domain-Driven Design implementation
- **Backend**: Python, FastAPI, BigQuery
- **Frontend**: Streamlit, Plotly
- **Infrastructure**: Google Cloud Platform

## 📞 Support

For support and questions:

- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation in the `docs/` directory

---

Built with ❤️ by AIgen Solutions s.r.l.