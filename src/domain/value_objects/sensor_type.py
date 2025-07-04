from enum import Enum


class SensorType(Enum):
    """Enumeration of sensor types in the water infrastructure."""
    
    FLOW_METER = "flow_meter"
    PRESSURE_SENSOR = "pressure_sensor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    VOLUME_METER = "volume_meter"
    MULTI_PARAMETER = "multi_parameter"
    
    @classmethod
    def from_string(cls, value: str) -> "SensorType":
        """Create SensorType from string value."""
        value = value.lower().strip()
        
        mapping = {
            "flow": cls.FLOW_METER,
            "flow_meter": cls.FLOW_METER,
            "pressure": cls.PRESSURE_SENSOR,
            "pressure_sensor": cls.PRESSURE_SENSOR,
            "temperature": cls.TEMPERATURE_SENSOR,
            "temp": cls.TEMPERATURE_SENSOR,
            "volume": cls.VOLUME_METER,
            "volume_meter": cls.VOLUME_METER,
            "multi": cls.MULTI_PARAMETER,
            "multi_parameter": cls.MULTI_PARAMETER,
        }
        
        sensor_type = mapping.get(value)
        if not sensor_type:
            raise ValueError(f"Unknown sensor type: {value}")
        
        return sensor_type