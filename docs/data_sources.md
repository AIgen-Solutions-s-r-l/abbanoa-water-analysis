# Data Sources Documentation

## Overview

The Abbanoa Water Infrastructure Analytics Platform ingests data from multiple sources to provide comprehensive network efficiency monitoring and analytics. This document describes all data sources, their integration methods, and the ETL pipelines that process them.

## Data Sources

### 1. Network Efficiency ETL Pipeline

The Network Efficiency ETL pipeline is the primary data collection system for real-time network monitoring.

#### Live Data Collection

**Source**: BigQuery tables and CSV files  
**Frequency**: Every 5 minutes  
**Pipeline**: `jobs/etl_collect_meter.py`  
**Target**: PostgreSQL `sensor_readings` table  

**Data Sources**:
- `sensor_readings_ml`: ML-optimized sensor data
- `v_sensor_readings_normalized`: Normalized sensor readings
- `sensor_data`: Raw sensor data from various districts
- CSV files from backup directories

**Metrics Collected**:
- Flow rate (L/s)
- Pressure (bar)
- Temperature (°C)
- Total flow volume (m³)
- Data quality scores

#### Historical Backfill

**Purpose**: Load historical data for trend analysis  
**Pipeline**: `jobs/backfill.py`  
**Capabilities**:
- 90-day automatic backfill
- Custom date range processing
- Multi-source data integration
- Parallel processing for performance

**Usage**:
```bash
# Standard 90-day backfill
python jobs/backfill.py --days=90

# Custom date range
python jobs/backfill.py --start-date=2024-01-01 --end-date=2024-03-31

# Force refresh existing data
python jobs/backfill.py --force-refresh
```

#### Schema Validation

**Purpose**: Ensure data integrity and schema compliance  
**Pipeline**: `jobs/validate_schema.py`  
**Validations**:
- Schema structure verification
- Data integrity checks
- Performance testing
- Network efficiency metrics validation
- Time series continuity analysis

**Usage**:
```bash
# Comprehensive validation
python jobs/validate_schema.py --verbose

# Automatic issue resolution
python jobs/validate_schema.py --fix-issues
```

### 2. BigQuery Data Sources

#### Primary Tables

**`sensor_readings_ml`**  
- Purpose: ML-optimized sensor data  
- Update frequency: Real-time  
- Schema: Standardized with quality scores  
- Usage: Primary source for analytics and forecasting  

**`v_sensor_readings_normalized`**  
- Purpose: Normalized view of legacy sensor data  
- Update frequency: Hourly  
- Schema: Standardized format  
- Usage: Backward compatibility  

**`sensor_data`**  
- Purpose: Raw sensor readings  
- Update frequency: Real-time  
- Schema: Variable by district  
- Usage: Data ingestion and processing  

#### District-Specific Tables

**Selargius Infrastructure**  
- Table: `selargius_infrastructure.sensor_data`  
- Nodes: 6 monitoring nodes  
- Metrics: Flow, pressure, temperature  
- Update frequency: 15-minute intervals  

**Quartucciu Infrastructure**  
- Table: `quartucciu_infrastructure.sensor_data`  
- Nodes: 4 monitoring nodes  
- Metrics: Flow, pressure, reservoir levels  
- Update frequency: 30-minute intervals  

**Teatinos Infrastructure**  
- Table: `teatinos_infrastructure.sensor_data`  
- Nodes: 3 monitoring nodes  
- Metrics: Flow, pressure, consumption  
- Update frequency: 15-minute intervals  

### 3. CSV Data Sources

#### Backup Data

**Location**: `RAWDATA/NEW_DATA/BACKUP/`  
**Format**: CSV files organized by node ID  
**Processing**: Parallel processing via `jobs/backfill.py`  
**Schema**: Standardized through column mapping  

**File Types**:
- `*_DATA_LOG.csv`: Standard sensor readings (15-second intervals)
- `*_PROCESS_DATA.csv`: Processed data with metrics
- `*_D_LOGGER_FORMAT.csv`: Diagnostic data

#### Normalized Data Files

**Files**:
- `normalized_data.csv`: Processed sensor data
- `cleaned_data.csv`: Quality-checked data
- `teatinos_hidroconta_normalized.csv`: Teatinos district data
- `normalized_quartucciu.csv`: Quartucciu district data
- `normalized_selargius.csv`: Selargius district data

### 4. Real-Time Data Processing

#### Data Flow

1. **Ingestion**: Data collected from multiple sources
2. **Normalization**: Schema standardization and quality checks
3. **Processing**: Metrics calculation and aggregation
4. **Storage**: Multi-tier storage architecture
5. **Caching**: Redis for real-time access

#### Storage Architecture

**Hot Tier (Redis)**  
- Latest readings for each node
- Response time: <100ms
- TTL: 10 minutes
- Usage: Real-time dashboard updates

**Warm Tier (PostgreSQL/TimescaleDB)**  
- Operational data (90 days)
- Response time: <500ms
- Features: Continuous aggregates, compression
- Usage: Analytics and reporting

**Cold Tier (BigQuery)**  
- Historical archive (all data)
- Response time: <5 seconds
- Usage: Long-term analysis and ML training

## ETL Scheduling

### Automated Scheduling

**Google Cloud Scheduler (cron.yaml)**:
- Network efficiency ETL: Every 5 minutes
- Data quality checks: Every 15 minutes
- Metrics calculation: Every hour
- Cache refresh: Daily

**Python ETL Scheduler**:
- Real-time sync: Every 5 minutes
- Daily sync: 2 AM UTC
- Anomaly detection: Every 15 minutes
- Cleanup: Weekly

### Manual Operations

**Data Backfill**:
```bash
# Recent data sync
python jobs/etl_collect_meter.py

# Historical backfill
python jobs/backfill.py --days=30

# Schema validation
python jobs/validate_schema.py
```

## Data Quality Assurance

### Quality Metrics

**Data Quality Score**: 0.0 to 1.0 scale  
- >0.9: High quality
- 0.5-0.9: Acceptable quality  
- <0.5: Low quality (filtered out)

**Quality Checks**:
- Value range validation
- Temporal consistency
- Missing data detection
- Outlier identification

### Monitoring

**ETL Job Tracking**:
- Job status and duration
- Records processed/failed
- Error logging and alerting
- Performance metrics

**Data Completeness**:
- Node coverage monitoring
- Time series gap detection
- Missing data alerts
- Quality score tracking

## Network Efficiency Metrics

### Calculated Metrics

**Flow Efficiency**:
- Average flow rate by time period
- Flow rate variance and trends
- Peak flow detection
- Flow rate anomalies

**Pressure Monitoring**:
- Pressure variance analysis
- Pressure drop detection
- System pressure efficiency
- Pressure anomaly alerts

**System Performance**:
- Network utilization rates
- Efficiency scores by district
- Performance trending
- Capacity utilization

### Aggregation Levels

**Real-time**: 5-minute intervals  
**Hourly**: 1-hour aggregates (materialized view)  
**Daily**: 1-day aggregates (materialized view)  
**Weekly**: 7-day rolling averages  
**Monthly**: Monthly performance summaries  

## Integration Points

### API Endpoints

**Data Access**:
- `/api/v1/network-efficiency/live`: Real-time data
- `/api/v1/network-efficiency/historical`: Historical data
- `/api/v1/network-efficiency/metrics`: Calculated metrics

**ETL Operations**:
- `/etl/collect-meter`: Trigger data collection
- `/etl/backfill`: Trigger backfill process
- `/etl/validate-schema`: Trigger validation

### Dashboard Integration

**Real-time Updates**:
- WebSocket connections for live data
- Automatic refresh every 5 minutes
- Real-time alerts and notifications

**Historical Analysis**:
- Date range selection
- Trend analysis tools
- Performance comparisons
- Export capabilities

## Troubleshooting

### Common Issues

**Data Gaps**:
- Check ETL job status
- Verify source data availability
- Run manual data collection
- Check network connectivity

**Quality Issues**:
- Run schema validation
- Check data source health
- Review quality metrics
- Investigate outliers

**Performance Issues**:
- Monitor ETL job duration
- Check database performance
- Review cache hit rates
- Optimize query performance

### Maintenance

**Regular Tasks**:
- Monthly data quality reviews
- Quarterly schema updates
- Annual performance optimization
- Continuous monitoring setup

**Emergency Procedures**:
- Data recovery from backups
- Emergency backfill procedures
- System failover protocols
- Data validation after incidents

## Future Enhancements

### Planned Features

**Enhanced Data Sources**:
- IoT sensor integration
- Mobile data collection
- Satellite data integration
- Weather data correlation

**Advanced Analytics**:
- Machine learning predictions
- Anomaly detection improvements
- Predictive maintenance
- Optimization recommendations

**Performance Improvements**:
- Streaming data processing
- Edge computing integration
- Enhanced caching strategies
- Real-time alerting systems

---

**Last Updated**: July 2025  
**Version**: 2.0.0  
**Contact**: Data Engineering Team 