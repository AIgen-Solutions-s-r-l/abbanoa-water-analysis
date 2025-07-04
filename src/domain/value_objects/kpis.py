"""Value objects for Key Performance Indicators (KPIs) in the water network system."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Union
from uuid import UUID


class KPIType(Enum):
    """Enumeration of supported KPI types."""
    FLOW_RATE = "flow_rate"
    RESERVOIR_LEVEL = "reservoir_level"
    PRESSURE = "pressure"
    NETWORK_EFFICIENCY = "network_efficiency"
    DEMAND_SATISFACTION = "demand_satisfaction"
    SYSTEM_AVAILABILITY = "system_availability"


class AlertLevel(Enum):
    """Alert severity levels for KPI threshold breaches."""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MeasurementUnit(Enum):
    """Standard measurement units for KPIs."""
    LITERS_PER_SECOND = "L/s"
    METERS = "m"
    BAR = "bar"
    PERCENTAGE = "%"
    CUBIC_METERS = "m3"


@dataclass(frozen=True)
class KPIThresholds:
    """Defines threshold values for KPI monitoring and alerting."""
    
    normal_min: float
    normal_max: float
    warning_min: Optional[float] = None
    warning_max: Optional[float] = None
    critical_min: Optional[float] = None
    critical_max: Optional[float] = None
    emergency_min: Optional[float] = None
    emergency_max: Optional[float] = None
    
    def get_alert_level(self, value: float) -> AlertLevel:
        """Determine alert level based on KPI value and thresholds."""
        if self.emergency_min is not None and value <= self.emergency_min:
            return AlertLevel.EMERGENCY
        if self.emergency_max is not None and value >= self.emergency_max:
            return AlertLevel.EMERGENCY
        if self.critical_min is not None and value <= self.critical_min:
            return AlertLevel.CRITICAL
        if self.critical_max is not None and value >= self.critical_max:
            return AlertLevel.CRITICAL
        if self.warning_min is not None and value <= self.warning_min:
            return AlertLevel.WARNING
        if self.warning_max is not None and value >= self.warning_max:
            return AlertLevel.WARNING
        if self.normal_min <= value <= self.normal_max:
            return AlertLevel.NORMAL
        return AlertLevel.WARNING


@dataclass(frozen=True)
class KPISpecification:
    """Complete specification for a KPI including metadata and thresholds."""
    
    kpi_type: KPIType
    name: str
    description: str
    unit: MeasurementUnit
    update_frequency_minutes: int
    accuracy_target: float  # As percentage (e.g., 0.05 for ±5%)
    thresholds: KPIThresholds
    calculation_method: str
    measurement_points: list[str] = field(default_factory=list)
    data_retention_days: int = 365
    
    def validate_value(self, value: float) -> bool:
        """Validate if a KPI value is within acceptable bounds."""
        # Basic validation - can be extended with more sophisticated rules
        return isinstance(value, (int, float)) and not (value < 0 and self.kpi_type != KPIType.NETWORK_EFFICIENCY)


@dataclass
class KPIValue:
    """Represents a measured or calculated KPI value at a specific point in time."""
    
    specification: KPISpecification
    value: float
    timestamp: datetime
    location_id: str
    measurement_id: UUID
    quality_score: float = 1.0  # 0.0 to 1.0, where 1.0 is perfect quality
    is_predicted: bool = False
    prediction_confidence: Optional[float] = None
    metadata: Dict[str, Union[str, float, int]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the KPI value after initialization."""
        if not self.specification.validate_value(self.value):
            raise ValueError(f"Invalid KPI value: {self.value} for {self.specification.kpi_type}")
        
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError(f"Quality score must be between 0.0 and 1.0, got {self.quality_score}")
        
        if self.is_predicted and self.prediction_confidence is None:
            raise ValueError("Prediction confidence must be provided for predicted values")
    
    @property
    def alert_level(self) -> AlertLevel:
        """Get the alert level for this KPI value."""
        return self.specification.thresholds.get_alert_level(self.value)
    
    @property
    def is_within_normal_range(self) -> bool:
        """Check if the value is within normal operating range."""
        return self.alert_level == AlertLevel.NORMAL
    
    @property
    def requires_attention(self) -> bool:
        """Check if the value requires operational attention."""
        return self.alert_level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]


# Pre-defined KPI specifications for the Abbanoa water network

FLOW_RATE_SPEC = KPISpecification(
    kpi_type=KPIType.FLOW_RATE,
    name="Water Flow Rate",
    description="Water flow rate through network segments",
    unit=MeasurementUnit.LITERS_PER_SECOND,
    update_frequency_minutes=15,
    accuracy_target=0.05,
    thresholds=KPIThresholds(
        normal_min=50.0,
        normal_max=8000.0,
        warning_min=25.0,
        warning_max=8500.0,
        critical_min=10.0,
        critical_max=9000.0,
        emergency_min=5.0,
        emergency_max=9500.0
    ),
    calculation_method="Time-averaged measurements over measurement interval",
    measurement_points=[
        "Main distribution nodes", 
        "District entry points", 
        "Critical junctions"
    ],
    data_retention_days=365
)

RESERVOIR_LEVEL_SPEC = KPISpecification(
    kpi_type=KPIType.RESERVOIR_LEVEL,
    name="Reservoir Water Level",
    description="Water level in storage reservoirs and tanks",
    unit=MeasurementUnit.METERS,
    update_frequency_minutes=5,
    accuracy_target=0.02,
    thresholds=KPIThresholds(
        normal_min=2.0,  # 40% of 5m capacity
        normal_max=4.25, # 85% of 5m capacity
        warning_min=1.5,  # 30% of capacity
        warning_max=4.5,  # 90% of capacity
        critical_min=1.0,  # 20% of capacity
        critical_max=4.75, # 95% of capacity
        emergency_min=0.5,  # 10% of capacity
        emergency_max=5.0   # 100% of capacity
    ),
    calculation_method="Direct sensor readings with temperature compensation",
    measurement_points=[
        "District reservoirs",
        "Main storage facilities", 
        "Emergency reserves"
    ],
    data_retention_days=1095  # 3 years
)

PRESSURE_SPEC = KPISpecification(
    kpi_type=KPIType.PRESSURE,
    name="Network Pressure",
    description="Water pressure at critical monitoring points",
    unit=MeasurementUnit.BAR,
    update_frequency_minutes=10,
    accuracy_target=0.02,
    thresholds=KPIThresholds(
        normal_min=2.5,
        normal_max=7.0,
        warning_min=2.0,
        warning_max=8.0,
        critical_min=1.5,
        critical_max=9.0,
        emergency_min=1.0,
        emergency_max=10.0
    ),
    calculation_method="Direct pressure sensor readings with temperature compensation",
    measurement_points=[
        "Customer connection points",
        "Network nodes",
        "Elevation change points"
    ],
    data_retention_days=365
)

NETWORK_EFFICIENCY_SPEC = KPISpecification(
    kpi_type=KPIType.NETWORK_EFFICIENCY,
    name="Network Efficiency",
    description="Overall network efficiency (Output/Input ratio)",
    unit=MeasurementUnit.PERCENTAGE,
    update_frequency_minutes=60,
    accuracy_target=0.01,
    thresholds=KPIThresholds(
        normal_min=85.0,
        normal_max=100.0,
        warning_min=80.0,
        warning_max=100.0,
        critical_min=75.0,
        critical_max=100.0,
        emergency_min=70.0,
        emergency_max=100.0
    ),
    calculation_method="(Total Output / Total Input) × 100",
    measurement_points=["Network-wide calculation"],
    data_retention_days=1095
)

# KPI Registry - Central registry of all available KPI specifications
KPI_REGISTRY: Dict[KPIType, KPISpecification] = {
    KPIType.FLOW_RATE: FLOW_RATE_SPEC,
    KPIType.RESERVOIR_LEVEL: RESERVOIR_LEVEL_SPEC,
    KPIType.PRESSURE: PRESSURE_SPEC,
    KPIType.NETWORK_EFFICIENCY: NETWORK_EFFICIENCY_SPEC,
}


def get_kpi_specification(kpi_type: KPIType) -> KPISpecification:
    """Retrieve KPI specification by type."""
    if kpi_type not in KPI_REGISTRY:
        raise ValueError(f"Unknown KPI type: {kpi_type}")
    return KPI_REGISTRY[kpi_type]


def create_kpi_value(
    kpi_type: KPIType,
    value: float,
    timestamp: datetime,
    location_id: str,
    measurement_id: UUID,
    **kwargs
) -> KPIValue:
    """Factory function to create KPI values with proper specification."""
    spec = get_kpi_specification(kpi_type)
    return KPIValue(
        specification=spec,
        value=value,
        timestamp=timestamp,
        location_id=location_id,
        measurement_id=measurement_id,
        **kwargs
    )