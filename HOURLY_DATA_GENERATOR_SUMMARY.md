# Hourly Synthetic Data Generator Setup

## Overview
Created an automated system to generate and insert synthetic sensor data every hour for all 14 nodes in the Abbanoa water infrastructure system.

## Data Frequency
- **Current database frequency**: 30 minutes (half-hourly)
- **Generator schedule**: Runs every hour
- **Data inserted per run**: 2 records per node (for :00 and :30 timestamps)

## Components Created

### 1. Main Script: `scripts/hourly_data_generator.py`
- Generates synthetic sensor data based on historical patterns
- Reads from all 14 active nodes in the database
- Creates realistic data with:
  - Temperature readings
  - Flow rate measurements
  - Pressure values
  - Total flow calculations
  - Quality scores
- Handles data continuity by checking existing records
- Prevents duplicate insertions
- Logs all operations to `/home/alessio/Customers/Abbanoa/logs/hourly_data_generator.log`

### 2. Installation Scripts

#### a) SystemD Service: `scripts/setup_hourly_service.sh`
- Creates `abbanoa-hourly-data.service` and `abbanoa-hourly-data.timer`
- Runs at :15 minutes past every hour
- Automatically restarts on failure
- Integrates with system logging

**To install:**
```bash
sudo bash /home/alessio/Customers/Abbanoa/scripts/setup_hourly_service.sh
```

**Useful SystemD commands:**
```bash
# Check status
sudo systemctl status abbanoa-hourly-data.timer
sudo systemctl status abbanoa-hourly-data.service

# View logs
sudo journalctl -u abbanoa-hourly-data.service -f

# Manual run
sudo systemctl start abbanoa-hourly-data.service

# Stop/disable
sudo systemctl stop abbanoa-hourly-data.timer
sudo systemctl disable abbanoa-hourly-data.timer
```

#### b) Cron Alternative: `scripts/setup_cron_hourly.sh`
- Simple cron job setup
- Also runs at :15 minutes past every hour
- Logs to `/home/alessio/Customers/Abbanoa/logs/hourly_cron.log`

**To install:**
```bash
bash /home/alessio/Customers/Abbanoa/scripts/setup_cron_hourly.sh
```

**Cron management:**
```bash
# View crontab
crontab -l

# Edit crontab
crontab -e

# View logs
tail -f /home/alessio/Customers/Abbanoa/logs/hourly_cron.log
```

### 3. Test Script: `scripts/test_hourly_generator.py`
- Tests the generator functionality
- Shows before/after database state
- Verifies data insertion
- Displays data distribution

**To run test:**
```bash
python3 /home/alessio/Customers/Abbanoa/scripts/test_hourly_generator.py
```

## Data Patterns
The generator uses patterns from `scripts/data_patterns.json` which contains:
- Hourly consumption patterns (24-hour cycle)
- Daily patterns (7-day week cycle)
- Monthly seasonal variations
- Base values and variations for each metric
- Node-specific multipliers based on node type

## How It Works

1. **Time Calculation**:
   - Determines which 30-minute slots need data
   - Checks current time and generates for previous unfilled slots

2. **Data Generation**:
   - Applies hourly, daily, and monthly patterns
   - Adds realistic random variations
   - Maintains continuity with previous readings
   - Respects node-type characteristics

3. **Database Operations**:
   - Checks for existing data to prevent duplicates
   - Inserts new records marked as `is_interpolated = true`
   - Handles all 14 active nodes from the database

## Node Types Handled
- **storage** (TANK01): Higher flow rates and pressure
- **distribution** (NODE01): Medium flow rates
- **monitoring** (MONITOR01, MONITOR02): Standard flow rates
- **interconnection** (INTERCON01-08): Higher flow rates
- **zone_meter** (ZONE01-02): Lower flow rates

## Schedule
The generator runs at **:15 minutes past every hour**, ensuring:
- Avoids conflicts with other hourly jobs
- Allows time for any manual data entries at the hour mark
- Provides consistent, predictable data updates

## Monitoring
- Check logs regularly for any errors
- Monitor database growth
- Verify data quality periodically
- Ensure service is running consistently

## Manual Execution
To run the generator manually:
```bash
cd /home/alessio/Customers/Abbanoa
python3 scripts/hourly_data_generator.py
```

## Future Considerations
- Adjust patterns based on real data as it becomes available
- Fine-tune node-specific behaviors
- Add seasonal adjustments
- Implement anomaly generation for testing alerts
