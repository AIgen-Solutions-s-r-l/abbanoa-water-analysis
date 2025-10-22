# Machine Learning Models Summary
## Abbanoa Water Analysis Platform

**Quick Reference Guide** | Analysis Date: October 22, 2025

---

## Key Findings

The Abbanoa platform uses **lightweight, interpretable ML** rather than deep learning:

| Aspect | Details |
|--------|---------|
| **Anomaly Detection** | Z-score statistical + scikit-learn Isolation Forest |
| **Forecasting** | Google BigQuery ML (ARIMA_PLUS) + Python statistical methods |
| **Flow Prediction** | scikit-learn RandomForestRegressor |
| **Efficiency** | scikit-learn RandomForestRegressor |
| **Deep Learning** | NONE (not used in production) |

---

## 1. Anomaly Detection Models

### Statistical Z-Score Method (Production)
- **File:** `src/domain/services/anomaly_detection_service.py`
- **Algorithm:** Z-score > 2.5 threshold
- **Detects:** Flow rate, pressure, temperature anomalies
- **Output:** Severity levels (Critical, High, Medium, Low)

### Isolation Forest (ML-Based)
- **File:** `src/application/services/anomaly_predictor.py`
- **Type:** Unsupervised ensemble
- **Features:** 12 engineered features (rolling windows, time features)
- **Training:** 30 days of historical data
- **Output:** Probability (0-1) + risk factors

---

## 2. Forecasting Models

### ARIMA_PLUS (BigQuery ML)
- **Type:** Time series forecasting
- **Horizon:** 7 days
- **Features:** Auto parameter selection, seasonal decomposition, holiday handling
- **Models:** 1 per district × metric (e.g., arima_dist001_flow_rate)

### Python Fallback
- **Method:** Simple moving average (7-day)
- **Purpose:** When ARIMA_PLUS unavailable
- **Metrics:** Trend direction, seasonality score, confidence intervals

---

## 3. Model Training

### ML Manager Service
- **File:** `src/processing/service/ml_manager.py`
- **Models:** Flow Prediction (RF), Anomaly Detection (IF), Efficiency (RF)
- **Lifecycle:** CREATED → TRAINING → VALIDATING → SHADOW → ACTIVE → RETIRED
- **Auto-Retraining:** Every 7 days or on 20% performance degradation

### Training Data Strategy
- **Recent (180 days):** 100% sampling
- **Medium-term (180-365 days):** 50% sampling  
- **Historical (1-2 years):** 10% sampling
- **Total features:** 9-12 engineered features per model

---

## 4. API Endpoints

All endpoints available at `/api/v1/ml`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/train-anomaly-detector` | POST | Train model for specific node |
| `/detect-anomalies` | GET | Real-time anomaly detection |
| `/predict-demand` | GET | Water demand forecasting |
| `/predictive-maintenance` | GET | Equipment maintenance risk |
| `/ml-dashboard-summary` | GET | Aggregated ML metrics |

---

## 5. Dependencies

**Installed ML Libraries:**
- scikit-learn 1.3.2 (Isolation Forest, Random Forest, StandardScaler)
- prophet 1.1.5 (Time series - legacy)
- pandas 2.1.4 (Data manipulation)
- numpy 1.26.2 (Numerical computing)
- scipy 1.11.4 (Scientific computing)
- joblib 1.3.2 (Model persistence)

**NOT Installed (Intentional):**
- TensorFlow / Keras
- PyTorch  
- LSTMs / RNNs
- Attention mechanisms
- AutoML frameworks

---

## 6. Performance Metrics Used

### Regression (Flow Prediction, Efficiency)
- RMSE: Root Mean Squared Error
- MAE: Mean Absolute Error
- MAPE: Mean Absolute Percentage Error (%)
- R²: Coefficient of Determination (0-1)

### Classification (Anomaly Detection)
- Precision: True positives / (TP + FP)
- Recall: True positives / (TP + FN)
- F1-Score: Harmonic mean of precision & recall
- Accuracy: (TP + TN) / Total

### Anomaly Scores
- Isolation Forest decision scores
- Anomaly probability (0-1)

---

## 7. Model Deployment

### Storage
- **Format:** joblib pickle (.pkl)
- **Location:** `/app/models/`
- **Hash:** SHA256 for integrity verification

### Shadow Deployment
1. Train new model version
2. Deploy in shadow mode (parallel predictions)
3. Monitor for 24 hours
4. Promote to active if better
5. Retire previous version

### Monitoring
- Real-time performance tracking
- Data drift detection
- Automatic retraining triggers

---

## 8. Data Drift Detection

**Method:** Statistical comparison of recent vs historical data

Triggers retraining if:
- Mean shifted > 2 standard deviations
- Z-score test confidence < 95%
- Historical distribution changed significantly

---

## 9. Key Characteristics

### Why No Deep Learning?
1. **Real-time constraints:** Need fast inference
2. **Interpretability:** Regulatory compliance in water utilities
3. **Resource efficiency:** Run on standard infrastructure
4. **Domain expertise:** Statistical methods proven for time series
5. **Maintainability:** Tree-based models easier to debug

### Strengths of Current Approach
- Lightweight (models < 50MB)
- Fast inference (< 100ms)
- Interpretable (feature importance available)
- Robust (no GPU dependency)
- Production-ready (battle-tested libraries)

---

## 10. Test Coverage

**Unit Tests:** 60+ test files covering:
- Model preprocessing
- Feature engineering
- Prediction validation
- Pattern extraction

**Integration Tests:**
- Database integration
- Real data training
- API endpoint validation
- Error handling

---

## 11. Configuration

### Z-Score Threshold (Anomaly Detection)
```python
z_score_threshold = 2.5  # Configurable per service
```

### Isolation Forest (Contamination Rate)
```python
contamination = 0.05  # Expect 5% anomalies
```

### Random Forest Parameters
```python
n_estimators = 100
max_depth = 15
min_samples_split = 5
random_state = 42
```

### ARIMA_PLUS (BigQuery)
```sql
horizon = 7                    -- 7-day forecast
data_frequency = 'DAILY'      -- Daily aggregation
holiday_region = 'IT'         -- Italian holidays
```

---

## 12. Recommended Next Steps

### Short-term
1. Implement SMOTE for class imbalance
2. Add hyperparameter tuning (GridSearchCV)
3. Implement cross-validation
4. Add SHAP values for explainability

### Medium-term
1. Advanced drift detection (PSI, KS test)
2. Ensemble voting mechanisms
3. A/B testing framework
4. Online learning capabilities

### Long-term
1. LSTM networks (if latency permits)
2. Attention mechanisms
3. Federated learning for distributed networks
4. Causal inference models

---

## 13. References

**Complete Analysis:** See `docs/ML_DL_MODELS_COMPREHENSIVE_ANALYSIS.md` (1300+ lines)

**Key Source Files:**
- `src/domain/services/anomaly_detection_service.py` (345 lines)
- `src/application/services/anomaly_predictor.py` (552 lines)  
- `src/infrastructure/services/forecast_calculation_service.py` (584 lines)
- `src/processing/service/ml_manager.py` (880 lines)
- `src/presentation/api/ml_endpoints.py` (479 lines)

**Documentation:**
- `docs/ANOMALY_DETECTION_IMPLEMENTATION.md`
- `docs/WATER_CONSUMPTION_FORECASTING.md`
- `docs/ml-models/arima-plus-forecast-prototype.md`

---

## Contact & Support

For questions about ML models in the Abbanoa platform:
1. Check the comprehensive analysis document
2. Review source code comments
3. Check test files for usage examples
4. Review API endpoint documentation

---

**Last Updated:** October 22, 2025  
**Maintained By:** ML/Data Science Team  
**Status:** Production Ready
