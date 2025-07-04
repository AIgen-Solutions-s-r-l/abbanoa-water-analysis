# 🚀 Quick Start Guide - Abbanoa Water Infrastructure v1.0.0

## Migration Status: ✅ COMPLETE

The project has been successfully migrated to the new Domain-Driven Design architecture.

## 🎯 Quick Commands

### 1. Test the System
```bash
# Run migration test
python3 test_migration.py
```

### 2. Process Data
```bash
# Normalize CSV data (works without full dependencies)
python3 -c "
from src.infrastructure.normalization.selargius_normalizer import SelargiusDataNormalizer
normalizer = SelargiusDataNormalizer()
nodes, readings, quality = normalizer.normalize_file('RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv')
print(f'Processed {len(readings)} readings with {quality.quality_score:.1f}% quality')
"
```

### 3. Use Legacy Scripts
```bash
# Legacy scripts are preserved in legacy/ directory
python3 -c "
from legacy.improved_normalizer import ImprovedWaterDataNormalizer
normalizer = ImprovedWaterDataNormalizer()
# Use as before...
"
```

## 📊 Available Data

- **Raw Data**: `RAWDATA/` directory (Selargius sensor data)
- **Processed Data**: Multiple normalized CSV files ready for use
- **Teatinos Data**: Large dataset (51MB) available

## 🔧 Environment Details

- **GCP Project**: `abbanoa-464816`
- **Account**: `a.rocchi@aigensolutions.it`
- **Authentication**: Using gcloud CLI (already configured)
- **Python**: 3.12

## 📦 For Full Features

To use all features (dashboard, API, anomaly detection), install dependencies:

```bash
# Option 1: Poetry (when it finishes resolving)
poetry install

# Option 2: Manual installation
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy matplotlib seaborn plotly streamlit
pip install google-cloud-bigquery python-dotenv
pip install fastapi uvicorn click dependency-injector
```

## 🆘 Troubleshooting

1. **Import Errors**: Make sure you're in the project root directory
2. **Authentication**: Run `gcloud auth login` if needed
3. **Dependencies**: Start with basic features that don't require all packages
4. **Legacy Code**: All original scripts are in `legacy/` directory

## 📧 Support

- Documentation: `docs/architecture/overview.md`
- Migration Guide: `MIGRATION_GUIDE.md`
- Contact: a.rocchi@aigensolutions.it

---

The system is ready to use! Start with the test script to verify everything works.