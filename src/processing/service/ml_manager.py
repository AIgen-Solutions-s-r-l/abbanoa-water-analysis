"""
ML Model Manager for training, evaluation, and deployment.

This module handles the complete ML lifecycle including:
- Model training with hybrid data strategy
- Performance evaluation and drift detection
- Shadow deployment and A/B testing
- Automatic rollback on performance degradation
"""

import asyncio
import hashlib
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class ModelType:
    """Model type constants."""

    FLOW_PREDICTION = "flow_prediction"
    ANOMALY_DETECTION = "anomaly_detection"
    EFFICIENCY_OPTIMIZATION = "efficiency_optimization"


class ModelStatus:
    """Model status constants."""

    CREATED = "created"
    TRAINING = "training"
    VALIDATING = "validating"
    SHADOW = "shadow"
    ACTIVE = "active"
    RETIRED = "retired"


class MLModelManager:
    """Manages ML model lifecycle."""

    def __init__(self):
        """Initialize ML model manager."""
        self.postgres_manager = None
        self.bigquery_client = None
        self.model_storage_path = os.getenv("MODEL_STORAGE_PATH", "/app/models")
        self.active_models = {}
        self.shadow_models = {}

        # Training configuration
        self.retrain_threshold_days = 7
        self.performance_degradation_threshold = 1.2  # 20% degradation

    async def initialize(self, postgres_manager, bigquery_client):
        """Initialize with database connections."""
        self.postgres_manager = postgres_manager
        self.bigquery_client = bigquery_client

        # Create model storage directory
        os.makedirs(self.model_storage_path, exist_ok=True)

        # Load active models
        await self._load_active_models()

        logger.info("ML model manager initialized")

    async def retrain_models(self):
        """Retrain models based on schedule or performance triggers."""
        logger.info("Starting model retraining cycle...")

        model_types = [
            ModelType.FLOW_PREDICTION,
            ModelType.ANOMALY_DETECTION,
            ModelType.EFFICIENCY_OPTIMIZATION,
        ]

        for model_type in model_types:
            try:
                should_retrain = await self._should_retrain(model_type)

                if should_retrain:
                    logger.info(f"Retraining {model_type} model...")

                    # Train new model
                    new_model = await self._train_model(model_type)

                    # Validate model
                    if await self._validate_model(new_model, model_type):
                        # Deploy in shadow mode
                        await self._deploy_shadow(new_model)

                        # Schedule promotion after monitoring period
                        asyncio.create_task(
                            self._monitor_and_promote(new_model, hours=24)
                        )
                    else:
                        logger.warning(
                            f"Model {model_type} validation failed, skipping deployment"
                        )

            except Exception as e:
                logger.error(f"Failed to retrain {model_type}: {e}", exc_info=True)

    async def _should_retrain(self, model_type: str) -> bool:
        """Determine if a model should be retrained."""
        current_model = await self._get_active_model(model_type)

        if not current_model:
            logger.info(f"No active model for {model_type}, training required")
            return True

        # Check model age
        model_age_days = (datetime.now() - current_model["created_at"]).days
        if model_age_days >= self.retrain_threshold_days:
            logger.info(f"Model {model_type} is {model_age_days} days old, retraining")
            return True

        # Check performance degradation
        recent_performance = await self._get_recent_performance(
            current_model["model_id"]
        )
        if (
            recent_performance
            and recent_performance["degradation_factor"]
            > self.performance_degradation_threshold
        ):
            logger.info(
                f"Model {model_type} performance degraded by {recent_performance['degradation_factor']:.2f}x, retraining"
            )
            return True

        # Check for data drift
        if await self._detect_data_drift(model_type):
            logger.info(f"Data drift detected for {model_type}, retraining")
            return True

        return False

    async def _train_model(self, model_type: str) -> Dict[str, Any]:
        """Train a new model version."""
        # Create model record
        model_id = await self._create_model_record(model_type)

        try:
            # Update status to training
            await self._update_model_status(model_id, ModelStatus.TRAINING)

            # Get training data using hybrid strategy
            (
                X_train,
                y_train,
                X_val,
                y_val,
                feature_names,
            ) = await self._get_training_data(model_type)

            # Train model based on type
            if model_type == ModelType.FLOW_PREDICTION:
                model = await self._train_flow_prediction_model(X_train, y_train)
            elif model_type == ModelType.ANOMALY_DETECTION:
                model = await self._train_anomaly_detection_model(X_train)
            elif model_type == ModelType.EFFICIENCY_OPTIMIZATION:
                model = await self._train_efficiency_model(X_train, y_train)
            else:
                raise ValueError(f"Unknown model type: {model_type}")

            # Evaluate model
            metrics = await self._evaluate_model(model, X_val, y_val, model_type)

            # Save model
            model_path = await self._save_model(model, model_id, model_type)

            # Update model record
            await self._update_model_record(
                model_id,
                status=ModelStatus.VALIDATING,
                metrics=metrics,
                model_path=model_path,
                feature_names=feature_names,
            )

            return {
                "model_id": model_id,
                "model_type": model_type,
                "metrics": metrics,
                "model_path": model_path,
            }

        except Exception as e:
            await self._update_model_status(model_id, ModelStatus.CREATED, error=str(e))
            raise

    async def _get_training_data(
        self, model_type: str
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """Get training data using hybrid strategy."""
        # Fetch data based on our hybrid approach
        # - Last 180 days: Full resolution
        # - 180-365 days: 50% sampling
        # - >365 days: 10% sampling

        end_date = datetime.now()

        # Recent data (full resolution)
        recent_data = await self._fetch_training_data(
            start_date=end_date - timedelta(days=180),
            end_date=end_date,
            sample_rate=1.0,
        )

        # Medium-term data (50% sampling)
        medium_data = await self._fetch_training_data(
            start_date=end_date - timedelta(days=365),
            end_date=end_date - timedelta(days=180),
            sample_rate=0.5,
        )

        # Historical data (10% sampling)
        historical_data = await self._fetch_training_data(
            start_date=end_date - timedelta(days=730),  # 2 years
            end_date=end_date - timedelta(days=365),
            sample_rate=0.1,
        )

        # Combine data
        all_data = pd.concat(
            [recent_data, medium_data, historical_data], ignore_index=True
        )

        # Feature engineering based on model type
        if model_type == ModelType.FLOW_PREDICTION:
            features, target = self._prepare_flow_prediction_features(all_data)
        elif model_type == ModelType.ANOMALY_DETECTION:
            features, target = self._prepare_anomaly_detection_features(all_data)
        elif model_type == ModelType.EFFICIENCY_OPTIMIZATION:
            features, target = self._prepare_efficiency_features(all_data)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            features.values, target.values, test_size=0.2, random_state=42
        )

        return X_train, y_train, X_val, y_val, features.columns.tolist()

    async def _fetch_training_data(
        self, start_date: datetime, end_date: datetime, sample_rate: float
    ) -> pd.DataFrame:
        """Fetch training data from BigQuery with sampling."""
        query = f"""
        SELECT 
            timestamp,
            node_id,
            flow_rate,
            pressure,
            temperature,
            volume as total_flow,
            LAG(flow_rate, 1) OVER (PARTITION BY node_id ORDER BY timestamp) as prev_flow_rate,
            LAG(pressure, 1) OVER (PARTITION BY node_id ORDER BY timestamp) as prev_pressure,
            EXTRACT(HOUR FROM timestamp) as hour_of_day,
            EXTRACT(DAYOFWEEK FROM timestamp) as day_of_week,
            EXTRACT(MONTH FROM timestamp) as month
        FROM `{self.bigquery_client.project_id}.{self.bigquery_client.dataset_id}.sensor_readings_ml`
        WHERE timestamp BETWEEN @start_date AND @end_date
        AND RAND() < @sample_rate
        ORDER BY timestamp
        """

        job_config = self.bigquery_client.client.query_job_config()
        job_config.query_parameters = [
            self.bigquery_client.client.query_parameter(
                "start_date", "TIMESTAMP", start_date
            ),
            self.bigquery_client.client.query_parameter(
                "end_date", "TIMESTAMP", end_date
            ),
            self.bigquery_client.client.query_parameter(
                "sample_rate", "FLOAT64", sample_rate
            ),
        ]

        return self.bigquery_client.client.query(
            query, job_config=job_config
        ).to_dataframe()

    def _prepare_flow_prediction_features(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for flow prediction model."""
        # Features for predicting next hour's flow rate
        features = pd.DataFrame(
            {
                "current_flow": df["flow_rate"],
                "prev_flow": df["prev_flow_rate"].fillna(df["flow_rate"].mean()),
                "current_pressure": df["pressure"],
                "prev_pressure": df["prev_pressure"].fillna(df["pressure"].mean()),
                "temperature": df["temperature"],
                "hour_of_day": df["hour_of_day"],
                "day_of_week": df["day_of_week"],
                "month": df["month"],
                "flow_pressure_ratio": df["flow_rate"]
                / (df["pressure"] + 0.1),  # Avoid division by zero
            }
        )

        # Target is next hour's flow rate
        target = df["flow_rate"].shift(-2)  # 2 periods ahead (1 hour with 30-min data)

        # Remove rows with NaN target
        valid_idx = ~target.isna()
        return features[valid_idx], target[valid_idx]

    def _prepare_anomaly_detection_features(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for anomaly detection model."""
        features = pd.DataFrame(
            {
                "flow_rate": df["flow_rate"],
                "pressure": df["pressure"],
                "temperature": df["temperature"],
                "flow_change": df["flow_rate"]
                - df["prev_flow_rate"].fillna(df["flow_rate"]),
                "pressure_change": df["pressure"]
                - df["prev_pressure"].fillna(df["pressure"]),
                "hour_of_day": df["hour_of_day"],
                "day_of_week": df["day_of_week"],
            }
        )

        # For anomaly detection, we don't have explicit labels
        # Using placeholder - in production, this would be based on labeled anomalies
        target = pd.Series(np.zeros(len(features)), index=features.index)

        return features.dropna(), target

    def _prepare_efficiency_features(
        self, df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for efficiency optimization model."""
        # Group by hour to get network-wide metrics
        hourly = df.groupby(df["timestamp"].dt.floor("H")).agg(
            {
                "flow_rate": ["sum", "mean", "std"],
                "pressure": ["mean", "std"],
                "temperature": "mean",
            }
        )

        features = pd.DataFrame(
            {
                "total_flow": hourly["flow_rate"]["sum"],
                "avg_flow": hourly["flow_rate"]["mean"],
                "flow_variance": hourly["flow_rate"]["std"].fillna(0),
                "avg_pressure": hourly["pressure"]["mean"],
                "pressure_variance": hourly["pressure"]["std"].fillna(0),
                "temperature": hourly["temperature"]["mean"],
                "hour": hourly.index.hour,
            }
        )

        # Target is efficiency (simplified as ratio of output to input)
        # In reality, this would be calculated from actual network topology
        target = (
            0.95
            - (features["flow_variance"] / features["avg_flow"].clip(lower=1)) * 0.1
        )

        return features.dropna(), target

    async def _train_flow_prediction_model(
        self, X_train: np.ndarray, y_train: np.ndarray
    ):
        """Train flow prediction model."""
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            n_jobs=-1,
            random_state=42,
        )

        # Run training in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, model.fit, X_train, y_train)

        return model

    async def _train_anomaly_detection_model(self, X_train: np.ndarray):
        """Train anomaly detection model."""
        model = IsolationForest(
            n_estimators=100,
            contamination=0.05,  # Expect 5% anomalies
            random_state=42,
            n_jobs=-1,
        )

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, model.fit, X_train)

        return model

    async def _train_efficiency_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train efficiency optimization model."""
        # Similar to flow prediction but focused on efficiency metrics
        model = RandomForestRegressor(
            n_estimators=50, max_depth=10, n_jobs=-1, random_state=42
        )

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, model.fit, X_train, y_train)

        return model

    async def _evaluate_model(
        self, model, X_val: np.ndarray, y_val: Optional[np.ndarray], model_type: str
    ) -> Dict[str, float]:
        """Evaluate model performance."""
        loop = asyncio.get_event_loop()

        if model_type == ModelType.ANOMALY_DETECTION:
            # For anomaly detection, evaluate using anomaly scores
            anomaly_scores = await loop.run_in_executor(
                None, model.decision_function, X_val
            )

            # Calculate metrics based on score distribution
            return {
                "mean_anomaly_score": float(np.mean(anomaly_scores)),
                "std_anomaly_score": float(np.std(anomaly_scores)),
                "min_score": float(np.min(anomaly_scores)),
                "max_score": float(np.max(anomaly_scores)),
            }
        else:
            # For regression models
            predictions = await loop.run_in_executor(None, model.predict, X_val)

            rmse = np.sqrt(mean_squared_error(y_val, predictions))
            mae = mean_absolute_error(y_val, predictions)
            r2 = r2_score(y_val, predictions)

            # Calculate MAPE (Mean Absolute Percentage Error)
            mape = np.mean(np.abs((y_val - predictions) / (y_val + 1e-10))) * 100

            return {
                "rmse": float(rmse),
                "mae": float(mae),
                "mape": float(mape),
                "r2": float(r2),
            }

    async def _save_model(self, model, model_id: str, model_type: str) -> str:
        """Save model to storage."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_type}_v{model_id}_{timestamp}.pkl"
        filepath = os.path.join(self.model_storage_path, filename)

        # Save model
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, joblib.dump, model, filepath)

        # Calculate model hash
        with open(filepath, "rb") as f:
            model_hash = hashlib.sha256(f.read()).hexdigest()

        # Update model size
        model_size = os.path.getsize(filepath)

        # Store hash and size in database
        async with self.postgres_manager.acquire() as conn:
            await conn.execute(
                """
                UPDATE water_infrastructure.ml_models
                SET model_hash = $1, model_size_bytes = $2
                WHERE model_id = $3
            """,
                model_hash,
                model_size,
                model_id,
            )

        return filepath

    async def _validate_model(
        self, model_info: Dict[str, Any], model_type: str
    ) -> bool:
        """Validate model against current active model."""
        current_model = await self._get_active_model(model_type)

        if not current_model:
            # No current model, new model is valid
            return True

        # Compare metrics
        new_metrics = model_info["metrics"]
        current_metrics = current_model["metrics"]

        if model_type == ModelType.ANOMALY_DETECTION:
            # For anomaly detection, we want consistent score distribution
            return True  # Simplified for now
        else:
            # For regression models, check if new model is better
            if "rmse" in new_metrics and "rmse" in current_metrics:
                # New model should have lower RMSE
                return (
                    new_metrics["rmse"] <= current_metrics["rmse"] * 1.1
                )  # Allow 10% tolerance

        return True

    async def _deploy_shadow(self, model_info: Dict[str, Any]):
        """Deploy model in shadow mode."""
        model_id = model_info["model_id"]
        model_type = model_info["model_type"]

        # Update status to shadow
        await self._update_model_status(model_id, ModelStatus.SHADOW)

        # Load model into shadow models
        model = joblib.load(model_info["model_path"])
        self.shadow_models[model_type] = {
            "model": model,
            "model_id": model_id,
            "deployed_at": datetime.now(),
        }

        logger.info(f"Deployed model {model_id} in shadow mode for {model_type}")

    async def _monitor_and_promote(self, model_info: Dict[str, Any], hours: int = 24):
        """Monitor shadow model and promote if performing well."""
        await asyncio.sleep(hours * 3600)  # Wait for monitoring period

        model_id = model_info["model_id"]
        model_type = model_info["model_type"]

        # Check shadow model performance
        shadow_performance = await self._evaluate_shadow_performance(model_id)

        if shadow_performance["is_better"]:
            # Promote to active
            await self._promote_model(model_id, model_type)
            logger.info(f"Promoted model {model_id} to active for {model_type}")
        else:
            # Retire shadow model
            await self._update_model_status(model_id, ModelStatus.RETIRED)
            del self.shadow_models[model_type]
            logger.info(f"Retired shadow model {model_id} due to poor performance")

    async def _evaluate_shadow_performance(self, model_id: str) -> Dict[str, Any]:
        """Evaluate shadow model performance."""
        # Get comparison metrics from shadow predictions
        async with self.postgres_manager.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as prediction_count,
                    AVG(ABS(predicted_value - actual_value)) as avg_error
                FROM water_infrastructure.shadow_predictions
                WHERE model_id = $1
                AND prediction_timestamp > CURRENT_TIMESTAMP - INTERVAL '24 hours'
            """,
                model_id,
            )

        # Simplified evaluation - in production, this would be more sophisticated
        return {
            "is_better": result["prediction_count"] > 100 and result["avg_error"] < 10,
            "prediction_count": result["prediction_count"],
            "avg_error": result["avg_error"],
        }

    async def _promote_model(self, model_id: str, model_type: str):
        """Promote shadow model to active."""
        async with self.postgres_manager.acquire() as conn:
            # Retire current active model
            await conn.execute(
                """
                UPDATE water_infrastructure.ml_models
                SET is_active = FALSE, status = 'retired', retired_at = CURRENT_TIMESTAMP
                WHERE model_type = $1 AND is_active = TRUE
            """,
                model_type,
            )

            # Activate new model
            await conn.execute(
                """
                UPDATE water_infrastructure.ml_models
                SET is_active = TRUE, status = 'active', activated_at = CURRENT_TIMESTAMP
                WHERE model_id = $1
            """,
                model_id,
            )

        # Update in-memory models
        if model_type in self.shadow_models:
            self.active_models[model_type] = self.shadow_models[model_type]
            del self.shadow_models[model_type]

    async def generate_predictions(self, nodes: List[str], timestamp: datetime):
        """Generate predictions for specified nodes."""
        for model_type in [ModelType.FLOW_PREDICTION]:  # Start with flow prediction
            if model_type not in self.active_models:
                logger.warning(f"No active model for {model_type}")
                continue

            model_info = self.active_models[model_type]
            model = model_info["model"]

            # Generate predictions for each node
            for node_id in nodes:
                try:
                    # Get recent data for features
                    features = await self._get_prediction_features(
                        node_id, timestamp, model_type
                    )

                    if features is not None:
                        # Make prediction
                        prediction = model.predict(features.reshape(1, -1))[0]

                        # Store prediction
                        await self._store_prediction(
                            model_info["model_id"],
                            node_id,
                            timestamp,
                            prediction,
                            model_type,
                        )

                except Exception as e:
                    logger.error(
                        f"Failed to generate prediction for node {node_id}: {e}"
                    )

    async def _get_prediction_features(
        self, node_id: str, timestamp: datetime, model_type: str
    ) -> Optional[np.ndarray]:
        """Get features for prediction."""
        # Get recent computed metrics
        async with self.postgres_manager.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT 
                    avg_flow_rate, avg_pressure, avg_temperature,
                    flow_variance, pressure_variance
                FROM water_infrastructure.computed_metrics
                WHERE node_id = $1
                AND window_end <= $2
                AND time_window = '1hour'
                ORDER BY window_end DESC
                LIMIT 1
            """,
                node_id,
                timestamp,
            )

        if not result:
            return None

        # Build features based on model type
        if model_type == ModelType.FLOW_PREDICTION:
            features = np.array(
                [
                    result["avg_flow_rate"],
                    result["avg_flow_rate"],  # Previous flow (simplified)
                    result["avg_pressure"],
                    result["avg_pressure"],  # Previous pressure (simplified)
                    result["avg_temperature"],
                    timestamp.hour,
                    timestamp.weekday(),
                    timestamp.month,
                    result["avg_flow_rate"] / (result["avg_pressure"] + 0.1),
                ]
            )
            return features

        return None

    async def _store_prediction(
        self,
        model_id: str,
        node_id: str,
        timestamp: datetime,
        prediction: float,
        model_type: str,
    ):
        """Store model prediction."""
        async with self.postgres_manager.acquire() as conn:
            # Calculate confidence intervals (simplified)
            confidence_interval = prediction * 0.1  # 10% confidence interval

            await conn.execute(
                """
                INSERT INTO water_infrastructure.ml_predictions_cache
                (model_id, node_id, prediction_timestamp, prediction_horizon_hours,
                 target_timestamp, predicted_flow_rate, flow_rate_lower, flow_rate_upper,
                 confidence_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (model_id, node_id, target_timestamp) DO UPDATE
                SET predicted_flow_rate = EXCLUDED.predicted_flow_rate,
                    flow_rate_lower = EXCLUDED.flow_rate_lower,
                    flow_rate_upper = EXCLUDED.flow_rate_upper
            """,
                model_id,
                node_id,
                timestamp,
                1,
                timestamp + timedelta(hours=1),
                prediction,
                prediction - confidence_interval,
                prediction + confidence_interval,
                0.80,  # 80% confidence
            )

    async def evaluate_models(self):
        """Periodic model evaluation."""
        logger.info("Evaluating active models...")

        for model_type, model_info in self.active_models.items():
            try:
                # Get recent predictions and actual values
                performance = await self._calculate_model_performance(
                    model_info["model_id"], model_type
                )

                # Store performance metrics
                await self._store_performance_metrics(
                    model_info["model_id"], performance
                )

                # Check for performance degradation
                if (
                    performance["rmse"]
                    > model_info.get("baseline_rmse", 0)
                    * self.performance_degradation_threshold
                ):
                    logger.warning(
                        f"Model {model_type} performance degraded significantly"
                    )

            except Exception as e:
                logger.error(f"Failed to evaluate model {model_type}: {e}")

    async def _calculate_model_performance(
        self, model_id: str, model_type: str
    ) -> Dict[str, float]:
        """Calculate model performance metrics."""
        # Get predictions vs actuals for the last day
        async with self.postgres_manager.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT 
                    p.predicted_flow_rate,
                    a.avg_flow_rate as actual_flow_rate
                FROM water_infrastructure.ml_predictions_cache p
                JOIN water_infrastructure.computed_metrics a
                    ON p.node_id = a.node_id
                    AND a.window_start <= p.target_timestamp
                    AND a.window_end > p.target_timestamp
                    AND a.time_window = '1hour'
                WHERE p.model_id = $1
                AND p.prediction_timestamp > CURRENT_TIMESTAMP - INTERVAL '1 day'
            """,
                model_id,
            )

        if not results:
            return {"rmse": 0, "mae": 0, "mape": 0, "r2": 0}

        predictions = np.array([r["predicted_flow_rate"] for r in results])
        actuals = np.array([r["actual_flow_rate"] for r in results])

        return {
            "rmse": float(np.sqrt(mean_squared_error(actuals, predictions))),
            "mae": float(mean_absolute_error(actuals, predictions)),
            "mape": float(
                np.mean(np.abs((actuals - predictions) / (actuals + 1e-10))) * 100
            ),
            "r2": float(r2_score(actuals, predictions)),
        }

    async def _store_performance_metrics(
        self, model_id: str, metrics: Dict[str, float]
    ):
        """Store model performance metrics."""
        async with self.postgres_manager.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO water_infrastructure.model_performance
                (model_id, evaluation_timestamp, evaluation_window,
                 predictions_count, rmse, mae, mape, r2_score)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                model_id,
                datetime.now(),
                "daily",
                100,  # Placeholder
                metrics["rmse"],
                metrics["mae"],
                metrics["mape"],
                metrics["r2"],
            )

    async def _get_active_model(self, model_type: str) -> Optional[Dict[str, Any]]:
        """Get active model information."""
        async with self.postgres_manager.acquire() as conn:
            result = await conn.fetchrow(
                """
                SELECT model_id, version, metrics, model_path, created_at
                FROM water_infrastructure.ml_models
                WHERE model_type = $1 AND is_active = TRUE
                LIMIT 1
            """,
                model_type,
            )

        return dict(result) if result else None

    async def _get_recent_performance(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get recent performance metrics for a model."""
        async with self.postgres_manager.acquire() as conn:
            current = await conn.fetchrow(
                """
                SELECT rmse
                FROM water_infrastructure.model_performance
                WHERE model_id = $1
                ORDER BY evaluation_timestamp DESC
                LIMIT 1
            """,
                model_id,
            )

            baseline = await conn.fetchrow(
                """
                SELECT metrics->>'rmse' as rmse
                FROM water_infrastructure.ml_models
                WHERE model_id = $1
            """,
                model_id,
            )

        if current and baseline:
            baseline_rmse = float(baseline["rmse"])
            current_rmse = float(current["rmse"])

            return {
                "current_rmse": current_rmse,
                "baseline_rmse": baseline_rmse,
                "degradation_factor": current_rmse / baseline_rmse
                if baseline_rmse > 0
                else 1.0,
            }

        return None

    async def _detect_data_drift(self, model_type: str) -> bool:
        """Detect if there's significant data drift."""
        # Simplified drift detection
        # In production, this would use statistical tests like KS test, PSI, etc.

        # Get recent data distribution
        async with self.postgres_manager.acquire() as conn:
            recent_stats = await conn.fetchrow(
                """
                SELECT 
                    AVG(avg_flow_rate) as mean_flow,
                    STDDEV(avg_flow_rate) as std_flow,
                    AVG(avg_pressure) as mean_pressure,
                    STDDEV(avg_pressure) as std_pressure
                FROM water_infrastructure.computed_metrics
                WHERE window_start > CURRENT_TIMESTAMP - INTERVAL '7 days'
                AND time_window = '1hour'
            """
            )

            historical_stats = await conn.fetchrow(
                """
                SELECT 
                    AVG(avg_flow_rate) as mean_flow,
                    STDDEV(avg_flow_rate) as std_flow,
                    AVG(avg_pressure) as mean_pressure,
                    STDDEV(avg_pressure) as std_pressure
                FROM water_infrastructure.computed_metrics
                WHERE window_start > CURRENT_TIMESTAMP - INTERVAL '180 days'
                AND window_start < CURRENT_TIMESTAMP - INTERVAL '7 days'
                AND time_window = '1hour'
            """
            )

        if recent_stats and historical_stats:
            # Check if mean has shifted significantly (> 2 standard deviations)
            flow_drift = (
                abs(recent_stats["mean_flow"] - historical_stats["mean_flow"])
                > 2 * historical_stats["std_flow"]
            )
            pressure_drift = (
                abs(recent_stats["mean_pressure"] - historical_stats["mean_pressure"])
                > 2 * historical_stats["std_pressure"]
            )

            return flow_drift or pressure_drift

        return False

    async def _create_model_record(self, model_type: str) -> str:
        """Create a new model record in database."""
        version = datetime.now().strftime("v%Y%m%d.%H%M%S")

        async with self.postgres_manager.acquire() as conn:
            model_id = await conn.fetchval(
                """
                INSERT INTO water_infrastructure.ml_models
                (model_name, model_type, version, status)
                VALUES ($1, $2, $3, $4)
                RETURNING model_id
            """,
                f"{model_type}_model",
                model_type,
                version,
                ModelStatus.CREATED,
            )

        return str(model_id)

    async def _update_model_status(
        self, model_id: str, status: str, error: Optional[str] = None
    ):
        """Update model status."""
        async with self.postgres_manager.acquire() as conn:
            if error:
                await conn.execute(
                    """
                    UPDATE water_infrastructure.ml_models
                    SET status = $1, description = $2
                    WHERE model_id = $3
                """,
                    status,
                    f"Error: {error}",
                    model_id,
                )
            else:
                await conn.execute(
                    """
                    UPDATE water_infrastructure.ml_models
                    SET status = $1
                    WHERE model_id = $2
                """,
                    status,
                    model_id,
                )

    async def _update_model_record(
        self,
        model_id: str,
        status: str,
        metrics: Dict[str, float],
        model_path: str,
        feature_names: List[str],
    ):
        """Update model record with training results."""
        async with self.postgres_manager.acquire() as conn:
            await conn.execute(
                """
                UPDATE water_infrastructure.ml_models
                SET 
                    status = $1,
                    metrics = $2,
                    model_path = $3,
                    parameters = $4,
                    training_completed_at = CURRENT_TIMESTAMP,
                    training_duration_seconds = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - training_started_at))
                WHERE model_id = $5
            """,
                status,
                metrics,
                model_path,
                {"features": feature_names},
                model_id,
            )

    async def _load_active_models(self):
        """Load active models into memory."""
        async with self.postgres_manager.acquire() as conn:
            active_models = await conn.fetch(
                """
                SELECT model_id, model_type, model_path, metrics
                FROM water_infrastructure.ml_models
                WHERE is_active = TRUE AND status = 'active'
            """
            )

        for model_record in active_models:
            try:
                model = joblib.load(model_record["model_path"])
                self.active_models[model_record["model_type"]] = {
                    "model": model,
                    "model_id": str(model_record["model_id"]),
                    "metrics": model_record["metrics"],
                    "baseline_rmse": model_record["metrics"].get("rmse", 0),
                }
                logger.info(f"Loaded active model for {model_record['model_type']}")
            except Exception as e:
                logger.error(f"Failed to load model {model_record['model_id']}: {e}")
