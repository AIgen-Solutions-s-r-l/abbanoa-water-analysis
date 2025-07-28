#!/usr/bin/env python3
"""
Proof of Concept: ML-based Anomaly Detection for Water Infrastructure
This demonstrates how to detect anomalies in real-time sensor data
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import asyncpg
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WaterAnomalyDetector:
    """
    ML-based anomaly detection for water infrastructure
    Combines statistical methods with machine learning
    """
    
    def __init__(self, contamination=0.01):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_fitted = False
        
    def prepare_features(self, df):
        """
        Feature engineering for anomaly detection
        """
        features = pd.DataFrame()
        
        # Basic measurements
        features['flow_rate'] = df['flow_rate']
        features['pressure'] = df['pressure']
        features['temperature'] = df['temperature']
        
        # Rolling statistics (detect sudden changes)
        for window in [5, 15, 30]:  # 5min, 15min, 30min windows
            features[f'flow_rate_ma_{window}'] = df['flow_rate'].rolling(window).mean()
            features[f'flow_rate_std_{window}'] = df['flow_rate'].rolling(window).std()
            features[f'pressure_ma_{window}'] = df['pressure'].rolling(window).mean()
            features[f'pressure_std_{window}'] = df['pressure'].rolling(window).std()
        
        # Rate of change
        features['flow_rate_change'] = df['flow_rate'].diff()
        features['pressure_change'] = df['pressure'].diff()
        
        # Time-based features
        features['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        features['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Interaction features
        features['flow_pressure_ratio'] = df['flow_rate'] / (df['pressure'] + 0.1)
        features['flow_temp_product'] = df['flow_rate'] * df['temperature']
        
        # Handle missing values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def fit(self, training_data):
        """
        Train the anomaly detection model
        """
        logger.info("Training anomaly detection model...")
        
        # Prepare features
        X = self.prepare_features(training_data)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train isolation forest
        self.isolation_forest.fit(X_scaled)
        self.is_fitted = True
        
        logger.info(f"Model trained on {len(training_data)} samples")
        return self
    
    def predict(self, data, return_scores=False):
        """
        Predict anomalies in new data
        Returns: -1 for anomalies, 1 for normal
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Prepare features
        X = self.prepare_features(data)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.isolation_forest.predict(X_scaled)
        
        if return_scores:
            scores = self.isolation_forest.score_samples(X_scaled)
            return predictions, scores
        
        return predictions
    
    def detect_anomaly_types(self, data, predictions):
        """
        Classify types of anomalies detected
        """
        anomaly_types = []
        
        for idx in np.where(predictions == -1)[0]:
            if idx >= len(data):
                continue
                
            row = data.iloc[idx]
            anomaly_type = []
            
            # Sudden pressure drop (potential leak)
            if idx > 0 and row['pressure'] < data.iloc[idx-1]['pressure'] * 0.8:
                anomaly_type.append('SUDDEN_PRESSURE_DROP')
            
            # Abnormal flow rate
            if row['flow_rate'] > data['flow_rate'].quantile(0.99):
                anomaly_type.append('HIGH_FLOW')
            elif row['flow_rate'] < data['flow_rate'].quantile(0.01):
                anomaly_type.append('LOW_FLOW')
            
            # Night time high consumption
            hour = pd.to_datetime(row['timestamp']).hour
            if 2 <= hour <= 5 and row['flow_rate'] > data['flow_rate'].median():
                anomaly_type.append('NIGHT_CONSUMPTION')
            
            # Temperature anomaly
            if row['temperature'] > 30 or row['temperature'] < 5:
                anomaly_type.append('TEMPERATURE_ANOMALY')
            
            if not anomaly_type:
                anomaly_type.append('GENERAL_ANOMALY')
            
            anomaly_types.append({
                'timestamp': row['timestamp'],
                'node_id': row.get('node_id', 'unknown'),
                'types': anomaly_type,
                'flow_rate': row['flow_rate'],
                'pressure': row['pressure'],
                'temperature': row['temperature']
            })
        
        return anomaly_types


async def fetch_training_data(conn, node_id, days=7):
    """
    Fetch historical data for training
    """
    query = """
        SELECT timestamp, node_id, flow_rate, pressure, temperature
        FROM water_infrastructure.sensor_readings
        WHERE node_id = $1 
        AND timestamp > CURRENT_TIMESTAMP - INTERVAL '%s days'
        ORDER BY timestamp
    """ % days
    
    rows = await conn.fetch(query, node_id)
    return pd.DataFrame(rows)


async def fetch_recent_data(conn, node_id, minutes=60):
    """
    Fetch recent data for anomaly detection
    """
    query = """
        SELECT timestamp, node_id, flow_rate, pressure, temperature
        FROM water_infrastructure.sensor_readings
        WHERE node_id = $1 
        AND timestamp > CURRENT_TIMESTAMP - INTERVAL '%s minutes'
        ORDER BY timestamp
    """ % minutes
    
    rows = await conn.fetch(query, node_id)
    return pd.DataFrame(rows)


def visualize_anomalies(data, predictions, scores=None):
    """
    Visualize detected anomalies
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Mark anomalies
    anomaly_mask = predictions == -1
    
    # Flow rate
    axes[0].plot(data['timestamp'], data['flow_rate'], 'b-', alpha=0.7, label='Normal')
    axes[0].scatter(data.loc[anomaly_mask, 'timestamp'], 
                   data.loc[anomaly_mask, 'flow_rate'], 
                   color='red', s=50, label='Anomaly')
    axes[0].set_ylabel('Flow Rate (L/s)')
    axes[0].legend()
    axes[0].set_title('Anomaly Detection Results')
    
    # Pressure
    axes[1].plot(data['timestamp'], data['pressure'], 'g-', alpha=0.7)
    axes[1].scatter(data.loc[anomaly_mask, 'timestamp'], 
                   data.loc[anomaly_mask, 'pressure'], 
                   color='red', s=50)
    axes[1].set_ylabel('Pressure (bar)')
    
    # Anomaly scores
    if scores is not None:
        axes[2].plot(data['timestamp'], scores, 'purple', alpha=0.7)
        axes[2].axhline(y=0, color='r', linestyle='--', label='Threshold')
        axes[2].set_ylabel('Anomaly Score')
        axes[2].set_xlabel('Time')
        axes[2].legend()
    
    plt.tight_layout()
    plt.show()


async def main():
    """
    Demo anomaly detection on water infrastructure data
    """
    # Database connection
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5434,
        'database': 'postgres',
        'user': 'abbanoa_user',
        'password': 'abbanoa_2024'
    }
    
    try:
        # Connect to database
        conn = await asyncpg.connect(**DB_CONFIG)
        logger.info("Connected to database")
        
        # Select a node for analysis
        node_id = 'DIST_001'  # Example node
        
        # Fetch training data (last 7 days)
        logger.info(f"Fetching training data for node {node_id}...")
        training_data = await fetch_training_data(conn, node_id, days=7)
        
        if len(training_data) < 100:
            logger.warning("Insufficient training data. Using synthetic data for demo.")
            # Generate synthetic data for demonstration
            dates = pd.date_range(end=datetime.now(), periods=2000, freq='5min')
            training_data = pd.DataFrame({
                'timestamp': dates,
                'node_id': node_id,
                'flow_rate': np.random.normal(50, 10, 2000) + 10*np.sin(np.arange(2000)/50),
                'pressure': np.random.normal(5, 0.5, 2000),
                'temperature': np.random.normal(20, 2, 2000)
            })
            # Add some anomalies
            anomaly_indices = np.random.choice(2000, 20, replace=False)
            training_data.loc[anomaly_indices, 'flow_rate'] *= np.random.uniform(0.3, 2.5, 20)
            training_data.loc[anomaly_indices, 'pressure'] *= np.random.uniform(0.5, 1.5, 20)
        
        # Initialize and train model
        detector = WaterAnomalyDetector(contamination=0.02)
        detector.fit(training_data)
        
        # Fetch recent data for prediction
        logger.info("Fetching recent data for anomaly detection...")
        recent_data = await fetch_recent_data(conn, node_id, minutes=60)
        
        if len(recent_data) < 10:
            logger.warning("Insufficient recent data. Using last part of training data.")
            recent_data = training_data.tail(200).copy()
        
        # Detect anomalies
        predictions, scores = detector.predict(recent_data, return_scores=True)
        
        # Classify anomaly types
        anomaly_types = detector.detect_anomaly_types(recent_data, predictions)
        
        # Report results
        n_anomalies = sum(predictions == -1)
        logger.info(f"Detected {n_anomalies} anomalies out of {len(predictions)} readings")
        
        if anomaly_types:
            logger.info("\nDetailed anomaly report:")
            for anomaly in anomaly_types[:5]:  # Show first 5
                logger.info(f"  {anomaly['timestamp']}: {', '.join(anomaly['types'])}")
                logger.info(f"    Flow: {anomaly['flow_rate']:.2f} L/s, "
                          f"Pressure: {anomaly['pressure']:.2f} bar")
        
        # Visualize results
        recent_data['timestamp'] = pd.to_datetime(recent_data['timestamp'])
        visualize_anomalies(recent_data, predictions, scores)
        
        # Calculate potential savings
        avg_flow = recent_data['flow_rate'].mean()
        leak_flow_estimate = avg_flow * 0.05  # Assume 5% water loss
        water_cost_per_m3 = 1.5  # EUR per cubic meter
        
        daily_loss_m3 = leak_flow_estimate * 86.4  # L/s to m³/day
        annual_savings = daily_loss_m3 * 365 * water_cost_per_m3
        
        logger.info(f"\nPotential annual savings from leak detection: €{annual_savings:,.0f}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        if 'conn' in locals():
            await conn.close()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main()) 