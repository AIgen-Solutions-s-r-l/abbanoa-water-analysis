"""Configuration for quality metrics and thresholds.

This module provides a centralized configuration system for all quality-related
thresholds and metrics, replacing hardcoded values throughout the application.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class QualityGrade(str, Enum):
    """Quality grade classifications."""
    A = "A"  # Excellent
    B = "B"  # Good
    C = "C"  # Acceptable
    D = "D"  # Poor
    F = "F"  # Failing


class TemperatureThresholds(BaseModel):
    """Temperature thresholds configuration."""
    optimal: float = Field(default=15.0, description="Optimal temperature in Celsius")
    min_normal: float = Field(default=10.0, description="Minimum normal temperature")
    max_normal: float = Field(default=20.0, description="Maximum normal temperature")
    alert_threshold: float = Field(default=25.0, description="Alert threshold temperature")
    high_alert_threshold: float = Field(default=30.0, description="High alert threshold")
    
    @validator('min_normal')
    def validate_min_normal(cls, v, values):
        if 'optimal' in values and v > values['optimal']:
            raise ValueError('min_normal must be less than optimal')
        return v
    
    @validator('max_normal')
    def validate_max_normal(cls, v, values):
        if 'optimal' in values and v < values['optimal']:
            raise ValueError('max_normal must be greater than optimal')
        return v


class PressureThresholds(BaseModel):
    """Pressure thresholds configuration in bar."""
    optimal: float = Field(default=4.0, description="Optimal pressure in bar")
    minimum: float = Field(default=2.0, description="Minimum acceptable pressure")
    critical: float = Field(default=1.0, description="Critical low pressure")
    maximum: float = Field(default=6.0, description="Maximum safe pressure")
    normal_min: float = Field(default=3.0, description="Normal range minimum")
    normal_max: float = Field(default=5.0, description="Normal range maximum")
    
    @validator('minimum')
    def validate_minimum(cls, v, values):
        if 'critical' in values and v <= values['critical']:
            raise ValueError('minimum must be greater than critical')
        return v


class FlowThresholds(BaseModel):
    """Flow rate thresholds configuration in L/s."""
    minimum: float = Field(default=0.1, description="Minimum flow rate")
    stagnation: float = Field(default=0.5, description="Stagnation threshold")
    normal_min: float = Field(default=50.0, description="Normal range minimum")
    normal_max: float = Field(default=150.0, description="Normal range maximum")
    normal_value: float = Field(default=100.0, description="Normal expected value")
    maximum: float = Field(default=10000.0, description="Maximum valid flow rate")


class QualityScoreThresholds(BaseModel):
    """Quality score thresholds (0.0 to 1.0)."""
    excellent: float = Field(default=0.9, ge=0.0, le=1.0, description="Excellent quality threshold")
    good: float = Field(default=0.7, ge=0.0, le=1.0, description="Good quality threshold")
    acceptable: float = Field(default=0.6, ge=0.0, le=1.0, description="Acceptable quality threshold")
    minimum: float = Field(default=0.85, ge=0.0, le=1.0, description="Minimum required quality")
    normal: float = Field(default=0.95, ge=0.0, le=1.0, description="Normal expected quality")
    maximum: float = Field(default=1.0, ge=0.0, le=1.0, description="Maximum quality score")
    
    @validator('good')
    def validate_good(cls, v, values):
        if 'excellent' in values and v >= values['excellent']:
            raise ValueError('good threshold must be less than excellent')
        return v
    
    @validator('acceptable')
    def validate_acceptable(cls, v, values):
        if 'good' in values and v >= values['good']:
            raise ValueError('acceptable threshold must be less than good')
        return v


class QualityGradeThresholds(BaseModel):
    """Quality grade thresholds as percentages."""
    grade_a: float = Field(default=90.0, ge=0.0, le=100.0, description="Grade A threshold (%)")
    grade_b: float = Field(default=80.0, ge=0.0, le=100.0, description="Grade B threshold (%)")
    grade_c: float = Field(default=70.0, ge=0.0, le=100.0, description="Grade C threshold (%)")
    grade_d: float = Field(default=60.0, ge=0.0, le=100.0, description="Grade D threshold (%)")
    
    def get_grade(self, percentage: float) -> QualityGrade:
        """Determine quality grade based on percentage."""
        if percentage >= self.grade_a:
            return QualityGrade.A
        elif percentage >= self.grade_b:
            return QualityGrade.B
        elif percentage >= self.grade_c:
            return QualityGrade.C
        elif percentage >= self.grade_d:
            return QualityGrade.D
        else:
            return QualityGrade.F


class ComplianceThresholds(BaseModel):
    """Compliance thresholds for KPIs."""
    quality_warning: float = Field(default=90.0, ge=0.0, le=100.0, description="Quality compliance warning (%)")
    quality_target: float = Field(default=98.0, ge=0.0, le=100.0, description="Quality compliance target (%)")
    temperature_warning: float = Field(default=95.0, ge=0.0, le=100.0, description="Temperature compliance warning (%)")
    temperature_target: float = Field(default=99.0, ge=0.0, le=100.0, description="Temperature compliance target (%)")
    pressure_warning: float = Field(default=90.0, ge=0.0, le=100.0, description="Pressure compliance warning (%)")
    pressure_target: float = Field(default=95.0, ge=0.0, le=100.0, description="Pressure compliance target (%)")
    contamination_warning: int = Field(default=5, ge=0, description="Contamination incidents warning threshold")
    contamination_target: int = Field(default=0, ge=0, description="Contamination incidents target")


class DataQualityThresholds(BaseModel):
    """Data quality thresholds for validation."""
    min_completeness: float = Field(default=95.0, ge=0.0, le=100.0, description="Minimum data completeness (%)")
    outlier_sigma: float = Field(default=3.0, gt=0, description="Sigma threshold for outlier detection")
    uptime_target: float = Field(default=99.0, ge=0.0, le=100.0, description="System uptime target (%)")
    prediction_accuracy_min: float = Field(default=95.0, ge=0.0, le=100.0, description="Minimum prediction accuracy (%)")
    prediction_accuracy_target: float = Field(default=99.0, ge=0.0, le=100.0, description="Target prediction accuracy (%)")


class QualityThresholdsConfig(BaseModel):
    """Main configuration class for all quality thresholds."""
    temperature: TemperatureThresholds = Field(default_factory=TemperatureThresholds)
    pressure: PressureThresholds = Field(default_factory=PressureThresholds)
    flow: FlowThresholds = Field(default_factory=FlowThresholds)
    quality_score: QualityScoreThresholds = Field(default_factory=QualityScoreThresholds)
    quality_grades: QualityGradeThresholds = Field(default_factory=QualityGradeThresholds)
    compliance: ComplianceThresholds = Field(default_factory=ComplianceThresholds)
    data_quality: DataQualityThresholds = Field(default_factory=DataQualityThresholds)
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        use_enum_values = True
    
    @classmethod
    def from_env(cls) -> "QualityThresholdsConfig":
        """Load configuration from environment variables.
        
        Environment variables should be prefixed with QUALITY_THRESHOLDS_
        and use double underscores for nested values.
        Example: QUALITY_THRESHOLDS_TEMPERATURE__OPTIMAL=16.0
        """
        import os
        from typing import Any
        
        config_dict: Dict[str, Any] = {}
        prefix = "QUALITY_THRESHOLDS_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(prefix):].lower()
                
                # Handle nested configuration with double underscores
                if "__" in config_key:
                    parts = config_key.split("__")
                    if len(parts) == 2:
                        section, param = parts
                        if section not in config_dict:
                            config_dict[section] = {}
                        
                        # Convert value to appropriate type
                        try:
                            # Try to convert to float first
                            config_dict[section][param] = float(value)
                        except ValueError:
                            try:
                                # Try to convert to int
                                config_dict[section][param] = int(value)
                            except ValueError:
                                # Keep as string
                                config_dict[section][param] = value
        
        return cls(**config_dict)
    
    @classmethod
    def from_yaml(cls, filepath: str) -> "QualityThresholdsConfig":
        """Load configuration from YAML file."""
        import yaml
        
        with open(filepath, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(**config_dict)
    
    def to_yaml(self, filepath: str) -> None:
        """Save configuration to YAML file."""
        import yaml
        
        with open(filepath, 'w') as f:
            yaml.dump(self.dict(), f, default_flow_style=False, sort_keys=False)


# Singleton instance
_config_instance: Optional[QualityThresholdsConfig] = None


def get_quality_config() -> QualityThresholdsConfig:
    """Get the singleton configuration instance.
    
    This function ensures a single configuration instance is used throughout
    the application. It first attempts to load from environment variables,
    then falls back to defaults.
    """
    global _config_instance
    
    if _config_instance is None:
        try:
            # Try to load from environment variables first
            _config_instance = QualityThresholdsConfig.from_env()
        except Exception:
            # Fall back to defaults
            _config_instance = QualityThresholdsConfig()
    
    return _config_instance


def reset_config() -> None:
    """Reset the configuration instance (mainly for testing)."""
    global _config_instance
    _config_instance = None