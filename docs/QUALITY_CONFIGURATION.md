# Quality Metrics Configuration Guide

## Overview
This document describes the new configurable quality metrics system that replaces hardcoded values throughout the application. The system uses a centralized configuration framework with support for environment variables and YAML files.

## Configuration Structure

### Main Configuration File
- **Location**: `config/quality_thresholds.yaml`
- **Python Module**: `src.config.quality_thresholds`

### Configuration Categories

#### 1. Temperature Thresholds
```yaml
temperature:
  optimal: 15.0        # Optimal temperature (°C)
  min_normal: 10.0     # Minimum normal range
  max_normal: 20.0     # Maximum normal range
  alert_threshold: 25.0     # Alert threshold
  high_alert_threshold: 30.0 # High alert threshold
```

#### 2. Pressure Thresholds
```yaml
pressure:
  optimal: 4.0     # Optimal pressure (bar)
  minimum: 2.0     # Minimum acceptable
  critical: 1.0    # Critical low pressure
  maximum: 6.0     # Maximum safe pressure
  normal_min: 3.0  # Normal range minimum
  normal_max: 5.0  # Normal range maximum
```

#### 3. Flow Thresholds
```yaml
flow:
  minimum: 0.1        # Minimum flow (L/s)
  stagnation: 0.5     # Stagnation threshold
  normal_min: 50.0    # Normal range minimum
  normal_max: 150.0   # Normal range maximum
  normal_value: 100.0 # Expected normal value
  maximum: 10000.0    # Maximum valid flow
```

#### 4. Quality Score Thresholds
```yaml
quality_score:
  excellent: 0.9   # 90% or higher
  good: 0.7        # 70% or higher
  acceptable: 0.6  # 60% or higher
  minimum: 0.85    # Minimum required
  normal: 0.95     # Expected normal
  maximum: 1.0     # Maximum possible
```

#### 5. Quality Grades
```yaml
quality_grades:
  grade_a: 90.0  # Grade A threshold (%)
  grade_b: 80.0  # Grade B threshold (%)
  grade_c: 70.0  # Grade C threshold (%)
  grade_d: 60.0  # Grade D threshold (%)
```

#### 6. Compliance Thresholds
```yaml
compliance:
  quality_warning: 90.0      # Quality warning (%)
  quality_target: 98.0       # Quality target (%)
  temperature_warning: 95.0  # Temperature warning (%)
  temperature_target: 99.0   # Temperature target (%)
  pressure_warning: 90.0     # Pressure warning (%)
  pressure_target: 95.0      # Pressure target (%)
  contamination_warning: 5   # Contamination incidents warning
  contamination_target: 0    # Contamination incidents target
```

## Usage Examples

### Basic Usage in Python
```python
from src.config.quality_thresholds import get_quality_config

# Get configuration instance
config = get_quality_config()

# Access thresholds
optimal_temp = config.temperature.optimal
min_pressure = config.pressure.minimum
quality_warning = config.compliance.quality_warning

# Check quality grade
grade = config.quality_grades.get_grade(85.0)  # Returns QualityGrade.B
```

### Using in Service Classes
```python
from src.config.quality_thresholds import get_quality_config

class WaterQualityAnalyzer:
    def __init__(self):
        self.config = get_quality_config()
    
    def check_temperature(self, temp: float) -> str:
        if temp > self.config.temperature.high_alert_threshold:
            return "HIGH_ALERT"
        elif temp > self.config.temperature.alert_threshold:
            return "ALERT"
        elif self.config.temperature.min_normal <= temp <= self.config.temperature.max_normal:
            return "NORMAL"
        else:
            return "WARNING"
```

## Environment Variable Override

Override configuration values using environment variables with the prefix `QUALITY_THRESHOLDS_`:

```bash
# Override temperature optimal value
export QUALITY_THRESHOLDS_TEMPERATURE__OPTIMAL=16.0

# Override pressure minimum
export QUALITY_THRESHOLDS_PRESSURE__MINIMUM=2.5

# Override compliance targets
export QUALITY_THRESHOLDS_COMPLIANCE__QUALITY_TARGET=99.0
export QUALITY_THRESHOLDS_COMPLIANCE__CONTAMINATION_TARGET=0
```

## Loading Custom Configuration

### From YAML File
```python
from src.config.quality_thresholds import QualityThresholdsConfig

# Load from custom YAML file
config = QualityThresholdsConfig.from_yaml('path/to/custom_config.yaml')
```

### From Dictionary
```python
config = QualityThresholdsConfig(
    temperature=TemperatureThresholds(optimal=16.0),
    pressure=PressureThresholds(minimum=2.5)
)
```

## Files Updated

The following files have been refactored to use the configuration system:

1. **src/api/services/water_quality_service.py**
   - Temperature compliance checks
   - Pressure thresholds for alerts
   - Flow rate monitoring
   - Quality score calculations
   - Contamination risk assessment

2. **src/api/services/kpis/quality_service.py**
   - KPI alert thresholds
   - Compliance targets
   - Goal generation

3. **src/application/anomaly_detector.py**
   - Anomaly detection thresholds
   - Normal operating ranges

## Migration Guide

### Before (Hardcoded)
```python
# Old approach - hardcoded values
if temperature > 25.0:
    alert("Temperature too high")

if quality_score < 0.6:
    alert("Quality below acceptable")
```

### After (Configurable)
```python
# New approach - configurable
config = get_quality_config()

if temperature > config.temperature.alert_threshold:
    alert("Temperature too high")

if quality_score < config.quality_score.acceptable:
    alert("Quality below acceptable")
```

## Benefits

1. **Centralized Management**: All quality thresholds in one place
2. **Environment-Specific**: Different thresholds for dev/staging/production
3. **No Code Changes**: Adjust thresholds without modifying code
4. **Type Safety**: Pydantic validation ensures correct types
5. **Documentation**: Self-documenting configuration structure
6. **Testing**: Easy to test with different threshold values

## Testing Configuration

```python
# Unit test example
from src.config.quality_thresholds import QualityThresholdsConfig, reset_config
import unittest

class TestWithCustomConfig(unittest.TestCase):
    def setUp(self):
        # Reset to ensure clean state
        reset_config()
        
        # Set custom configuration for testing
        self.config = QualityThresholdsConfig(
            temperature=TemperatureThresholds(optimal=20.0),
            pressure=PressureThresholds(minimum=3.0)
        )
    
    def test_alert_generation(self):
        # Test with custom thresholds
        ...
```

## Monitoring and Validation

The configuration system includes built-in validation:
- Range checks (e.g., percentages 0-100)
- Logical constraints (e.g., min < optimal < max)
- Type validation (floats, integers, etc.)

## Future Enhancements

Potential improvements for the configuration system:
1. Dynamic reload without restart
2. Database-backed configuration
3. A/B testing different thresholds
4. Machine learning-based threshold optimization
5. Historical threshold tracking and auditing