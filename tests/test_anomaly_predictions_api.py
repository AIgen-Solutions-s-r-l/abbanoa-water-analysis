"""Test anomaly predictions with real database data"""

import asyncio
import asyncpg
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.repositories.anomaly_prediction_repository import (
    AnomalyPredictionRepository
)


async def test_real_data():
    """Test fetching real data from database"""
    
    # Database connection
    POSTGRES_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "database": "abbanoa_processing",
        "user": "abbanoa_user",
        "password": "abbanoa_secure_pass",
    }
    
    # Create connection pool
    pool = await asyncpg.create_pool(**POSTGRES_CONFIG)
    
    try:
        # Initialize repository
        repo = AnomalyPredictionRepository(pool)
        
        print("=" * 60)
        print("TESTING ANOMALY PREDICTIONS WITH REAL DATABASE DATA")
        print("=" * 60)
        
        # 1. Get active nodes
        print("\n1. Active Nodes:")
        active_nodes = await repo.get_active_nodes()
        print(f"   Found {len(active_nodes)} active nodes: {active_nodes[:5]}")
        
        # 2. Get sensor data for first node
        if active_nodes:
            node_id = active_nodes[0]
            print(f"\n2. Sensor Data for {node_id}:")
            sensor_data = await repo.get_sensor_data_for_node(node_id, hours_back=24)
            print(f"   Records: {len(sensor_data)}")
            if not sensor_data.empty:
                print(f"   Columns: {list(sensor_data.columns)}")
                print(f"   Latest reading:")
                latest = sensor_data.iloc[0]
                print(f"     - Timestamp: {latest['timestamp']}")
                print(f"     - Pressure: {latest['pressure']:.2f}")
                print(f"     - Flow Rate: {latest['flow_rate']:.2f}")
        
        # 3. Get historical anomalies
        print("\n3. Historical Anomalies (last 30 days):")
        anomalies = await repo.get_historical_anomalies(days_back=30)
        print(f"   Total anomalies: {len(anomalies)}")
        if not anomalies.empty:
            print(f"   Anomaly types: {anomalies['anomaly_type'].value_counts().to_dict()}")
            print(f"   Severity distribution: {anomalies['severity'].value_counts().to_dict()}")
            print(f"   Affected nodes: {anomalies['node_id'].nunique()}")
        
        # 4. Get training data
        print("\n4. Training Data Preparation:")
        training_data = await repo.get_training_data(days_back=7)
        print(f"   Sensor samples: {len(training_data.sensor_data)}")
        print(f"   Anomaly labels: {len(training_data.anomaly_labels)}")
        if not training_data.sensor_data.empty:
            if 'has_anomaly' in training_data.sensor_data.columns:
                anomaly_rate = training_data.sensor_data['has_anomaly'].mean()
                print(f"   Anomaly rate: {anomaly_rate:.2%}")
        print(f"   Node info available: {len(training_data.node_info)} nodes")
        
        # 5. Get node statistics
        if active_nodes:
            print(f"\n5. Node Statistics for {active_nodes[0]}:")
            stats = await repo.get_node_statistics(active_nodes[0])
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"   - {key}: {value:.2f}")
                else:
                    print(f"   - {key}: {value}")
        
        # 6. Test saving a prediction
        print("\n6. Testing Prediction Save:")
        if active_nodes:
            prediction_id = await repo.save_prediction(
                node_id=active_nodes[0],
                probability=0.75,
                predicted_time=datetime.now() + timedelta(hours=3),
                confidence="HIGH",
                risk_factors=["pressure_spike", "flow_anomaly"],
                model_version="test_v1.0"
            )
            print(f"   Saved prediction with ID: {prediction_id}")
        
        # 7. Check recent sensor data for all nodes
        print("\n7. Recent Sensor Data Summary:")
        recent_data = await repo.get_recent_sensor_data_all_nodes(hours_back=6)
        for node_id, data in recent_data.items():
            if not data.empty:
                avg_pressure = data['pressure'].mean()
                avg_flow = data['flow_rate'].mean()
                print(f"   {node_id}:")
                print(f"     - Records: {len(data)}")
                print(f"     - Avg Pressure: {avg_pressure:.2f}")
                print(f"     - Avg Flow: {avg_flow:.2f}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(test_real_data())