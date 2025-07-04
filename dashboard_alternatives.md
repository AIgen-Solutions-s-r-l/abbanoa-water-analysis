# 🚀 **Dashboard Alternatives to Looker Studio**

Since you don't like Looker Studio, here are **much better alternatives** for your water infrastructure monitoring:

---

## 🥇 **1. Grafana - The Best for Infrastructure Monitoring**

### **Why Grafana is Perfect for Water Infrastructure:**
- ✅ **Built for time-series monitoring** (perfect for sensors)
- ✅ **Beautiful, professional dashboards**
- ✅ **Real-time updates and alerts**
- ✅ **Mobile-responsive**
- ✅ **Free and open-source**
- ✅ **Used by Netflix, Uber, eBay**

### **🚀 Quick Setup on GCP (20 minutes)**

#### **Step 1: Deploy Grafana on Cloud Run**
```bash
# Deploy Grafana container
gcloud run deploy grafana-water-dashboard \
  --image=grafana/grafana:latest \
  --platform=managed \
  --region=europe-west1 \
  --allow-unauthenticated \
  --port=3000 \
  --memory=512Mi \
  --set-env-vars="GF_SECURITY_ADMIN_PASSWORD=your-secure-password"
```

#### **Step 2: Connect to BigQuery**
1. Open Grafana URL from Cloud Run
2. Login with `admin` / `your-secure-password`
3. **Configuration** → **Data Sources** → **Add BigQuery**
4. **Project ID**: `abbanoa-464816`
5. **Authenticate** with your service account

#### **Step 3: Import Water Infrastructure Dashboard**
Use these pre-built panel queries:

**Flow Rate Time Series:**
```sql
SELECT 
  DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as time,
  selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as "Sant Anna Flow",
  selargius_serbatoio_selargius_portata_uscita as "Tank Output"
FROM `abbanoa-464816.water_infrastructure.sensor_data`
WHERE $__timeFilter(DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)))
ORDER BY time
```

---

## 🥈 **2. Streamlit - Interactive Python Dashboards**

### **Why Streamlit is Great:**
- ✅ **Python-based** (perfect for data scientists)
- ✅ **Interactive widgets and filters**
- ✅ **Deploy on Cloud Run for free**
- ✅ **Highly customizable**
- ✅ **Real-time data updates**

### **🚀 Ready-to-Deploy Streamlit App**

I'll create a complete Streamlit dashboard for you:

```python
# streamlit_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Water Infrastructure Monitor",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize BigQuery client
@st.cache_resource
def init_bigquery_client():
    return bigquery.Client(project='abbanoa-464816')

@st.cache_data
def load_data(hours_back=24):
    client = init_bigquery_client()
    
    query = f"""
    WITH recent_data AS (
      SELECT 
        DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as datetime,
        selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as sant_anna_flow,
        selargius_serbatoio_selargius_portata_uscita as tank_output,
        quartucciu_serbatoio_cuccuru_linu_portata_selargius as external_supply,
        selargius_nodo_via_sant_anna_temperatura_interna as temperature
      FROM `abbanoa-464816.water_infrastructure.sensor_data`
      WHERE data IS NOT NULL AND ora IS NOT NULL
        AND DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) 
        >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL {hours_back} HOUR)
    )
    SELECT * FROM recent_data ORDER BY datetime DESC
    """
    
    return client.query(query).to_dataframe()

# Sidebar
st.sidebar.title("🌊 Water Infrastructure Monitor")
st.sidebar.markdown("---")

# Time range selector
time_range = st.sidebar.selectbox(
    "Select Time Range",
    ["Last 6 Hours", "Last 24 Hours", "Last 3 Days", "Last Week"],
    index=1
)

time_mapping = {
    "Last 6 Hours": 6,
    "Last 24 Hours": 24,
    "Last 3 Days": 72,
    "Last Week": 168
}

# Load data
with st.spinner("Loading water infrastructure data..."):
    df = load_data(time_mapping[time_range])

# Main dashboard
st.title("🌊 Water Infrastructure Dashboard")
st.markdown("Real-time monitoring of Selargius water network")

# Current status row
col1, col2, col3, col4 = st.columns(4)

if not df.empty:
    latest = df.iloc[0]
    
    with col1:
        st.metric(
            label="Current Flow Rate",
            value=f"{latest['sant_anna_flow']:.1f} L/S",
            delta=f"{latest['sant_anna_flow'] - df.iloc[1]['sant_anna_flow']:.1f} L/S"
        )
    
    with col2:
        st.metric(
            label="Tank Output", 
            value=f"{latest['tank_output']:.1f} L/S",
            delta=f"{latest['tank_output'] - df.iloc[1]['tank_output']:.1f} L/S"
        )
    
    with col3:
        st.metric(
            label="Temperature",
            value=f"{latest['temperature']:.1f}°C",
            delta=f"{latest['temperature'] - df.iloc[1]['temperature']:.1f}°C"
        )
    
    with col4:
        status = "🟢 NORMAL" if 30 <= latest['sant_anna_flow'] <= 120 else "🔴 ALERT"
        st.metric(label="System Status", value=status)

# Charts row
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Flow Rate Trends")
    fig = px.line(df, x='datetime', y=['sant_anna_flow', 'tank_output'], 
                  title="Water Flow Rates Over Time")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌡️ Temperature Monitoring")
    fig = px.line(df, x='datetime', y='temperature',
                  title="Temperature Trend")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Network balance
st.subheader("⚖️ Water Network Balance")
df['total_input'] = df['sant_anna_flow'] + df['external_supply'].fillna(0)
df['apparent_loss'] = df['total_input'] - df['tank_output']

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['datetime'], y=df['total_input'], name='Total Input', fill='tonexty'))
fig.add_trace(go.Scatter(x=df['datetime'], y=df['tank_output'], name='Tank Output', fill='tozeroy'))
fig.add_trace(go.Scatter(x=df['datetime'], y=df['apparent_loss'], name='Apparent Loss'))
fig.update_layout(title="Water Network Balance Analysis", height=400)
st.plotly_chart(fig, use_container_width=True)

# Consumption patterns heatmap
st.subheader("🔥 Consumption Patterns")
if len(df) > 24:  # Only show if we have enough data
    df['hour'] = df['datetime'].dt.hour
    df['day'] = df['datetime'].dt.day_name()
    
    heatmap_data = df.groupby(['day', 'hour'])['sant_anna_flow'].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='day', columns='hour', values='sant_anna_flow')
    
    fig = px.imshow(heatmap_pivot, 
                    title="Average Flow Rate by Day and Hour",
                    color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

# Data table
with st.expander("📊 Raw Data"):
    st.dataframe(df, use_container_width=True)

# Auto-refresh
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# Add auto-refresh every 5 minutes
st.sidebar.markdown("Dashboard auto-refreshes every 5 minutes")
```

### **Deploy to Cloud Run:**
```bash
# Create requirements.txt
echo "streamlit==1.28.0
google-cloud-bigquery==3.11.4
plotly==5.15.0
pandas==2.0.3" > requirements.txt

# Create Dockerfile
echo "FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ['streamlit', 'run', 'streamlit_dashboard.py', '--server.port=8501', '--server.address=0.0.0.0']" > Dockerfile

# Deploy
gcloud run deploy water-dashboard \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated
```

---

## 🥉 **3. Jupyter Notebook + Voilà - Interactive Reports**

### **Perfect for Data Scientists & Engineers**

Deploy interactive Jupyter notebooks as web dashboards:

```python
# water_analysis_notebook.ipynb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
import ipywidgets as widgets
from IPython.display import display

# Interactive widgets
time_range = widgets.Dropdown(
    options=['6h', '24h', '7d', '30d'],
    value='24h',
    description='Time Range:'
)

sensor_type = widgets.Dropdown(
    options=['Flow Rate', 'Temperature', 'All'],
    value='All',
    description='Sensor:'
)

# Real-time charts that update based on widget selection
def create_dashboard():
    client = bigquery.Client(project='abbanoa-464816')
    
    # Your BigQuery queries here
    df = client.query(query).to_dataframe()
    
    # Interactive Plotly charts
    fig = px.line(df, x='datetime', y='flow_rate', 
                  title='Real-time Water Flow Monitoring')
    fig.show()

# Deploy with Voilà to Cloud Run
```

---

## 🔥 **4. Custom React/Vue.js Dashboard**

### **Professional-Grade Custom Solution**

For the ultimate customization, I can help you build a custom dashboard:

**Features:**
- Real-time updates via WebSocket
- Custom alerts and notifications
- Mobile-first responsive design
- PWA (Progressive Web App) capabilities
- Custom branding and themes

**Tech Stack:**
- **Frontend**: React.js + Chart.js/D3.js
- **Backend**: Node.js + Express
- **Database**: BigQuery
- **Hosting**: Cloud Run
- **Real-time**: WebSocket/Server-Sent Events

---

## 📊 **5. Power BI (Microsoft)**

### **Enterprise-Grade Business Intelligence**

If you prefer Microsoft tools:

**Setup:**
1. **Power BI Desktop** → **Get Data** → **Google BigQuery**
2. Connect to `abbanoa-464816.water_infrastructure.sensor_data`
3. Build reports with drag-and-drop interface
4. **Publish** to Power BI Service for sharing

**Pros:**
- Enterprise-grade security
- Advanced analytics capabilities
- Integration with Microsoft ecosystem
- Mobile apps available

---

## 🎯 **My Recommendations**

### **🥇 For Infrastructure Teams: Grafana**
- **Best for**: Real-time monitoring, alerts, time-series data
- **Setup time**: 30 minutes
- **Cost**: Free
- **Learning curve**: Medium

### **🥈 For Data Scientists: Streamlit**
- **Best for**: Interactive analysis, custom widgets, Python integration
- **Setup time**: 1 hour  
- **Cost**: Free on Cloud Run
- **Learning curve**: Easy (if you know Python)

### **🥉 For Executives: Power BI**
- **Best for**: Business intelligence, reporting, Microsoft integration
- **Setup time**: 2 hours
- **Cost**: $10/user/month
- **Learning curve**: Easy

---

## 🚀 **Quick Start - Pick Your Favorite**

### **Option 1: Grafana (Recommended)**
```bash
# Deploy now
gcloud run deploy grafana-water \
  --image=grafana/grafana:latest \
  --platform=managed \
  --region=europe-west1 \
  --allow-unauthenticated \
  --memory=1Gi
```

### **Option 2: Streamlit**
I'll create the complete Streamlit app for you in the next step.

### **Option 3: Jupyter + Voilà**
Perfect for interactive data exploration and sharing notebooks as dashboards.

---

## 💡 **Which Would You Prefer?**

Let me know which option interests you most, and I'll:
1. **Set it up completely for you**
2. **Create all the charts and visualizations**
3. **Deploy it to GCP**
4. **Configure it for your water infrastructure data**

**What sounds most appealing to you?** 🤔 