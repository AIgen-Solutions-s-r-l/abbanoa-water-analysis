# ML/DL Models Documentation Index
## Abbanoa Water Analysis Platform

---

## Document Overview

This index guides you through all machine learning and deep learning analysis for the Abbanoa platform.

### Start Here
- **First-time readers:** Start with `ML_MODELS_SUMMARY.md` (quick reference)
- **Detailed analysis:** Read `ML_DL_MODELS_COMPREHENSIVE_ANALYSIS.md` (1300+ lines)
- **Code exploration:** Use source file references below

---

## Core Documentation Files

### Summary Documents
| Document | Lines | Purpose | Audience |
|----------|-------|---------|----------|
| `ML_MODELS_SUMMARY.md` | 250 | Quick reference guide | Everyone |
| `ML_DL_MODELS_COMPREHENSIVE_ANALYSIS.md` | 1326 | Complete technical analysis | Developers, Data Scientists |
| `ML_MODELS_INDEX.md` | This file | Navigation & organization | Everyone |

### Existing Related Docs
- `ANOMALY_DETECTION_IMPLEMENTATION.md` - Anomaly detection design
- `WATER_CONSUMPTION_FORECASTING.md` - Forecasting algorithms
- `ml-models/arima-plus-forecast-prototype.md` - ARIMA_PLUS details

---

## Source Code Files

### Anomaly Detection (345 lines)
**File:** `/root/abbanoa-water-analysis/src/domain/services/anomaly_detection_service.py`

**Key Methods:**
- `detect_anomalies()` - Main detection entry point
- `_detect_statistical_anomalies()` - Z-score based detection (lines 89-150)
- `_detect_rate_of_change_anomalies()` - Rapid change detection (lines 152-207)
- `check_thresholds()` - Threshold enforcement (lines 220-305)

**Metrics Monitored:**
- Flow Rate (L/S)
- Pressure (BAR)
- Temperature (°C)

**Output:** AnomalyDetectedEvent objects with severity levels

---

### Anomaly Predictor (552 lines)
**File:** `/root/abbanoa-water-analysis/src/application/services/anomaly_predictor.py`

**Key Classes:**
- `AnomalyPredictor` - Main predictor class
- `AnomalyPrediction` - Prediction output dataclass
- `PredictionConfidence` - Confidence enum (LOW, MEDIUM, HIGH)

**Key Methods:**
- `preprocess_data()` - Feature engineering (lines 75-114)
- `extract_patterns()` - Pattern analysis (lines 116-169)
- `train_from_database()` - ML training (lines 171-242)
- `predict()` - Single prediction (lines 342-429)
- `predict_batch()` - Batch predictions (lines 431-459)

**Models Used:**
- RandomForestClassifier (supervised)
- StandardScaler (feature normalization)

**Features:** 12 engineered features including rolling statistics, time features

---

### Forecast Calculation Service (584 lines)
**File:** `/root/abbanoa-water-analysis/src/infrastructure/services/forecast_calculation_service.py`

**Key Methods:**
- `calculate_forecast()` - Main forecasting pipeline (lines 33-142)
- `_fetch_historical_data()` - Data retrieval (lines 144-203)
- `_generate_forecast()` - ARIMA_PLUS integration (lines 210-276)
- `_get_trend_direction()` - Trend analysis (lines 332-360)
- `_calculate_trend_strength()` - R² calculation (lines 362-389)
- `_detect_seasonality()` - Autocorrelation detection (lines 391-412)
- `_fallback_forecast()` - Fallback method (lines 485-584)

**Forecast Metrics Returned:**
- trend_direction: 'increasing' / 'decreasing' / 'stable'
- trend_strength: R² value (0-1)
- seasonality_score: Autocorrelation (0-1)
- confidence_level: 0.8 (80% CI)
- forecast_mean, forecast_std, historical_mean, etc.

---

### ML Model Manager (880 lines)
**File:** `/root/abbanoa-water-analysis/src/processing/service/ml_manager.py`

**Key Classes:**
- `MLModelManager` - Lifecycle management
- `ModelType` - Constants (FLOW_PREDICTION, ANOMALY_DETECTION, EFFICIENCY_OPTIMIZATION)
- `ModelStatus` - Status enum (CREATED, TRAINING, VALIDATING, SHADOW, ACTIVE, RETIRED)

**Key Methods:**
- `retrain_models()` - Retraining cycle (lines 73-106)
- `_should_retrain()` - Trigger logic (lines 108-133)
- `_train_model()` - Model training (lines 135-181)
- `_get_training_data()` - Hybrid sampling (lines 183-229)
- `_train_flow_prediction_model()` - RandomForestRegressor (lines 331-345)
- `_train_anomaly_detection_model()` - IsolationForest (lines 347-359)
- `_evaluate_model()` - Performance metrics (lines 376-413)
- `_deploy_shadow()` - Shadow deployment (lines 465-482)
- `_monitor_and_promote()` - Promotion logic (lines 483-502)
- `_detect_data_drift()` - Drift detection (lines 765-802)

**Model Storage:**
- Format: joblib pickle (.pkl)
- Hash: SHA256 verification
- Path: `/app/models/`

---

### ML Endpoints API (479 lines)
**File:** `/root/abbanoa-water-analysis/src/presentation/api/ml_endpoints.py`

**Key Classes:**
- `AnomalyDetector` - Simplified detector for API
- Routes with decorators:
  - `train_anomaly_detector` (POST)
  - `detect_anomalies` (GET)
  - `predict_demand` (GET)
  - `predictive_maintenance` (GET)
  - `ml_dashboard_summary` (GET)

**Helper Functions:**
- `generate_recommendations()` - Actionable advice
- `calculate_weekend_factor()` - Pattern analysis
- `calculate_maintenance_risk()` - Risk scoring

---

### Legacy Code

#### Prophet Prototype
**File:** `/root/abbanoa-water-analysis/docs/legacy/prophet_prototype.py` (136 lines)

**Status:** NOT IN PRODUCTION (commented out)

**Algorithm:**
```python
model = Prophet(
    daily_seasonality=True,
    weekly_seasonality=True,
    yearly_seasonality=False,
    changepoint_prior_scale=0.05
)
```

**Alternative to:** ARIMA_PLUS for forecasting

#### ML Anomaly Detection POC
**File:** `/root/abbanoa-water-analysis/scripts/ml_anomaly_detection_poc.py` (323 lines)

**Status:** PROOF OF CONCEPT

**Features:**
- WaterAnomalyDetector class
- IsolationForest implementation (contamination=0.01)
- 21 engineered features
- 7 anomaly type classifications

---

## Model Architecture Overview

### Training Data Flow
```
Raw Sensor Data
    ↓
Feature Engineering (rolling windows, lag features)
    ↓
Data Preprocessing (scaling, normalization)
    ↓
Train/Test Split (80/20)
    ↓
Model Training
    ↓
Validation & Evaluation
    ↓
Shadow Deployment (24h monitoring)
    ↓
Production Deployment (Active model)
```

### Prediction Flow
```
Real-time Sensor Data
    ↓
Feature Engineering
    ↓
Feature Scaling
    ↓
Model Prediction
    ↓
Post-processing (confidence, risk factors)
    ↓
API Response
    ↓
Database Storage
```

---

## Model Summary Table

| Model | Type | Location | Status | Purpose |
|-------|------|----------|--------|---------|
| Z-Score Anomaly | Statistical | anomaly_detection_service.py | PRODUCTION | Detect statistical anomalies |
| Isolation Forest | ML-Unsupervised | anomaly_predictor.py | PRODUCTION | Unsupervised anomaly detection |
| Random Forest Classifier | ML-Supervised | anomaly_predictor.py | PRODUCTION | Supervised anomaly prediction |
| ARIMA_PLUS | Time Series ML | BigQuery ML | PRODUCTION | 7-day forecasting |
| Random Forest Regressor | ML-Regression | ml_manager.py | PRODUCTION | Flow rate prediction |
| Random Forest Regressor | ML-Regression | ml_manager.py | PRODUCTION | Efficiency optimization |
| Simple Moving Average | Statistical | forecast_calculation_service.py | FALLBACK | Fallback forecasting |
| Prophet | Time Series | prophet_prototype.py | LEGACY | Alternative forecasting |

---

## Dependencies

### Installed
- scikit-learn 1.3.2 - Ensemble methods, preprocessing
- prophet 1.1.5 - Time series
- pandas 2.1.4 - Data manipulation
- numpy 1.26.2 - Numerical computing
- scipy 1.11.4 - Scientific computing
- joblib 1.3.2 - Model persistence

### NOT Installed (Intentional)
- TensorFlow / Keras
- PyTorch
- LSTMs / RNNs
- Attention mechanisms
- AutoML frameworks

**Rationale:** Platform prioritizes interpretability, speed, and maintainability over raw performance.

---

## Testing Files

### Unit Tests (60+ files)
- `tests/unit/test_anomaly_predictor.spec.py` - Anomaly prediction tests
- `tests/unit/test_forecasting_service.py` - Forecast service tests
- `tests/unit/test_prediction_tracker.spec.py` - Tracking tests

### Integration Tests
- `tests/integration/test_anomaly_detection.int.py` - End-to-end anomaly
- `tests/integration/test_forecast_flow.py` - Forecasting pipeline
- `tests/integration/test_prediction_tracking.int.py` - Prediction tracking

---

## Configuration Parameters

### Anomaly Detection
```python
z_score_threshold = 2.5          # Configurable
min_data_points = 10             # Minimum samples
rolling_window_hours = 24        # Window size
severity_boundaries = {
    'critical': >= 4.0,
    'high': >= 3.0,
    'medium': >= 2.5,
    'low': < 2.5
}
```

### Isolation Forest
```python
n_estimators = 100
contamination = 0.05             # 5% anomalies expected
random_state = 42
n_jobs = -1                      # Parallel processing
```

### ARIMA_PLUS
```sql
horizon = 7                      -- Days ahead
data_frequency = 'DAILY'         -- Aggregation
holiday_region = 'IT'            -- Italian holidays
auto_arima = TRUE                -- Parameter selection
decompose_time_series = TRUE     -- Seasonal decomposition
```

---

## Quick Start

### For Developers
1. Read `ML_MODELS_SUMMARY.md` first
2. Explore source code starting with `anomaly_detection_service.py`
3. Check tests in `tests/unit/` for usage examples
4. Review API endpoints in `ml_endpoints.py`

### For Data Scientists
1. Read full `ML_DL_MODELS_COMPREHENSIVE_ANALYSIS.md`
2. Review feature engineering in `anomaly_predictor.py`
3. Check training data strategy in `ml_manager.py`
4. Examine evaluation metrics and performance
5. Review recommendations section

### For Operations
1. Check `ML_MODELS_SUMMARY.md` for overview
2. Review "Model Deployment" section
3. Monitor data drift detection alerts
4. Check model versioning in `/app/models/`

---

## Key Insights

### What's Implemented
1. ✅ Statistical anomaly detection (Z-score)
2. ✅ ML-based anomaly detection (Isolation Forest)
3. ✅ Time series forecasting (ARIMA_PLUS + fallback)
4. ✅ Flow prediction (RandomForest)
5. ✅ Efficiency optimization (RandomForest)
6. ✅ Complete ML lifecycle management
7. ✅ Data drift detection
8. ✅ Shadow deployment strategy

### What's NOT Implemented
1. ❌ Deep Learning (no LSTM, CNN, RNN)
2. ❌ Neural Networks
3. ❌ Attention mechanisms
4. ❌ Transformer models
5. ❌ AutoML

### Why?
- Real-time requirements (< 100ms latency)
- Interpretability (regulatory compliance)
- Resource efficiency (no GPU needed)
- Domain fit (time series + statistical methods)
- Maintainability (simpler models, easier debugging)

---

## Performance Metrics

### Target MAPE (Mean Absolute Percentage Error)
- Forecasting: ≤ 15%
- Flow Prediction: Target varies by district
- Anomaly Detection: Precision ≥ 0.78, Recall ≥ 0.75

### Model Retraining
- Triggers: Every 7 days OR 20% performance degradation
- Strategy: Shadow deployment for 24 hours before promotion
- Monitoring: Real-time performance tracking

---

## Future Enhancements

### Short-term (1-3 months)
- SMOTE for class imbalance
- Hyperparameter tuning (GridSearchCV)
- Cross-validation
- SHAP values for explainability

### Medium-term (3-6 months)
- Advanced drift detection (PSI, KS test)
- Ensemble voting
- A/B testing framework
- Online learning

### Long-term (6+ months)
- LSTM networks (if latency permits)
- Attention mechanisms
- Federated learning
- Causal inference

---

## Navigation Guide

```
ML/DL Analysis
├─ Quick Start
│  └─ ML_MODELS_SUMMARY.md (this is your start)
│
├─ Deep Dive
│  └─ ML_DL_MODELS_COMPREHENSIVE_ANALYSIS.md
│
├─ Source Code
│  ├─ Anomaly Detection
│  │  ├─ src/domain/services/anomaly_detection_service.py (345 lines)
│  │  └─ src/application/services/anomaly_predictor.py (552 lines)
│  ├─ Forecasting
│  │  └─ src/infrastructure/services/forecast_calculation_service.py (584 lines)
│  ├─ Training & Deployment
│  │  └─ src/processing/service/ml_manager.py (880 lines)
│  └─ API
│     └─ src/presentation/api/ml_endpoints.py (479 lines)
│
├─ Tests
│  ├─ tests/unit/test_anomaly_predictor.spec.py
│  ├─ tests/integration/test_anomaly_detection.int.py
│  └─ tests/integration/test_forecast_flow.py
│
└─ Reference Docs
   ├─ ANOMALY_DETECTION_IMPLEMENTATION.md
   ├─ WATER_CONSUMPTION_FORECASTING.md
   └─ ml-models/arima-plus-forecast-prototype.md
```

---

## Support & Questions

For specific questions:
1. **Model training:** See ml_manager.py (lines 135-181)
2. **Feature engineering:** See anomaly_predictor.py (lines 75-114)
3. **Anomaly detection:** See anomaly_detection_service.py
4. **Forecasting:** See forecast_calculation_service.py
5. **API usage:** See ml_endpoints.py

---

**Version:** 1.0  
**Date:** October 22, 2025  
**Status:** Complete Analysis Available
