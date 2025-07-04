# 🚀 **Water Infrastructure Dashboard - Deployment Guide**

I've created a **professional Streamlit dashboard** for your water infrastructure monitoring. Here are multiple ways to deploy it:

---

## 🎯 **Option 1: Run Locally (Immediate - 2 minutes)**

### **Start Your Dashboard Now:**
```bash
# In your current directory
streamlit run streamlit_dashboard.py --server.port 8501 --server.address 0.0.0.0
```

**🌐 Access at**: `http://localhost:8501`

**✅ Perfect for:**
- Immediate testing and development
- Private internal use
- Proof of concept demonstrations

---

## 🌊 **Option 2: Streamlit Community Cloud (FREE Forever)**

### **Deploy in 5 minutes - Zero cost:**

1. **Push to GitHub**:
   ```bash
   git init
   git add streamlit_dashboard.py requirements.txt
   git commit -m "Add water infrastructure dashboard"
   git remote add origin https://github.com/YOUR_USERNAME/abbanoa-dashboard.git
   git push -u origin main
   ```

2. **Deploy**:
   - Go to [`share.streamlit.io`](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - **App Path**: `streamlit_dashboard.py`
   - **Deploy**!

**✅ Benefits:**
- ✅ **100% FREE** forever
- ✅ **HTTPS** automatic
- ✅ **Auto-updates** from GitHub
- ✅ **Share with anyone** via URL
- ✅ **No server maintenance**

---

## ⚡ **Option 3: Cloud Run (Scalable Production)**

### **For production use with automatic scaling:**

**Fix the Docker build first:**
```dockerfile
# Updated Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY streamlit_dashboard.py .

# Configure Streamlit
RUN mkdir -p ~/.streamlit
RUN echo "[server]" > ~/.streamlit/config.toml
RUN echo "headless = true" >> ~/.streamlit/config.toml
RUN echo "port = 8501" >> ~/.streamlit/config.toml
RUN echo "enableCORS = false" >> ~/.streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Deploy:**
```bash
gcloud run deploy abbanoa-dashboard \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 300
```

---

## 🔧 **Option 4: Grafana (Infrastructure Monitoring Pro)**

### **For serious infrastructure teams:**

**1. Deploy Grafana:**
```bash
gcloud run deploy grafana-abbanoa \
  --image=grafana/grafana:latest \
  --platform=managed \
  --region=europe-west1 \
  --allow-unauthenticated \
  --memory=1Gi \
  --set-env-vars="GF_SECURITY_ADMIN_PASSWORD=AbbanoacAcqua2024"
```

**2. Configure BigQuery Data Source:**
- **URL**: Your Grafana Cloud Run URL
- **Login**: admin / AbbanoacAcqua2024
- **Add Data Source** → **BigQuery**
- **Project**: `abbanoa-464816`
- **Default Dataset**: `water_infrastructure`

**3. Import Dashboard JSON:**
```json
{
  "dashboard": {
    "title": "Abbanoa Water Infrastructure",
    "panels": [
      {
        "title": "Current Flow Rate",
        "type": "stat",
        "targets": [{
          "rawSql": "SELECT selargius_nodo_via_sant_anna_portata_w_istantanea_diretta FROM `abbanoa-464816.water_infrastructure.sensor_data` ORDER BY _ingestion_timestamp DESC LIMIT 1"
        }]
      },
      {
        "title": "Flow Rate Trends",
        "type": "timeseries",
        "targets": [{
          "rawSql": "SELECT DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as time, selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow FROM `abbanoa-464816.water_infrastructure.sensor_data` WHERE $__timeFilter(DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M/%S', ora))) ORDER BY time"
        }]
      }
    ]
  }
}
```

---

## 📱 **Option 5: Jupyter Dashboard (Data Science)**

### **For interactive analysis and sharing:**

**1. Create Jupyter Dashboard:**
```python
# jupyter_dashboard.py
import jupyter_dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from google.cloud import bigquery

app = jupyter_dash.JupyterDash(__name__)

# Layout
app.layout = html.Div([
    html.H1("🌊 Abbanoa Water Infrastructure"),
    dcc.Graph(id='flow-chart'),
    dcc.Interval(id='interval', interval=300000)  # Update every 5 minutes
])

@app.callback(Output('flow-chart', 'figure'), Input('interval', 'n_intervals'))
def update_chart(n):
    client = bigquery.Client(project='abbanoa-464816')
    query = """
    SELECT 
      DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as datetime,
      selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow
    FROM `abbanoa-464816.water_infrastructure.sensor_data`
    WHERE data IS NOT NULL AND ora IS NOT NULL
    ORDER BY datetime DESC LIMIT 100
    """
    df = client.query(query).to_dataframe()
    fig = px.line(df, x='datetime', y='flow', title='Real-time Flow Rate')
    return fig

# Run
app.run_server(host='0.0.0.0', port=8050)
```

---

## 🏆 **My Recommendation: Streamlit Community Cloud**

### **Why this is the best choice for you:**

✅ **FREE** - No hosting costs ever  
✅ **HTTPS** - Secure by default  
✅ **Easy sharing** - Send URL to anyone  
✅ **Auto-updates** - Sync with GitHub  
✅ **No maintenance** - Streamlit handles everything  
✅ **Professional** - Used by thousands of companies  

### **Quick Setup (5 minutes):**

1. **Create GitHub repo** with your dashboard files
2. **Go to** [`share.streamlit.io`](https://share.streamlit.io)  
3. **Connect GitHub** and select your repo
4. **Deploy** - Get instant HTTPS URL
5. **Share** dashboard with your team

---

## 🚀 **What Your Dashboard Includes:**

### **📊 Real-Time Monitoring:**
- Current flow rates with trend indicators
- Temperature monitoring across sensors
- System status alerts (Normal/Warning/Alert)
- Network balance analysis

### **📈 Advanced Analytics:**
- Consumption pattern heatmap (hourly/daily)
- Water network efficiency metrics
- Apparent loss calculations
- Historical trend analysis

### **🔔 Smart Alerts:**
- Automatic anomaly detection
- Flow rate thresholds (>120 L/S or <30 L/S)
- Temperature warnings (>25°C)
- Data quality monitoring

### **📱 Interactive Features:**
- Time range filters (6h, 24h, 3d, 1w)
- Real-time data refresh
- Mobile-responsive design
- Expandable raw data tables

---

## 🎯 **Next Steps:**

### **Immediate (Today):**
1. **Test locally**: `streamlit run streamlit_dashboard.py`
2. **Verify data**: Check all charts load correctly
3. **Take screenshots** for documentation

### **This Week:**
1. **Deploy to Streamlit Cloud** (recommended)
2. **Share URL** with operations team
3. **Set up GitHub repo** for version control

### **Advanced (Next Week):**
1. **Add ML predictions** from your BigQuery models
2. **Set up automated alerts** via email/SMS
3. **Create mobile app** using the dashboard API

---

## 💡 **Pro Tips:**

### **Performance Optimization:**
- Dashboard caches data for 5 minutes
- Use time range filters for large datasets
- BigQuery queries are optimized for speed

### **Customization:**
- Edit `streamlit_dashboard.py` for custom metrics
- Modify colors/themes in the CSS section
- Add new sensors by updating BigQuery queries

### **Security:**
- Use environment variables for sensitive data
- Set up authentication if needed
- Monitor BigQuery usage and costs

**Your water infrastructure monitoring is now enterprise-grade!** 🌊✨

**Which deployment option would you like to try first?** 