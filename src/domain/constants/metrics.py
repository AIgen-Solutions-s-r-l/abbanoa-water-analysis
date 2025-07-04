"""Constants and configuration for metrics and measurements in the water network system."""

from typing import Dict, List, Final

# Measurement intervals in minutes
MEASUREMENT_INTERVALS: Final[Dict[str, int]] = {
    "FLOW_RATE": 15,           # Every 15 minutes
    "RESERVOIR_LEVEL": 5,      # Every 5 minutes
    "PRESSURE": 10,            # Every 10 minutes
    "NETWORK_EFFICIENCY": 60,  # Every hour
    "DEMAND_SATISFACTION": 1440,  # Daily
    "SYSTEM_AVAILABILITY": 1,  # Every minute
}

# Data quality thresholds
DATA_QUALITY: Final[Dict[str, float]] = {
    "MINIMUM_COMPLETENESS": 0.95,      # 95% minimum data availability
    "MAX_INTERPOLATION_GAP_MIN": 30,   # Maximum 30 minutes for interpolation
    "OUTLIER_DETECTION_SIGMA": 3.0,    # 3-sigma rule for outlier detection
    "SENSOR_ACCURACY_TOLERANCE": 0.05,  # 5% tolerance for sensor drift
    "CALIBRATION_DRIFT_THRESHOLD": 0.02, # 2% drift triggers recalibration
}

# System performance requirements
PERFORMANCE_TARGETS: Final[Dict[str, float]] = {
    "SYSTEM_AVAILABILITY": 0.99,       # 99% uptime requirement
    "RESPONSE_TIME_SECONDS": 2.0,      # Maximum 2 seconds for queries
    "PREDICTION_ACCURACY_FLOW": 0.95,  # 95% accuracy for flow predictions
    "PREDICTION_ACCURACY_PRESSURE": 0.98,  # 98% accuracy for pressure
    "PREDICTION_ACCURACY_LEVEL": 0.99, # 99% accuracy for reservoir levels
    "ALERT_RESPONSE_TIME_MINUTES": 2.0, # Maximum 2 minutes for alert processing
}

# Alert escalation timeouts (in minutes)
ALERT_ESCALATION: Final[Dict[str, int]] = {
    "LEVEL_1_TIMEOUT": 15,    # 15 minutes to level 1 escalation
    "LEVEL_2_TIMEOUT": 30,    # 30 minutes to level 2 escalation  
    "LEVEL_3_TIMEOUT": 60,    # 60 minutes to level 3 escalation
    "CRITICAL_IMMEDIATE": 0,  # Immediate escalation for critical alerts
    "EMERGENCY_IMMEDIATE": 0, # Immediate escalation for emergency alerts
}

# Business KPI targets
BUSINESS_TARGETS: Final[Dict[str, float]] = {
    "OPERATIONAL_EFFICIENCY_IMPROVEMENT": 0.15,  # 15% improvement target
    "MAINTENANCE_REDUCTION": 0.10,               # 10% reduction in maintenance
    "ISSUE_DETECTION_IMPROVEMENT": 0.50,         # 50% improvement in detection
    "STAFF_PRODUCTIVITY_IMPROVEMENT": 0.20,      # 20% productivity improvement
    "WATER_LOSS_REDUCTION": 0.05,               # 5% reduction in water loss
    "ENERGY_EFFICIENCY_IMPROVEMENT": 0.08,       # 8% energy efficiency gain
    "CUSTOMER_SATISFACTION_TARGET": 0.80,        # 80% satisfaction target
}

# Data retention policies (in days)
DATA_RETENTION: Final[Dict[str, int]] = {
    "RAW_DATA": 365,          # 1 year for raw measurements
    "HOURLY_AGGREGATES": 1095, # 3 years for hourly data
    "DAILY_AGGREGATES": 3650,  # 10 years for daily summaries
    "MONTHLY_AGGREGATES": 7300, # 20 years for monthly data
    "ALERT_HISTORY": 2555,     # 7 years for alert records
    "AUDIT_LOGS": 2555,        # 7 years for audit trails
}

# Network topology constants
NETWORK_TOPOLOGY: Final[Dict[str, List[str]]] = {
    "MEASUREMENT_POINT_TYPES": [
        "main_distribution_node",
        "district_entry_point", 
        "critical_junction",
        "customer_connection",
        "elevation_change_point",
        "reservoir_outlet",
        "pump_station",
        "valve_station"
    ],
    
    "INFRASTRUCTURE_MATERIALS": [
        "ductile_iron",
        "PVC",
        "steel", 
        "HDPE",
        "concrete",
        "cast_iron"
    ],
    
    "FACILITY_TYPES": [
        "elevated_tank",
        "ground_reservoir",
        "underground_reservoir",
        "pump_station",
        "treatment_plant",
        "distribution_center"
    ]
}

# Validation ranges for different KPI types
VALIDATION_RANGES: Final[Dict[str, Dict[str, float]]] = {
    "FLOW_RATE": {
        "MIN": 0.0,
        "MAX": 10000.0,  # L/s
        "TYPICAL_MIN": 10.0,
        "TYPICAL_MAX": 5000.0
    },
    
    "RESERVOIR_LEVEL": {
        "MIN": 0.0,
        "MAX": 50.0,     # meters
        "TYPICAL_MIN": 1.0,
        "TYPICAL_MAX": 20.0
    },
    
    "PRESSURE": {
        "MIN": 0.0,
        "MAX": 10.0,     # bar
        "TYPICAL_MIN": 1.5,
        "TYPICAL_MAX": 8.0
    },
    
    "NETWORK_EFFICIENCY": {
        "MIN": 0.0,
        "MAX": 100.0,    # percentage
        "TYPICAL_MIN": 70.0,
        "TYPICAL_MAX": 95.0
    }
}

# Seasonal adjustment factors
SEASONAL_FACTORS: Final[Dict[str, Dict[str, float]]] = {
    "MONTHLY_DEMAND_FACTORS": {
        "JANUARY": 0.85,
        "FEBRUARY": 0.88,
        "MARCH": 0.95,
        "APRIL": 1.02,
        "MAY": 1.08,
        "JUNE": 1.15,
        "JULY": 1.25,
        "AUGUST": 1.22,
        "SEPTEMBER": 1.10,
        "OCTOBER": 1.00,
        "NOVEMBER": 0.92,
        "DECEMBER": 0.88
    },
    
    "DAILY_DEMAND_FACTORS": {
        "MONDAY": 1.02,
        "TUESDAY": 1.05,
        "WEDNESDAY": 1.08,
        "THURSDAY": 1.10,
        "FRIDAY": 1.12,
        "SATURDAY": 0.95,
        "SUNDAY": 0.88
    },
    
    "HOURLY_DEMAND_FACTORS": {
        "00": 0.45, "01": 0.40, "02": 0.38, "03": 0.35,
        "04": 0.33, "05": 0.40, "06": 0.65, "07": 0.90,
        "08": 1.20, "09": 1.35, "10": 1.25, "11": 1.15,
        "12": 1.10, "13": 1.05, "14": 1.08, "15": 1.12,
        "16": 1.18, "17": 1.25, "18": 1.35, "19": 1.40,
        "20": 1.25, "21": 1.10, "22": 0.85, "23": 0.65
    }
}

# Model performance benchmarks
MODEL_BENCHMARKS: Final[Dict[str, Dict[str, float]]] = {
    "FLOW_RATE_PREDICTION": {
        "R_SQUARED_MIN": 0.85,        # Minimum R² for model acceptance
        "MAPE_MAX": 10.0,             # Maximum Mean Absolute Percentage Error
        "RMSE_THRESHOLD": 50.0,       # Root Mean Square Error threshold (L/s)
        "BIAS_MAX": 5.0,              # Maximum bias percentage
    },
    
    "PRESSURE_PREDICTION": {
        "R_SQUARED_MIN": 0.90,
        "MAPE_MAX": 5.0,
        "RMSE_THRESHOLD": 0.2,        # bar
        "BIAS_MAX": 2.0,
    },
    
    "RESERVOIR_LEVEL_PREDICTION": {
        "R_SQUARED_MIN": 0.95,
        "MAPE_MAX": 3.0,
        "RMSE_THRESHOLD": 0.1,        # meters
        "BIAS_MAX": 1.0,
    }
}

# Communication and notification settings
NOTIFICATION_SETTINGS: Final[Dict[str, Dict[str, any]]] = {
    "EMAIL": {
        "MAX_FREQUENCY_MINUTES": 30,   # Minimum 30 minutes between emails
        "BATCH_SIZE": 10,              # Maximum alerts per email
        "PRIORITY_IMMEDIATE": ["EMERGENCY", "CRITICAL"],
        "PRIORITY_BATCH": ["WARNING"],
    },
    
    "SMS": {
        "MAX_FREQUENCY_MINUTES": 60,   # Minimum 60 minutes between SMS
        "CHARACTER_LIMIT": 160,
        "PRIORITY_ONLY": ["EMERGENCY", "CRITICAL"],
    },
    
    "DASHBOARD": {
        "REFRESH_INTERVAL_SECONDS": 30,
        "MAX_ALERTS_DISPLAY": 50,
        "AUTO_ACKNOWLEDGE_MINUTES": 1440,  # 24 hours
    }
}

# Integration endpoints and timeouts
INTEGRATION_SETTINGS: Final[Dict[str, Dict[str, any]]] = {
    "BIGQUERY": {
        "CONNECTION_TIMEOUT_SECONDS": 30,
        "QUERY_TIMEOUT_SECONDS": 300,
        "BATCH_SIZE": 1000,
        "RETRY_ATTEMPTS": 3,
        "RETRY_DELAY_SECONDS": 5,
    },
    
    "SCADA": {
        "CONNECTION_TIMEOUT_SECONDS": 10,
        "READ_TIMEOUT_SECONDS": 30,
        "HEARTBEAT_INTERVAL_SECONDS": 60,
        "MAX_RECONNECT_ATTEMPTS": 5,
    },
    
    "API": {
        "RATE_LIMIT_PER_MINUTE": 1000,
        "MAX_CONCURRENT_CONNECTIONS": 100,
        "REQUEST_TIMEOUT_SECONDS": 30,
        "KEEPALIVE_TIMEOUT_SECONDS": 75,
    }
}