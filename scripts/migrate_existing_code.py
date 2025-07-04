#!/usr/bin/env python3
"""Script to migrate existing code to the new DDD structure."""

import shutil
from pathlib import Path
from typing import Dict, List


def create_migration_mapping() -> Dict[str, str]:
    """Create mapping of old files to new locations."""
    return {
        # Data normalization
        "data_normalizer.py": "legacy/data_normalizer.py",
        "improved_normalizer.py": "legacy/improved_normalizer.py",
        "hidroconta_normalizer.py": "legacy/hidroconta_normalizer.py",
        
        # BigQuery pipeline
        "bigquery_pipeline.py": "legacy/bigquery_pipeline.py",
        "bigquery_teatinos_importer.py": "legacy/bigquery_teatinos_importer.py",
        "gcp_analytics_setup.py": "legacy/gcp_analytics_setup.py",
        
        # Analysis scripts
        "analyze_quality.py": "legacy/analyze_quality.py",
        "time_series_analysis.py": "legacy/time_series_analysis.py",
        "phase2_eda.py": "legacy/phase2_eda.py",
        "phase3_ml_recommendations.py": "legacy/phase3_ml_recommendations.py",
        "prophet_prototype.py": "legacy/prophet_prototype.py",
        
        # Dashboards
        "streamlit_dashboard.py": "legacy/streamlit_dashboard.py",
        "simple_dashboard.py": "legacy/simple_dashboard.py",
        
        # Other files
        "analysis_simple.py": "legacy/analysis_simple.py",
    }


def create_legacy_readme() -> str:
    """Create README for legacy code."""
    return """# Legacy Code

This directory contains the original implementation before the DDD refactoring.

## Migration Status

### ✅ Migrated Components

1. **Data Normalization**
   - `SelargiusDataNormalizer` → `src/infrastructure/normalization/`
   - CSV parsing logic preserved

2. **BigQuery Integration**
   - Repository pattern implementation → `src/infrastructure/repositories/`
   - BigQuery service → `src/infrastructure/external_services/`

3. **Analysis Functions**
   - Consumption patterns → `src/application/use_cases/analyze_consumption_patterns.py`
   - Anomaly detection → `src/application/use_cases/detect_network_anomalies.py`
   - Network efficiency → `src/application/use_cases/calculate_network_efficiency.py`

4. **Dashboards**
   - Streamlit dashboard → `src/presentation/web/dashboard.py`
   - CLI interface → `src/presentation/cli/main.py`

### 📝 Migration Notes

- Domain entities created to replace DataFrame-centric approach
- Business logic extracted into domain services
- Infrastructure concerns separated from business logic
- Dependency injection implemented for loose coupling

### 🔧 Using Legacy Code

If you need to reference the original implementation:

```python
# Example: Using legacy normalizer
from legacy.improved_normalizer import ImprovedWaterDataNormalizer

normalizer = ImprovedWaterDataNormalizer()
results = normalizer.analyze_and_normalize("data.csv")
```

### 🚀 Recommended Actions

1. Use the new DDD structure for all new features
2. Gradually migrate remaining legacy code
3. Update scripts to use new interfaces
4. Archive this directory once migration is complete
"""


def main():
    """Main migration script."""
    print("🚀 Starting code migration to DDD structure...")
    
    # Create legacy directory
    legacy_dir = Path("legacy")
    legacy_dir.mkdir(exist_ok=True)
    
    # Get migration mapping
    file_mapping = create_migration_mapping()
    
    # Move files
    moved_count = 0
    for old_path, new_path in file_mapping.items():
        old_file = Path(old_path)
        new_file = Path(new_path)
        
        if old_file.exists():
            # Create directory if needed
            new_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(old_file), str(new_file))
            print(f"✓ Moved {old_path} → {new_path}")
            moved_count += 1
        else:
            print(f"⚠️  File not found: {old_path}")
    
    # Create legacy README
    with open(legacy_dir / "README.md", "w") as f:
        f.write(create_legacy_readme())
    
    print(f"\n✅ Migration complete! Moved {moved_count} files to legacy/")
    print("\n📋 Next steps:")
    print("1. Review the new structure in src/")
    print("2. Update any import statements in remaining files")
    print("3. Run tests to ensure everything works")
    print("4. Update deployment scripts to use new entry points")
    
    # Create migration summary
    summary = {
        "Entry Points": {
            "Web Dashboard": "poetry run streamlit run src/presentation/web/dashboard.py",
            "CLI": "poetry run python -m src.presentation.cli.main",
            "API": "poetry run uvicorn src.presentation.api.app:app",
        },
        "Key Changes": {
            "Data Models": "DataFrames → Domain Entities",
            "Architecture": "Script-based → DDD with clean architecture",
            "Dependencies": "Direct imports → Dependency Injection",
            "Testing": "Minimal → Comprehensive test coverage",
        },
        "Benefits": {
            "Maintainability": "Clear separation of concerns",
            "Testability": "Isolated components with mocked dependencies",
            "Scalability": "Easy to add new features without breaking existing code",
            "Documentation": "Self-documenting domain model",
        }
    }
    
    print("\n📊 Migration Summary:")
    for category, items in summary.items():
        print(f"\n{category}:")
        for key, value in items.items():
            print(f"  - {key}: {value}")


if __name__ == "__main__":
    main()