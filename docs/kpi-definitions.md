# KPI Definitions and Specifications
## Abbanoa Water Network Optimization

**Document Version:** 1.0  
**Date:** 2025-07-04  
**Status:** APPROVED  

### Overview

This document provides detailed definitions, measurement specifications, and calculation methodologies for all Key Performance Indicators (KPIs) in the Abbanoa water network optimization project.

## Core KPIs

### 1. Flow Rate

**Definition**: Water flow rate through network segments  
**Unit**: Liters per second (L/s)  
**Business Importance**: Critical for demand management and network capacity planning  

#### Measurement Specifications
- **Measurement Points**:
  - Main distribution nodes (12 locations)
  - District entry points (8 locations)
  - Critical junctions (15 locations)
- **Calculation Method**: Time-averaged measurements over measurement interval
- **Update Frequency**: Every 15 minutes
- **Data Source**: Ultrasonic flow meters, electromagnetic flow sensors

#### Validation and Thresholds
- **Valid Range**: 0 - 10,000 L/s
- **Normal Operating Range**: 50 - 8,000 L/s
- **Critical Thresholds**:
  - Low Flow Alert: <10% of normal capacity
  - High Flow Alert: >90% of maximum capacity
  - Emergency Threshold: >95% of maximum capacity

#### Quality Metrics
- **Accuracy Requirement**: ±5% of true value
- **Data Completeness**: >95% valid readings per day
- **Calibration Frequency**: Monthly verification required

### 2. Reservoir Level

**Definition**: Water level in storage reservoirs and tanks  
**Unit**: Meters (m)  
**Business Importance**: Essential for supply security and emergency preparedness  

#### Measurement Specifications
- **Measurement Points**:
  - All district reservoirs (6 locations)
  - Main storage facilities (3 locations)
  - Emergency reserves (2 locations)
- **Calculation Method**: Direct sensor readings with temperature compensation
- **Update Frequency**: Every 5 minutes
- **Data Source**: Ultrasonic level sensors, pressure transducers

#### Validation and Thresholds
- **Valid Range**: 0 - 50 meters
- **Critical Thresholds**:
  - Emergency Low: 20% of capacity
  - Low Warning: 30% of capacity
  - Optimal Range: 40% - 85% of capacity
  - High Warning: 90% of capacity
  - Emergency High: 95% of capacity

#### Quality Metrics
- **Accuracy Requirement**: ±2% of full scale
- **Data Completeness**: >98% valid readings per day
- **Calibration Frequency**: Quarterly verification required

### 3. Pressure

**Definition**: Water pressure at critical monitoring points throughout the network  
**Unit**: Bar (bar)  
**Business Importance**: Critical for service quality and network integrity  

#### Measurement Specifications
- **Measurement Points**:
  - Customer connection points (25 locations)
  - Network nodes (18 locations)
  - Elevation change points (12 locations)
- **Calculation Method**: Direct pressure sensor readings with temperature compensation
- **Update Frequency**: Every 10 minutes
- **Data Source**: Piezoresistive pressure sensors

#### Validation and Thresholds
- **Valid Range**: 0 - 10 bar
- **Service Standards**:
  - Minimum Service Pressure: 2.0 bar
  - Optimal Service Pressure: 4.5 bar
  - Maximum Service Pressure: 8.0 bar
- **Critical Thresholds**:
  - Low Pressure Alert: <2.5 bar
  - High Pressure Alert: >7.0 bar
  - Emergency Pressure: <1.5 bar or >9.0 bar

#### Quality Metrics
- **Accuracy Requirement**: ±2% of true value
- **Data Completeness**: >96% valid readings per day
- **Calibration Frequency**: Bi-monthly verification required

## Derived KPIs

### Network Efficiency
- **Calculation**: (Total Output / Total Input) × 100
- **Unit**: Percentage (%)
- **Update Frequency**: Hourly calculation
- **Target Range**: >85% efficiency

### Demand Satisfaction Rate
- **Calculation**: (Actual Supply / Requested Demand) × 100
- **Unit**: Percentage (%)
- **Update Frequency**: Daily calculation
- **Target Range**: >98% satisfaction

### System Availability
- **Calculation**: (Operational Time / Total Time) × 100
- **Unit**: Percentage (%)
- **Update Frequency**: Continuous monitoring
- **Target Range**: >99% availability

## Data Quality Requirements

### Completeness
- **Minimum Data Availability**: 95% for all KPIs
- **Missing Data Handling**: Linear interpolation for gaps <30 minutes
- **Extended Outages**: Flag as data quality issue, exclude from calculations

### Accuracy
- **Sensor Calibration**: Regular calibration per manufacturer specifications
- **Cross-validation**: Multiple sensor redundancy where critical
- **Outlier Detection**: Automated statistical anomaly detection

### Timeliness
- **Real-time Updates**: Within specified measurement intervals
- **Maximum Delay**: 5 minutes for critical measurements
- **Data Lag Monitoring**: Automated alerts for delayed data streams

## Calculation Methodologies

### Time Aggregation
- **Raw Data**: Stored at measurement frequency
- **Hourly Aggregates**: Mean, min, max, standard deviation
- **Daily Aggregates**: Mean, min, max, total volume (where applicable)
- **Weekly/Monthly**: Trend analysis and pattern recognition

### Statistical Processing
- **Smoothing**: 5-point moving average for trend analysis
- **Seasonal Adjustment**: Weekly and daily pattern normalization
- **Anomaly Detection**: 3-sigma rule with seasonal baseline

## Implementation Notes

### Data Storage
- **Time Series Database**: Optimized for high-frequency measurements
- **Retention Policy**: 
  - Raw data: 1 year
  - Hourly aggregates: 3 years
  - Daily aggregates: 10 years

### API Specifications
- **Real-time Access**: WebSocket connections for live data
- **Historical Queries**: REST API with time range parameters
- **Batch Export**: CSV/JSON formats for analysis tools

### Monitoring and Alerting
- **Threshold Monitoring**: Automated evaluation against defined thresholds
- **Alert Delivery**: Email, SMS, dashboard notifications
- **Escalation Rules**: Automatic escalation for critical thresholds

---

**Document Control:**
- **Next Review Date**: 2025-10-04
- **Review Frequency**: Quarterly
- **Change Approval**: Product Owner + Technical Lead