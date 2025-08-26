
# Machine Learning

The machine learning endpoints provide access to the machine learning models for the water infrastructure system.

*   `POST /api/v1/ml/train-anomaly-detector`: Train an anomaly detection model for a specific node.
*   `GET /api/v1/ml/detect-anomalies`: Detect anomalies in recent sensor data.
*   `GET /api/v1/ml/predict-demand`: Predict water demand for the next N hours.
*   `GET /api/v1/ml/dashboard-summary`: Get ML insights summary for dashboard.
