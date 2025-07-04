# 📊 **Looker Studio Dashboard Setup Guide**

## 🚀 **Step-by-Step Setup (30 minutes)**

### **Step 1: Access Looker Studio**
1. Go to [`datastudio.google.com`](https://datastudio.google.com)
2. Sign in with your Google account (same one used for GCP)
3. Click "**Create**" → "**Report**"

### **Step 2: Connect to BigQuery**
1. Click "**Add Data**"
2. Select "**BigQuery**"
3. **Authorize** Looker Studio to access BigQuery
4. Navigate to: `abbanoa-464816` → `water_infrastructure` → `sensor_data`
5. Click "**Add**"

### **Step 3: Create Data Sources with Custom Queries**

Instead of using the raw table, we'll create custom data sources with pre-aggregated data for better performance.

#### **🔥 Data Source 1: Real-Time Metrics**
1. Click "**Resource**" → "**Manage added data sources**"
2. Click "**Add a data source**" → "**BigQuery**"
3. Select "**Custom Query**"
4. **Project**: `abbanoa-464816`
5. **Query Name**: `Real_Time_Metrics`
6. **Custom Query**:

```sql
WITH latest_data AS (
  SELECT 
    data,
    ora,
    selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as sant_anna_flow,
    selargius_nodo_via_seneca_portata_w_istantanea_diretta as seneca_flow,
    selargius_serbatoio_selargius_portata_uscita as tank_output,
    quartucciu_serbatoio_cuccuru_linu_portata_selargius as external_supply,
    selargius_nodo_via_sant_anna_temperatura_interna as sant_anna_temp,
    selargius_nodo_via_seneca_temperatura_interna as seneca_temp,
    DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as datetime_combined,
    _ingestion_timestamp,
    ROW_NUMBER() OVER (ORDER BY _ingestion_timestamp DESC) as row_num
  FROM `abbanoa-464816.water_infrastructure.sensor_data`
  WHERE data IS NOT NULL AND ora IS NOT NULL
)
SELECT 
  datetime_combined,
  data as date_string,
  ora as time_string,
  sant_anna_flow,
  seneca_flow,
  tank_output,
  external_supply,
  sant_anna_temp,
  seneca_temp,
  CASE 
    WHEN sant_anna_flow > 120 THEN 'HIGH'
    WHEN sant_anna_flow < 30 THEN 'LOW' 
    ELSE 'NORMAL'
  END as flow_status,
  COALESCE(sant_anna_flow, 0) + COALESCE(seneca_flow, 0) + COALESCE(external_supply, 0) as total_input,
  COALESCE(sant_anna_flow, 0) + COALESCE(seneca_flow, 0) + COALESCE(external_supply, 0) - COALESCE(tank_output, 0) as apparent_loss
FROM latest_data
ORDER BY datetime_combined DESC
```

#### **🔥 Data Source 2: Hourly Patterns**
1. Create another custom query data source
2. **Query Name**: `Hourly_Patterns`
3. **Custom Query**:

```sql
SELECT 
  EXTRACT(HOUR FROM PARSE_TIME('%H:%M:%S', ora)) as hour_of_day,
  EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data)) as day_of_week,
  CASE EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data))
    WHEN 1 THEN 'Sunday'
    WHEN 2 THEN 'Monday'
    WHEN 3 THEN 'Tuesday'
    WHEN 4 THEN 'Wednesday'
    WHEN 5 THEN 'Thursday'
    WHEN 6 THEN 'Friday'
    WHEN 7 THEN 'Saturday'
  END as day_name,
  AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as avg_flow_rate,
  STDDEV(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as stddev_flow_rate,
  MIN(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as min_flow_rate,
  MAX(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as max_flow_rate,
  COUNT(*) as measurements,
  AVG(selargius_serbatoio_selargius_portata_uscita) as avg_tank_output
FROM `abbanoa-464816.water_infrastructure.sensor_data`
WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
  AND ora IS NOT NULL 
  AND data IS NOT NULL
GROUP BY hour_of_day, day_of_week, day_name
ORDER BY day_of_week, hour_of_day
```

#### **🔥 Data Source 3: Daily Aggregates**
1. Create third custom query data source
2. **Query Name**: `Daily_Aggregates`
3. **Custom Query**:

```sql
SELECT 
  PARSE_DATE('%d/%m/%Y', data) as date_parsed,
  data as date_string,
  COUNT(*) as total_measurements,
  AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as avg_sant_anna_flow,
  MAX(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as max_sant_anna_flow,
  MIN(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as min_sant_anna_flow,
  AVG(selargius_serbatoio_selargius_portata_uscita) as avg_tank_output,
  AVG(quartucciu_serbatoio_cuccuru_linu_portata_selargius) as avg_external_supply,
  AVG(selargius_nodo_via_sant_anna_temperatura_interna) as avg_temperature,
  SUM(selargius_nodo_via_sant_anna_portata_w_totale_diretta) as total_volume_m3,
  AVG(COALESCE(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta, 0) + 
      COALESCE(selargius_nodo_via_seneca_portata_w_istantanea_diretta, 0) + 
      COALESCE(quartucciu_serbatoio_cuccuru_linu_portata_selargius, 0) - 
      COALESCE(selargius_serbatoio_selargius_portata_uscita, 0)) as avg_apparent_loss
FROM `abbanoa-464816.water_infrastructure.sensor_data`
WHERE data IS NOT NULL
GROUP BY data, date_parsed
ORDER BY date_parsed DESC
```

---

## 📊 **Dashboard Layout Design**

### **Page 1: Real-Time Operations Dashboard**

#### **🔥 Top Row: KPI Scorecards**
1. **Add Chart** → **Scorecard**
2. **Data Source**: `Real_Time_Metrics`
3. Create 4 scorecards:

**Scorecard 1: Current Flow Rate**
- **Metric**: `sant_anna_flow`
- **Title**: "Current Flow Rate (L/S)"
- **Style**: Large number, blue background

**Scorecard 2: Tank Output**
- **Metric**: `tank_output`
- **Title**: "Tank Output (L/S)"
- **Style**: Large number, green background

**Scorecard 3: Temperature**
- **Metric**: `sant_anna_temp`
- **Title**: "Temperature (°C)"
- **Style**: Large number, orange background

**Scorecard 4: System Status**
- **Metric**: `flow_status`
- **Title**: "System Status"
- **Style**: Text, conditional formatting (GREEN for NORMAL, RED for HIGH/LOW)

#### **📈 Middle Row: Time Series Charts**

**Chart 1: Flow Rate Trend (24 hours)**
1. **Add Chart** → **Time Series Chart**
2. **Data Source**: `Real_Time_Metrics`
3. **Date Range Dimension**: `datetime_combined`
4. **Metrics**: 
   - `sant_anna_flow` (Blue line)
   - `tank_output` (Green line)
   - `external_supply` (Orange line)
5. **Title**: "Water Flow Rates - Last 24 Hours"
6. **Date Range**: Last 24 hours

**Chart 2: Network Balance**
1. **Add Chart** → **Combo Chart**
2. **Data Source**: `Real_Time_Metrics`
3. **Date Range Dimension**: `datetime_combined`
4. **Left Y-Axis Metrics**: `total_input`, `tank_output`
5. **Right Y-Axis Metrics**: `apparent_loss`
6. **Title**: "Water Network Balance"

#### **🌡️ Bottom Row: System Health**

**Chart 3: Temperature Monitoring**
1. **Add Chart** → **Line Chart**
2. **Data Source**: `Real_Time_Metrics`
3. **Dimension**: `datetime_combined`
4. **Metrics**: `sant_anna_temp`, `seneca_temp`
5. **Title**: "Temperature Monitoring"

### **Page 2: Consumption Patterns**

#### **🔥 Consumption Heatmap**
1. **Add Chart** → **Heatmap**
2. **Data Source**: `Hourly_Patterns`
3. **Row Dimension**: `day_name`
4. **Column Dimension**: `hour_of_day`
5. **Metric**: `avg_flow_rate`
6. **Title**: "Consumption Patterns by Hour and Day"
7. **Color Scale**: Blue (low) to Red (high)

#### **📊 Weekly Pattern Analysis**
1. **Add Chart** → **Column Chart**
2. **Data Source**: `Hourly_Patterns`
3. **Dimension**: `hour_of_day`
4. **Metric**: `avg_flow_rate`
5. **Breakdown Dimension**: `day_name`
6. **Title**: "Average Hourly Consumption by Day of Week"

### **Page 3: Historical Analysis**

#### **📈 Daily Trends**
1. **Add Chart** → **Time Series Chart**
2. **Data Source**: `Daily_Aggregates`
3. **Date Range Dimension**: `date_parsed`
4. **Metrics**: `avg_sant_anna_flow`, `avg_tank_output`, `avg_external_supply`
5. **Title**: "Daily Average Flow Rates"

#### **📊 Efficiency Metrics**
1. **Add Chart** → **Table**
2. **Data Source**: `Daily_Aggregates`
3. **Dimensions**: `date_string`
4. **Metrics**: 
   - `avg_sant_anna_flow`
   - `avg_tank_output`
   - `avg_apparent_loss`
   - `total_volume_m3`
5. **Title**: "Daily Efficiency Summary"

---

## 🎨 **Dashboard Styling**

### **Color Scheme:**
- **Primary**: #1a73e8 (Google Blue)
- **Success**: #34a853 (Green)
- **Warning**: #fbbc04 (Yellow)
- **Error**: #ea4335 (Red)
- **Background**: #f8f9fa (Light Gray)

### **Conditional Formatting:**

**For Flow Status Scorecard:**
- NORMAL: Green background (#34a853)
- HIGH: Red background (#ea4335)
- LOW: Orange background (#fbbc04)

**For Flow Rate Metrics:**
- > 100 L/S: Red text
- 50-100 L/S: Green text
- < 50 L/S: Orange text

---

## 🔧 **Advanced Features to Add**

### **1. Date Range Control**
1. **Add Control** → **Date Range Control**
2. Position at top of dashboard
3. **Default Range**: Last 7 days

### **2. Filter Controls**
1. **Add Control** → **Drop-down list**
2. **Dimension**: `flow_status`
3. **Title**: "Filter by Status"

### **3. Dashboard Theme**
1. **Theme and Layout** → **Corporate Theme**
2. **Background**: White
3. **Font**: Roboto

---

## 📱 **Mobile Optimization**

1. **View** → **Mobile Layout**
2. Rearrange charts for mobile viewing:
   - Stack KPI cards vertically
   - Make time series charts full width
   - Hide complex tables on mobile

---

## 🚀 **Sharing and Collaboration**

### **Share Dashboard:**
1. Click **Share** button (top right)
2. **Get shareable link** for view-only access
3. **Add people** for editor access
4. **Email reports** - set up weekly automated reports

### **Embed Options:**
1. **File** → **Embed**
2. Get embed code for websites/applications

---

## ✅ **Final Checklist**

- [ ] Connected to BigQuery data source
- [ ] Created 3 custom query data sources
- [ ] Built KPI scorecards
- [ ] Added time series charts
- [ ] Created consumption heatmap
- [ ] Set up date range controls
- [ ] Applied conditional formatting
- [ ] Configured mobile layout
- [ ] Shared dashboard with team
- [ ] Set up automated reports

**🎉 Your professional water infrastructure dashboard is ready!**

---

## 🔄 **Next Steps After Setup**

1. **Monitor daily** for unusual patterns
2. **Set up data refresh** (automatic every hour)
3. **Create alerts** using BigQuery scheduled queries
4. **Add more sensors** as data becomes available
5. **Expand with ML predictions** from your forecasting model

**Time to complete**: 30-45 minutes
**Result**: Enterprise-grade water infrastructure dashboard! 🌊📊 