# Migration Guide - v0.x to v1.0.0

This guide helps you migrate from the legacy script-based architecture to the new Domain-Driven Design structure.

## Overview of Changes

The project has been completely restructured following DDD and clean architecture principles. The main changes include:

1. **Project Structure**: From flat script files to layered architecture
2. **Data Models**: From DataFrames to domain entities
3. **Dependencies**: From direct imports to dependency injection
4. **Entry Points**: New CLI, API, and web interfaces

## Step-by-Step Migration

### 1. Backup Current Work

```bash
# Create a backup of your current setup
cp -r /path/to/current/project /path/to/backup
```

### 2. Update Dependencies

```bash
# Remove old virtual environment
rm -rf venv/

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install new dependencies
poetry install
```

### 3. Run Migration Script

```bash
# This moves legacy files to a 'legacy' directory
poetry run python scripts/migrate_existing_code.py
```

### 4. Update Configuration

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Update with your settings:
```env
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_DATASET_ID=water_infrastructure
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

### 5. Update Import Statements

#### Old Style
```python
from data_normalizer import WaterDataNormalizer
from bigquery_pipeline import BigQueryPipeline
import pandas as pd
```

#### New Style
```python
from src.infrastructure.normalization.selargius_normalizer import SelargiusDataNormalizer
from src.domain.entities.sensor_reading import SensorReading
from src.application.use_cases.analyze_consumption_patterns import AnalyzeConsumptionPatternsUseCase
```

### 6. Replace DataFrame Operations

#### Old Style
```python
# Direct DataFrame manipulation
df = pd.read_csv('data.csv')
flow_rate = df['flow_rate'].mean()
```

#### New Style
```python
# Using domain entities
normalizer = SelargiusDataNormalizer()
nodes, readings, quality = normalizer.normalize_file('data.csv')

# Using use cases
use_case = container.analyze_consumption_patterns_use_case()
result = await use_case.execute(node_id, start_date, end_date)
```

### 7. Update Scripts and Automation

#### Old Dashboard Launch
```bash
streamlit run streamlit_dashboard.py
```

#### New Dashboard Launch
```bash
poetry run streamlit run src/presentation/web/dashboard.py
```

#### Old Data Processing
```python
python bigquery_pipeline.py --input data.csv
```

#### New Data Processing
```bash
poetry run python -m src.presentation.cli.main normalize data.csv -o output
```

### 8. API Integration

The new system provides a REST API for programmatic access:

```python
# Old: Direct script execution
import subprocess
subprocess.run(['python', 'analyze_quality.py', 'data.csv'])

# New: API calls
import requests
response = requests.post(
    'http://localhost:8000/api/v1/anomalies/detect',
    json={'time_window_hours': 24}
)
```

## Common Migration Scenarios

### Scenario 1: Scheduled Data Import

**Old Approach:**
```bash
# Cron job
0 * * * * cd /project && python bigquery_pipeline.py
```

**New Approach:**
```bash
# Cron job
0 * * * * cd /project && poetry run python -m src.presentation.cli.main normalize /data/latest.csv
```

### Scenario 2: Custom Analysis Scripts

**Old Approach:**
```python
# custom_analysis.py
import pandas as pd
from improved_normalizer import ImprovedWaterDataNormalizer

normalizer = ImprovedWaterDataNormalizer()
results = normalizer.analyze_and_normalize('data.csv')
```

**New Approach:**
```python
# custom_analysis.py
from src.infrastructure.di_container import Container
from datetime import datetime, timedelta

# Initialize container
container = Container()
container.config.from_dict({...})

# Use the use case
use_case = container.analyze_consumption_patterns_use_case()
result = await use_case.execute(
    node_id=node_id,
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now()
)
```

### Scenario 3: BigQuery Integration

**Old Approach:**
```python
from bigquery_pipeline import BigQueryPipeline
pipeline = BigQueryPipeline(project_id, dataset_id)
pipeline.run_pipeline(['file1.csv', 'file2.csv'])
```

**New Approach:**
```python
from src.infrastructure.external_services.bigquery_service import BigQueryService
from src.infrastructure.persistence.bigquery_config import BigQueryConfig

config = BigQueryConfig(
    project_id=project_id,
    dataset_id=dataset_id
)
service = BigQueryService(config)
# Use repository pattern for data operations
```

## Testing Your Migration

1. **Run Unit Tests**
   ```bash
   poetry run pytest tests/unit
   ```

2. **Verify Data Import**
   ```bash
   poetry run python -m src.presentation.cli.main normalize sample_data.csv --dry-run
   ```

3. **Check Dashboard**
   ```bash
   poetry run streamlit run src/presentation/web/dashboard.py
   ```

4. **Test API**
   ```bash
   poetry run uvicorn src.presentation.api.app:app
   # Visit http://localhost:8000/docs
   ```

## Rollback Plan

If you encounter issues:

1. The legacy code is preserved in the `legacy/` directory
2. You can still run old scripts: `python legacy/script_name.py`
3. Restore from backup if needed

## Getting Help

- Check the architecture documentation: `docs/architecture/overview.md`
- Review the README for updated usage instructions
- Submit issues on GitHub for migration problems

## Benefits After Migration

1. **Better Maintainability**: Clear separation of concerns
2. **Improved Testing**: Isolated components with dependency injection
3. **Type Safety**: Full type hints and validation
4. **Scalability**: Easy to add new features without breaking existing code
5. **Multiple Interfaces**: CLI, API, and web dashboard
6. **Better Documentation**: Self-documenting code with clear domain models