# 🚰 Synthetic Water Consumption Dataset Generator

This directory contains scripts to generate realistic synthetic water consumption data for the Abbanoa Water Management System. The generated dataset simulates daily water usage patterns for 50,000 users across multiple districts in Sardinia, Italy.

## 📁 Files Overview

- **`generate_consumption_dataset.py`** - Main generator script
- **`test_consumption_generator.py`** - Test script with smaller dataset
- **`requirements.txt`** - Python dependencies
- **`README_consumption_generator.md`** - This documentation

## 🎯 Dataset Specifications

### **Data Volume**
- **Users:** 50,000 anonymized users
- **Time Range:** August 1, 2023 to June 30, 2025 (~700+ days)
- **Total Records:** ~35 million records
- **Output Format:** CSV files split by district

### **User Types & Distribution**
- **Residential (75%):** 250 L/day base consumption
- **Commercial (20%):** 800 L/day base consumption  
- **Industrial (5%):** 5,000 L/day base consumption

### **Geographic Districts**
- **Cagliari_Centro** - Coastal, high tourism
- **Quartu_SantElena** - Coastal, moderate tourism
- **Assemini_Industrial** - Inland, industrial focus
- **Monserrato_Residential** - Inland, residential focus
- **Selargius_Distribution** - Inland, distribution hub

### **Realistic Variations**
✅ **Seasonal Trends** - Summer irrigation peaks, winter reductions  
✅ **Weather Influence** - Temperature-based consumption adjustments  
✅ **Weekly Cycles** - Weekend vs weekday patterns  
✅ **Holidays** - Italian national holidays and summer vacation periods  
✅ **Tourism Impact** - Summer peaks in coastal districts  
✅ **User Variability** - Individual consumption patterns  
✅ **System Losses** - 0.5-2% random losses (leaks, measurement errors)

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Test the Generator (Recommended)**
```bash
python test_consumption_generator.py
```
This generates a small test dataset (100 users, 31 days) to validate functionality.

### **3. Generate Full Dataset**
```bash
python generate_consumption_dataset.py
```
This generates the complete 50,000 user dataset (~35M records).

## 📊 Output Structure

### **CSV File Format**
```csv
user_id,date,user_type,district,temperature_c,is_holiday,consumption_liters
USER_000001,2023-08-01,residential,Cagliari_Centro,28.5,false,267.45
USER_000001,2023-08-02,residential,Cagliari_Centro,30.2,false,289.12
...
```

### **Column Descriptions**
- **`user_id`** - Unique user identifier (USER_XXXXXX)
- **`date`** - Date in YYYY-MM-DD format
- **`user_type`** - User category (residential/commercial/industrial)
- **`district`** - Geographic district name
- **`temperature_c`** - Daily temperature in Celsius
- **`is_holiday`** - Boolean indicating holiday/vacation periods
- **`consumption_liters`** - Daily water consumption in liters

### **Output Files**
```
consumption_data/
├── water_consumption_Cagliari_Centro.csv
├── water_consumption_Quartu_SantElena.csv  
├── water_consumption_Assemini_Industrial.csv
├── water_consumption_Monserrato_Residential.csv
├── water_consumption_Selargius_Distribution.csv
└── dataset_summary.json
```

## ⚙️ Configuration Options

### **Main Script Parameters**
```python
# In generate_consumption_dataset.py main() function
START_DATE = '2023-08-01'      # Start date
END_DATE = '2025-06-30'        # End date  
NUM_USERS = 50000              # Number of users
OUTPUT_DIR = 'consumption_data' # Output directory
BATCH_SIZE = 10000             # Users per batch (memory management)
```

### **User Type Customization**
Edit the `user_types` dictionary in `WaterConsumptionGenerator.__init__()`:
```python
'residential': {
    'probability': 0.75,        # 75% of users
    'base_consumption': 250,    # Liters per day
    'weekend_factor': 1.15,     # 15% increase on weekends
    'holiday_factor': 1.1,      # 10% increase on holidays
    'temp_sensitivity': 8.0,    # Extra liters per °C above 25°C
    'variability': 0.25         # Individual variation (25%)
}
```

### **District Characteristics**
Edit the `districts` dictionary to modify geographic properties:
```python
'Cagliari_Centro': {
    'coastal': True,            # Coastal location
    'tourism_factor': 1.4,      # 40% summer tourism boost
    'base_temp_offset': 2.0     # 2°C warmer than baseline
}
```

## 🧮 Mathematical Models

### **Temperature Simulation**
```python
# Sardinia climate model (sinusoidal + noise)
base_temp = 25 + 10 * sin(2π * (day_of_year - 80) / 365)
temperature = base_temp + district_offset + random_noise(0, 3)
```

### **Consumption Calculation**
```python
# Multi-factor consumption model
consumption = base_consumption * weekend_factor * holiday_factor 
            + temperature_effect + seasonal_irrigation 
            * tourism_effect * user_variability * loss_factor
```

### **Seasonal Irrigation (Residential)**
```python
# Summer months irrigation boost
if month in [6,7,8,9]:
    irrigation_factor = 1.2 + 0.1 * sin(2π * (month-6) / 4)
```

## 📈 Data Quality Validation

The generator includes comprehensive validation:

✅ **Range Validation** - Consumption: 10-10,000 L/day, Temperature: 5-45°C  
✅ **Record Count** - Validates total records = users × days  
✅ **Data Integrity** - Checks for missing values, negative consumption  
✅ **Distribution** - Validates user type and district distributions  
✅ **Temporal Consistency** - Ensures all dates are covered

## 🔧 Troubleshooting

### **Memory Issues**
- Reduce `BATCH_SIZE` in main script (default: 10,000)
- Reduce `NUM_USERS` for testing
- Ensure sufficient disk space (~2-5 GB for full dataset)

### **Slow Performance**
- The full dataset takes 15-30 minutes on modern hardware
- Use the test script first to validate functionality
- Monitor progress with `tqdm` progress bars

### **Missing Dependencies**
```bash
# Install missing packages
pip install pandas numpy tqdm

# Or use requirements file
pip install -r requirements.txt
```

## 📊 Expected Output Statistics

### **Full Dataset (50,000 users)**
- **Total Records:** ~35,000,000
- **File Size:** ~2-5 GB total
- **Generation Time:** 15-30 minutes
- **Memory Usage:** ~1-2 GB peak

### **Sample Statistics**
- **Avg Residential:** 280 L/day
- **Avg Commercial:** 950 L/day  
- **Avg Industrial:** 5,200 L/day
- **Summer Peak:** +20-40% (coastal districts)
- **Holiday Effect:** +10% (residential), -60% (commercial/industrial)

## 🎯 Integration with Abbanoa System

### **Database Import**
The generated CSV files can be imported into PostgreSQL:
```sql
CREATE TABLE water_consumption (
    user_id VARCHAR(20),
    date DATE,
    user_type VARCHAR(20),
    district VARCHAR(50),
    temperature_c FLOAT,
    is_holiday BOOLEAN,
    consumption_liters FLOAT
);

COPY water_consumption FROM 'water_consumption_district.csv' CSV HEADER;
```

### **API Endpoints**
The consumption data supports new API endpoints:
- `/api/v1/consumption/users/{user_id}`
- `/api/v1/consumption/districts/{district}`  
- `/api/v1/consumption/analytics/trends`
- `/api/v1/consumption/forecasting/{district}`

## 🔒 Data Privacy

✅ **Fully Synthetic** - No real user data used  
✅ **Anonymized IDs** - Generic USER_XXXXXX identifiers  
✅ **GDPR Compliant** - No personal information generated  
✅ **Reproducible** - Fixed random seed for consistent results

## 📞 Support

For issues or questions about the consumption dataset generator:
1. Check this documentation
2. Run the test script to validate setup
3. Review error logs for specific issues
4. Contact the AI Water Management System team

---

**Generated by:** AI Water Management System  
**Last Updated:** 2025-01-28  
**Version:** 1.0.0 