"""Unit tests for quality thresholds configuration."""

import os
import tempfile
import pytest
from unittest.mock import patch
from src.config.quality_thresholds import (
    QualityThresholdsConfig,
    TemperatureThresholds,
    PressureThresholds,
    FlowThresholds,
    QualityScoreThresholds,
    QualityGradeThresholds,
    ComplianceThresholds,
    DataQualityThresholds,
    QualityGrade,
    get_quality_config,
    reset_config
)


class TestTemperatureThresholds:
    """Test temperature thresholds configuration."""
    
    def test_default_values(self):
        """Test default temperature threshold values."""
        config = TemperatureThresholds()
        assert config.optimal == 15.0
        assert config.min_normal == 10.0
        assert config.max_normal == 20.0
        assert config.alert_threshold == 25.0
        assert config.high_alert_threshold == 30.0
    
    def test_custom_values(self):
        """Test custom temperature threshold values."""
        config = TemperatureThresholds(
            optimal=16.0,
            min_normal=12.0,
            max_normal=22.0
        )
        assert config.optimal == 16.0
        assert config.min_normal == 12.0
        assert config.max_normal == 22.0
    
    def test_validation_min_normal(self):
        """Test validation that min_normal < optimal."""
        with pytest.raises(ValueError, match="min_normal must be less than optimal"):
            TemperatureThresholds(optimal=15.0, min_normal=20.0)
    
    def test_validation_max_normal(self):
        """Test validation that max_normal > optimal."""
        with pytest.raises(ValueError, match="max_normal must be greater than optimal"):
            TemperatureThresholds(optimal=15.0, max_normal=10.0)


class TestPressureThresholds:
    """Test pressure thresholds configuration."""
    
    def test_default_values(self):
        """Test default pressure threshold values."""
        config = PressureThresholds()
        assert config.optimal == 4.0
        assert config.minimum == 2.0
        assert config.critical == 1.0
        assert config.maximum == 6.0
        assert config.normal_min == 3.0
        assert config.normal_max == 5.0
    
    def test_validation_minimum(self):
        """Test validation that minimum > critical."""
        with pytest.raises(ValueError, match="minimum must be greater than critical"):
            PressureThresholds(critical=2.0, minimum=1.5)


class TestFlowThresholds:
    """Test flow thresholds configuration."""
    
    def test_default_values(self):
        """Test default flow threshold values."""
        config = FlowThresholds()
        assert config.minimum == 0.1
        assert config.stagnation == 0.5
        assert config.normal_min == 50.0
        assert config.normal_max == 150.0
        assert config.normal_value == 100.0
        assert config.maximum == 10000.0


class TestQualityScoreThresholds:
    """Test quality score thresholds configuration."""
    
    def test_default_values(self):
        """Test default quality score threshold values."""
        config = QualityScoreThresholds()
        assert config.excellent == 0.9
        assert config.good == 0.7
        assert config.acceptable == 0.6
        assert config.minimum == 0.85
        assert config.normal == 0.95
        assert config.maximum == 1.0
    
    def test_value_bounds(self):
        """Test that values are constrained between 0 and 1."""
        with pytest.raises(ValueError):
            QualityScoreThresholds(excellent=1.5)
        
        with pytest.raises(ValueError):
            QualityScoreThresholds(good=-0.1)
    
    def test_validation_hierarchy(self):
        """Test validation that thresholds are in correct order."""
        with pytest.raises(ValueError, match="good threshold must be less than excellent"):
            QualityScoreThresholds(excellent=0.8, good=0.9)
        
        with pytest.raises(ValueError, match="acceptable threshold must be less than good"):
            QualityScoreThresholds(good=0.6, acceptable=0.7)


class TestQualityGradeThresholds:
    """Test quality grade thresholds configuration."""
    
    def test_default_values(self):
        """Test default grade threshold values."""
        config = QualityGradeThresholds()
        assert config.grade_a == 90.0
        assert config.grade_b == 80.0
        assert config.grade_c == 70.0
        assert config.grade_d == 60.0
    
    def test_get_grade(self):
        """Test grade determination based on percentage."""
        config = QualityGradeThresholds()
        
        assert config.get_grade(95.0) == QualityGrade.A
        assert config.get_grade(90.0) == QualityGrade.A
        assert config.get_grade(85.0) == QualityGrade.B
        assert config.get_grade(75.0) == QualityGrade.C
        assert config.get_grade(65.0) == QualityGrade.D
        assert config.get_grade(55.0) == QualityGrade.F
        assert config.get_grade(0.0) == QualityGrade.F


class TestComplianceThresholds:
    """Test compliance thresholds configuration."""
    
    def test_default_values(self):
        """Test default compliance threshold values."""
        config = ComplianceThresholds()
        assert config.quality_warning == 90.0
        assert config.quality_target == 98.0
        assert config.temperature_warning == 95.0
        assert config.temperature_target == 99.0
        assert config.pressure_warning == 90.0
        assert config.pressure_target == 95.0
        assert config.contamination_warning == 5
        assert config.contamination_target == 0


class TestDataQualityThresholds:
    """Test data quality thresholds configuration."""
    
    def test_default_values(self):
        """Test default data quality threshold values."""
        config = DataQualityThresholds()
        assert config.min_completeness == 95.0
        assert config.outlier_sigma == 3.0
        assert config.uptime_target == 99.0
        assert config.prediction_accuracy_min == 95.0
        assert config.prediction_accuracy_target == 99.0


class TestQualityThresholdsConfig:
    """Test main quality thresholds configuration."""
    
    def test_default_initialization(self):
        """Test that configuration initializes with all defaults."""
        config = QualityThresholdsConfig()
        
        assert isinstance(config.temperature, TemperatureThresholds)
        assert isinstance(config.pressure, PressureThresholds)
        assert isinstance(config.flow, FlowThresholds)
        assert isinstance(config.quality_score, QualityScoreThresholds)
        assert isinstance(config.quality_grades, QualityGradeThresholds)
        assert isinstance(config.compliance, ComplianceThresholds)
        assert isinstance(config.data_quality, DataQualityThresholds)
    
    def test_partial_initialization(self):
        """Test partial configuration with some custom values."""
        config = QualityThresholdsConfig(
            temperature=TemperatureThresholds(optimal=16.0),
            pressure=PressureThresholds(minimum=2.5)
        )
        
        assert config.temperature.optimal == 16.0
        assert config.pressure.minimum == 2.5
        # Other values should be defaults
        assert config.flow.minimum == 0.1
    
    def test_from_env(self):
        """Test loading configuration from environment variables."""
        env_vars = {
            "QUALITY_THRESHOLDS_TEMPERATURE__OPTIMAL": "16.5",
            "QUALITY_THRESHOLDS_PRESSURE__MINIMUM": "2.5",
            "QUALITY_THRESHOLDS_FLOW__NORMAL_VALUE": "110.0",
            "QUALITY_THRESHOLDS_COMPLIANCE__CONTAMINATION_TARGET": "1",
        }
        
        with patch.dict(os.environ, env_vars):
            config = QualityThresholdsConfig.from_env()
            
            assert config.temperature.optimal == 16.5
            assert config.pressure.minimum == 2.5
            assert config.flow.normal_value == 110.0
            assert config.compliance.contamination_target == 1
    
    def test_from_yaml(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
temperature:
  optimal: 17.0
  min_normal: 12.0
pressure:
  minimum: 2.2
quality_score:
  excellent: 0.95
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            f.flush()
            
            config = QualityThresholdsConfig.from_yaml(f.name)
            
            assert config.temperature.optimal == 17.0
            assert config.temperature.min_normal == 12.0
            assert config.pressure.minimum == 2.2
            assert config.quality_score.excellent == 0.95
            
            # Clean up
            os.unlink(f.name)
    
    def test_to_yaml(self):
        """Test saving configuration to YAML file."""
        config = QualityThresholdsConfig(
            temperature=TemperatureThresholds(optimal=18.0)
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config.to_yaml(f.name)
            
            # Read back and verify
            loaded_config = QualityThresholdsConfig.from_yaml(f.name)
            assert loaded_config.temperature.optimal == 18.0
            
            # Clean up
            os.unlink(f.name)


class TestConfigSingleton:
    """Test configuration singleton pattern."""
    
    def setup_method(self):
        """Reset configuration before each test."""
        reset_config()
    
    def test_get_quality_config_returns_singleton(self):
        """Test that get_quality_config returns the same instance."""
        config1 = get_quality_config()
        config2 = get_quality_config()
        
        assert config1 is config2
    
    def test_get_quality_config_loads_from_env(self):
        """Test that singleton loads from environment variables."""
        env_vars = {
            "QUALITY_THRESHOLDS_TEMPERATURE__OPTIMAL": "19.0",
        }
        
        with patch.dict(os.environ, env_vars):
            config = get_quality_config()
            assert config.temperature.optimal == 19.0
    
    def test_reset_config(self):
        """Test that reset_config clears the singleton."""
        config1 = get_quality_config()
        reset_config()
        config2 = get_quality_config()
        
        assert config1 is not config2