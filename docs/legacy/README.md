# Legacy Code

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
