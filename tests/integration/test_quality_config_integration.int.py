"""Integration tests for quality configuration system."""

import os
import sys
from unittest.mock import MagicMock, patch

# Mock Google Cloud dependencies
sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.bigquery'] = MagicMock()

import pytest
from src.config.quality_thresholds import (
    QualityThresholdsConfig,
    get_quality_config,
    reset_config
)


class TestQualityConfigIntegration:
    """Integration tests for quality configuration system."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_config()
    
    def test_configuration_loads_with_defaults(self):
        """Test that configuration loads with default values."""
        config = get_quality_config()
        
        assert config is not None
        assert config.temperature.optimal == 15.0
        assert config.pressure.minimum == 2.0
        assert config.compliance.quality_warning == 90.0
    
    def test_configuration_singleton_pattern(self):
        """Test that configuration follows singleton pattern."""
        config1 = get_quality_config()
        config2 = get_quality_config()
        
        assert config1 is config2
    
    def test_environment_variable_override(self):
        """Test configuration override via environment variables."""
        # Set environment variables
        os.environ['QUALITY_THRESHOLDS_TEMPERATURE__OPTIMAL'] = '18.0'
        os.environ['QUALITY_THRESHOLDS_PRESSURE__MINIMUM'] = '2.5'
        
        # Reset and reload configuration
        reset_config()
        config = get_quality_config()
        
        assert config.temperature.optimal == 18.0
        assert config.pressure.minimum == 2.5
        
        # Clean up environment
        del os.environ['QUALITY_THRESHOLDS_TEMPERATURE__OPTIMAL']
        del os.environ['QUALITY_THRESHOLDS_PRESSURE__MINIMUM']
    
    @patch('src.api.services.water_quality_service.get_quality_config')
    def test_water_quality_service_uses_config(self, mock_get_config):
        """Test that water quality service uses configuration."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.temperature.optimal = 16.0
        mock_config.temperature.alert_threshold = 26.0
        mock_get_config.return_value = mock_config
        
        # Import service after mocking
        from src.api.services.water_quality_service import generate_quality_alerts
        import pandas as pd
        import numpy as np
        from datetime import datetime
        
        # Create test data
        data = pd.DataFrame({
            'timestamp': pd.date_range(start=datetime.now(), periods=5, freq='H'),
            'node_id': ['NODE_001'] * 5,
            'temperature': [15, 20, 27, 30, 25],  # Some above threshold
            'pressure': [3, 4, 2, 1, 3],
            'flow_rate': [100, 150, 80, 50, 120],
            'overall_quality': [0.9, 0.8, 0.7, 0.5, 0.6]
        })
        
        # Create mock metrics
        metrics = MagicMock()
        
        # Generate alerts (this should use the mocked config)
        alerts = generate_quality_alerts(data, metrics)
        
        # Verify configuration was used
        mock_get_config.assert_called()
    
    @patch('src.api.services.kpis.quality_service.get_quality_config')
    def test_quality_kpi_service_uses_config(self, mock_get_config):
        """Test that quality KPI service uses configuration."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.compliance.quality_warning = 85.0
        mock_config.compliance.contamination_warning = 3
        mock_get_config.return_value = mock_config
        
        # Import service after mocking
        from src.api.services.kpis.quality_service import QualityService
        from src.schemas.api.kpis import QualityKPIs
        from datetime import datetime
        
        # Create service instance
        service = QualityService()
        
        # Create test KPIs
        kpis = QualityKPIs(
            quality_compliance_percentage=80.0,  # Below mocked threshold
            contamination_incidents_count=5,  # Above mocked threshold
            temperature_compliance_percentage=96.0,
            pressure_compliance_percentage=91.0,
            flow_rate_compliance_percentage=93.0,
            quality_score=88.0,
            timestamp=datetime.now()
        )
        
        # Check alerts (this should use the mocked config)
        alerts = service.check_quality_alerts(kpis)
        
        # Verify configuration was used
        mock_get_config.assert_called()
    
    @patch('src.application.anomaly_detector.get_quality_config')
    def test_anomaly_detector_uses_config(self, mock_get_config):
        """Test that anomaly detector uses configuration."""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.pressure.minimum = 2.5
        mock_config.pressure.critical = 1.5
        mock_config.pressure.optimal = 4.5
        mock_config.flow.normal_min = 60.0
        mock_config.flow.normal_max = 140.0
        mock_config.flow.normal_value = 100.0
        mock_config.quality_score.minimum = 0.8
        mock_config.quality_score.maximum = 1.0
        mock_config.quality_score.normal = 0.9
        mock_config.temperature.min_normal = 12.0
        mock_config.temperature.max_normal = 22.0
        mock_config.temperature.optimal = 17.0
        mock_get_config.return_value = mock_config
        
        # Mock asyncpg connection
        mock_connection = MagicMock()
        
        # Import and create detector after mocking
        from src.application.anomaly_detector import AnomalyDetector
        
        detector = AnomalyDetector(mock_connection)
        
        # Verify configuration was used in initialization
        mock_get_config.assert_called()
        
        # Check that thresholds were set from config
        assert detector.thresholds['pressure']['minimum'] == 2.5
        assert detector.thresholds['pressure']['optimal'] == 4.5
        assert detector.thresholds['flow_rate']['normal_min'] == 60.0
        assert detector.thresholds['temperature']['optimal'] == 17.0
    
    def test_quality_grades_calculation(self):
        """Test quality grade calculation with configuration."""
        config = get_quality_config()
        
        # Test grade boundaries
        assert config.quality_grades.get_grade(95.0).value == 'A'
        assert config.quality_grades.get_grade(85.0).value == 'B'
        assert config.quality_grades.get_grade(75.0).value == 'C'
        assert config.quality_grades.get_grade(65.0).value == 'D'
        assert config.quality_grades.get_grade(55.0).value == 'F'
    
    def test_configuration_validation(self):
        """Test configuration validation rules."""
        # Test invalid temperature range (min > optimal)
        with pytest.raises(ValueError):
            QualityThresholdsConfig.model_validate({
                'temperature': {
                    'optimal': 15.0,
                    'min_normal': 20.0,  # Invalid: greater than optimal
                    'max_normal': 25.0
                }
            })
        
        # Test invalid pressure (minimum <= critical)
        with pytest.raises(ValueError):
            QualityThresholdsConfig.model_validate({
                'pressure': {
                    'critical': 2.0,
                    'minimum': 1.5  # Invalid: less than critical
                }
            })


if __name__ == '__main__':
    pytest.main([__file__, '-v'])