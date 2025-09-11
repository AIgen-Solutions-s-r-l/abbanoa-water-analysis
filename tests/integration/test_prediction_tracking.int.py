"""Integration tests for prediction tracking system"""

import pytest
import asyncio
import asyncpg
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.infrastructure.repositories.tracking_repository_extension import TrackingRepositoryExtension
from src.application.services.prediction_tracker import PredictionTracker


@pytest.fixture
async def db_pool():
    """Create test database connection pool"""
    config = {
        "host": "localhost",
        "port": 5432,
        "database": "abbanoa_processing",
        "user": "abbanoa_user",
        "password": "abbanoa_secure_pass",
    }
    
    pool = await asyncpg.create_pool(**config)
    yield pool
    await pool.close()


@pytest.fixture
async def tracking_repo(db_pool):
    """Create tracking repository with real database"""
    return TrackingRepositoryExtension(db_pool)


@pytest.fixture
async def prediction_tracker(tracking_repo):
    """Create prediction tracker with real repository"""
    return PredictionTracker(repository=tracking_repo)


class TestPredictionTrackingIntegration:
    """Integration tests with real database"""
    
    @pytest.mark.asyncio
    async def test_save_and_retrieve_prediction_outcome(self, tracking_repo):
        """Test saving prediction outcome to database"""
        # Create a test prediction first
        create_prediction = """
            INSERT INTO water_infrastructure.ml_predictions 
            (node_id, probability, predicted_timestamp, confidence, risk_factors, model_version, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING prediction_id
        """
        
        async with tracking_repo.pool.acquire() as conn:
            # Insert test prediction
            row = await conn.fetchrow(
                create_prediction,
                'TEST_NODE_001',
                0.85,
                datetime.now() + timedelta(hours=2),
                'HIGH',
                ['pressure_spike'],
                'test_v1.0',
                '{"test": true}'
            )
            prediction_id = row['prediction_id']
        
        # Test outcome update
        await tracking_repo.update_prediction_outcome(
            prediction_id=prediction_id,
            actual_occurred=True,
            feedback_source='integration_test'
        )
        
        # Verify outcome was saved
        prediction = await tracking_repo.get_prediction(prediction_id)
        
        assert prediction is not None
        assert prediction['actual_occurred'] == True
        assert prediction['feedback_source'] == 'integration_test'
        assert prediction['feedback_at'] is not None
        
        # Cleanup
        async with tracking_repo.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM water_infrastructure.ml_predictions WHERE prediction_id = $1",
                prediction_id
            )
    
    @pytest.mark.asyncio
    async def test_batch_outcome_updates(self, tracking_repo):
        """Test batch updating multiple prediction outcomes"""
        # Create multiple test predictions
        create_query = """
            INSERT INTO water_infrastructure.ml_predictions 
            (node_id, probability, predicted_timestamp, confidence, risk_factors, model_version, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING prediction_id
        """
        
        prediction_ids = []
        async with tracking_repo.pool.acquire() as conn:
            for i in range(3):
                row = await conn.fetchrow(
                    create_query,
                    f'TEST_NODE_{i:03d}',
                    0.7 + i * 0.1,
                    datetime.now() + timedelta(hours=i+1),
                    'HIGH',
                    ['test_factor'],
                    'test_v1.0',
                    '{"test": true}'
                )
                prediction_ids.append(row['prediction_id'])
        
        # Test batch update
        outcome_updates = [
            (prediction_ids[0], True, 'batch_test'),
            (prediction_ids[1], False, 'batch_test'),
            (prediction_ids[2], True, 'batch_test')
        ]
        
        await tracking_repo.batch_update_outcomes(outcome_updates)
        
        # Verify all outcomes were updated
        for i, prediction_id in enumerate(prediction_ids):
            prediction = await tracking_repo.get_prediction(prediction_id)
            expected_outcome = outcome_updates[i][1]
            
            assert prediction['actual_occurred'] == expected_outcome
            assert prediction['feedback_source'] == 'batch_test'
        
        # Cleanup
        async with tracking_repo.pool.acquire() as conn:
            for prediction_id in prediction_ids:
                await conn.execute(
                    "DELETE FROM water_infrastructure.ml_predictions WHERE prediction_id = $1",
                    prediction_id
                )
    
    @pytest.mark.asyncio
    async def test_performance_metrics_calculation(self, tracking_repo, prediction_tracker):
        """Test metrics calculation with real data"""
        # Create test predictions with known outcomes
        test_data = [
            ('NODE_A', 0.9, True, True),   # True positive
            ('NODE_B', 0.8, True, False),  # False positive
            ('NODE_C', 0.2, False, False), # True negative
            ('NODE_D', 0.1, False, True),  # False negative
        ]
        
        prediction_ids = []
        
        # Insert test predictions with outcomes
        async with tracking_repo.pool.acquire() as conn:
            for node_id, prob, predicted, actual in test_data:
                # Insert prediction
                row = await conn.fetchrow(
                    """INSERT INTO water_infrastructure.ml_predictions 
                       (node_id, probability, predicted_timestamp, confidence, 
                        actual_occurred, feedback_at, feedback_source)
                       VALUES ($1, $2, $3, $4, $5, NOW(), $6)
                       RETURNING prediction_id""",
                    node_id, prob, datetime.now() - timedelta(hours=1),
                    'HIGH', actual, 'test_metrics'
                )
                prediction_ids.append(row['prediction_id'])
        
        # Calculate metrics
        metrics = await prediction_tracker.calculate_metrics(days_back=1)
        
        # Verify metrics
        assert metrics.precision == 1/2  # 1 TP / (1 TP + 1 FP)
        assert metrics.recall == 1/2     # 1 TP / (1 TP + 1 FN)
        assert metrics.accuracy == 2/4   # (1 TP + 1 TN) / 4
        assert abs(metrics.f1_score - 0.5) < 0.01  # 2 * (0.5 * 0.5) / (0.5 + 0.5)
        
        # Cleanup
        async with tracking_repo.pool.acquire() as conn:
            for prediction_id in prediction_ids:
                await conn.execute(
                    "DELETE FROM water_infrastructure.ml_predictions WHERE prediction_id = $1",
                    prediction_id
                )
    
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, tracking_repo):
        """Test transaction rollback on database errors"""
        prediction_id = 99999  # Non-existent prediction
        
        # This should fail and rollback
        with pytest.raises(Exception):
            await tracking_repo.update_prediction_outcome(
                prediction_id=prediction_id,
                actual_occurred=True,
                feedback_source='rollback_test'
            )
        
        # Verify no partial updates occurred
        prediction = await tracking_repo.get_prediction(prediction_id)
        assert prediction is None
    
    @pytest.mark.asyncio
    async def test_database_indexes_exist(self, tracking_repo):
        """Test that required database indexes exist for performance"""
        # Check for indexes on ml_predictions table
        index_query = """
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'ml_predictions' 
                AND schemaname = 'water_infrastructure'
        """
        
        async with tracking_repo.pool.acquire() as conn:
            rows = await conn.fetch(index_query)
            
            # Should have at least primary key index
            assert len(rows) > 0
            
            # Look for performance-critical indexes
            index_names = [row['indexname'] for row in rows]
            
            # At minimum should have primary key
            primary_key_exists = any('pkey' in idx for idx in index_names)
            assert primary_key_exists, "Primary key index should exist"
    
    @pytest.mark.asyncio
    async def test_concurrent_updates(self, tracking_repo):
        """Test handling concurrent prediction updates"""
        # Create test prediction
        async with tracking_repo.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO water_infrastructure.ml_predictions 
                   (node_id, probability, predicted_timestamp, confidence)
                   VALUES ($1, $2, $3, $4) RETURNING prediction_id""",
                'CONCURRENT_NODE', 0.8, datetime.now() + timedelta(hours=1), 'HIGH'
            )
            prediction_id = row['prediction_id']
        
        # Simulate concurrent updates
        async def update_outcome(outcome, source):
            await tracking_repo.update_prediction_outcome(
                prediction_id=prediction_id,
                actual_occurred=outcome,
                feedback_source=source
            )
        
        # Run concurrent updates
        tasks = [
            update_outcome(True, 'concurrent_1'),
            update_outcome(False, 'concurrent_2'),
            update_outcome(True, 'concurrent_3')
        ]
        
        # Should complete without deadlocks
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify final state is consistent
        prediction = await tracking_repo.get_prediction(prediction_id)
        assert prediction is not None
        assert prediction['actual_occurred'] is not None
        assert prediction['feedback_source'] is not None
        
        # Cleanup
        async with tracking_repo.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM water_infrastructure.ml_predictions WHERE prediction_id = $1",
                prediction_id
            )