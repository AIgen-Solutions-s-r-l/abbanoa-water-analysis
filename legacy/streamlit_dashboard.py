import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Abbanoa Water Infrastructure Monitor",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-normal {
        color: #28a745;
        font-weight: bold;
    }
    .status-alert {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Initialize BigQuery client
@st.cache_resource
def init_bigquery_client():
    return bigquery.Client(project="abbanoa-464816")


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(time_range_option="Last 24 Hours"):
    """Load water infrastructure data from BigQuery"""
    client = init_bigquery_client()

    # Map time range options to actual data periods
    if time_range_option == "Last 6 Hours":
        # Show last 6 hours of available data
        limit_clause = "LIMIT 12"  # ~6 hours of 30-min intervals
    elif time_range_option == "Last 24 Hours":
        # Show last 24 hours of available data
        limit_clause = "LIMIT 48"  # ~24 hours of 30-min intervals
    elif time_range_option == "Last 3 Days":
        # Show last 3 days of available data
        limit_clause = "LIMIT 144"  # ~3 days of 30-min intervals
    else:  # Last Week
        # Show all available data (it's only about 4 months)
        limit_clause = ""

    query = f"""
    WITH recent_data AS (
      SELECT 
        DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as datetime,
        selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as sant_anna_flow,
        selargius_nodo_via_seneca_portata_w_istantanea_diretta as seneca_flow,
        selargius_serbatoio_selargius_portata_uscita as tank_output,
        quartucciu_serbatoio_cuccuru_linu_portata_selargius as external_supply,
        selargius_nodo_via_sant_anna_temperatura_interna as sant_anna_temp,
        selargius_nodo_via_seneca_temperatura_interna as seneca_temp,
        data as date_string,
        ora as time_string
      FROM `abbanoa-464816.water_infrastructure.sensor_data`
      WHERE data IS NOT NULL AND ora IS NOT NULL
    )
    SELECT * FROM recent_data 
    WHERE datetime IS NOT NULL
    ORDER BY datetime DESC
    {limit_clause}
    """

    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_hourly_patterns():
    """Load hourly consumption patterns"""
    client = init_bigquery_client()

    query = """
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
      COUNT(*) as measurements
    FROM `abbanoa-464816.water_infrastructure.sensor_data`
    WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
      AND ora IS NOT NULL 
      AND data IS NOT NULL
    GROUP BY hour_of_day, day_of_week, day_name
    ORDER BY day_of_week, hour_of_day
    """

    try:
        return client.query(query).to_dataframe()
    except Exception as e:
        st.error(f"Error loading pattern data: {str(e)}")
        return pd.DataFrame()


def get_system_status(flow_rate, temperature):
    """Determine system status based on current metrics"""
    if pd.isna(flow_rate) or pd.isna(temperature):
        return "🔴 NO DATA", "alert"

    if flow_rate > 120:
        return "🔴 HIGH FLOW ALERT", "alert"
    elif flow_rate < 30:
        return "🟠 LOW FLOW WARNING", "warning"
    elif temperature > 25:
        return "🟠 HIGH TEMPERATURE", "warning"
    else:
        return "🟢 SYSTEM NORMAL", "normal"


# Sidebar
st.sidebar.title("🌊 Abbanoa Control Center")
st.sidebar.markdown("Real-time monitoring of Selargius water network")
st.sidebar.markdown("---")

# Time range selector
time_range = st.sidebar.selectbox(
    "📅 Select Time Range",
    ["Last 6 Hours", "Last 24 Hours", "Last 3 Days", "Last Week"],
    index=1,
)

# Time ranges now handled directly in load_data function

# Refresh data
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Dashboard Features:**")
st.sidebar.markdown("• Real-time flow monitoring")
st.sidebar.markdown("• Temperature tracking")
st.sidebar.markdown("• Network balance analysis")
st.sidebar.markdown("• Consumption patterns")
st.sidebar.markdown("• System alerts")

# Main dashboard
st.markdown(
    '<h1 class="main-header">🌊 Abbanoa Water Infrastructure Dashboard</h1>',
    unsafe_allow_html=True,
)

# Load data
with st.spinner("🔄 Loading water infrastructure data..."):
    df = load_data(time_range)

if df.empty:
    st.error("❌ No data available for the selected time range.")
    st.stop()

# Current status row
st.subheader("📊 Current System Status")
col1, col2, col3, col4 = st.columns(4)

latest = df.iloc[0]

with col1:
    current_flow = latest["sant_anna_flow"]
    prev_flow = df.iloc[1]["sant_anna_flow"] if len(df) > 1 else current_flow
    flow_delta = current_flow - prev_flow if not pd.isna(prev_flow) else 0

    st.metric(
        label="🌊 Current Flow Rate",
        value=f"{current_flow:.1f} L/S" if not pd.isna(current_flow) else "No data",
        delta=f"{flow_delta:.1f} L/S" if not pd.isna(flow_delta) else None,
    )

with col2:
    tank_output = latest["tank_output"]
    prev_tank = df.iloc[1]["tank_output"] if len(df) > 1 else tank_output
    tank_delta = tank_output - prev_tank if not pd.isna(prev_tank) else 0

    st.metric(
        label="🏭 Tank Output",
        value=f"{tank_output:.1f} L/S" if not pd.isna(tank_output) else "No data",
        delta=f"{tank_delta:.1f} L/S" if not pd.isna(tank_delta) else None,
    )

with col3:
    temperature = latest["sant_anna_temp"]
    prev_temp = df.iloc[1]["sant_anna_temp"] if len(df) > 1 else temperature
    temp_delta = temperature - prev_temp if not pd.isna(prev_temp) else 0

    st.metric(
        label="🌡️ Temperature",
        value=f"{temperature:.1f}°C" if not pd.isna(temperature) else "No data",
        delta=f"{temp_delta:.1f}°C" if not pd.isna(temp_delta) else None,
    )

with col4:
    status_text, status_class = get_system_status(current_flow, temperature)
    st.metric(label="🚨 System Status", value=status_text)

# Charts section
st.markdown("---")

# Flow rate trends
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Flow Rate Trends")
    if not df.empty:
        fig = go.Figure()

        # Sant Anna flow
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["sant_anna_flow"],
                name="Sant Anna Flow",
                line=dict(color="#1f77b4", width=2),
                hovertemplate="%{y:.1f} L/S<br>%{x}<extra></extra>",
            )
        )

        # Tank output
        fig.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["tank_output"],
                name="Tank Output",
                line=dict(color="#ff7f0e", width=2),
                hovertemplate="%{y:.1f} L/S<br>%{x}<extra></extra>",
            )
        )

        # External supply (if available)
        if "external_supply" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["datetime"],
                    y=df["external_supply"],
                    name="External Supply",
                    line=dict(color="#2ca02c", width=2),
                    hovertemplate="%{y:.1f} L/S<br>%{x}<extra></extra>",
                )
            )

        fig.update_layout(
            title="Water Flow Rates Over Time",
            xaxis_title="Time",
            yaxis_title="Flow Rate (L/S)",
            height=400,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🌡️ Temperature Monitoring")
    if not df.empty and "sant_anna_temp" in df.columns:
        fig = px.line(
            df,
            x="datetime",
            y="sant_anna_temp",
            title="Temperature Trend",
            labels={"sant_anna_temp": "Temperature (°C)", "datetime": "Time"},
        )
        fig.update_layout(height=400)
        fig.update_traces(line_color="#d62728", line_width=2)
        st.plotly_chart(fig, use_container_width=True)

# Network balance analysis
st.subheader("⚖️ Water Network Balance Analysis")
if not df.empty:
    # Calculate network balance
    df_balance = df.copy()
    df_balance["total_input"] = (
        df_balance["sant_anna_flow"].fillna(0)
        + df_balance["seneca_flow"].fillna(0)
        + df_balance["external_supply"].fillna(0)
    )
    df_balance["apparent_loss"] = df_balance["total_input"] - df_balance[
        "tank_output"
    ].fillna(0)

    fig = go.Figure()

    # Total input (area chart)
    fig.add_trace(
        go.Scatter(
            x=df_balance["datetime"],
            y=df_balance["total_input"],
            fill="tonexty",
            name="Total Input",
            line_color="rgba(31, 119, 180, 0.7)",
            hovertemplate="Input: %{y:.1f} L/S<extra></extra>",
        )
    )

    # Tank output
    fig.add_trace(
        go.Scatter(
            x=df_balance["datetime"],
            y=df_balance["tank_output"],
            name="Tank Output",
            line_color="#ff7f0e",
            hovertemplate="Output: %{y:.1f} L/S<extra></extra>",
        )
    )

    # Apparent loss
    fig.add_trace(
        go.Scatter(
            x=df_balance["datetime"],
            y=df_balance["apparent_loss"],
            name="Apparent Loss",
            line_color="#d62728",
            hovertemplate="Loss: %{y:.1f} L/S<extra></extra>",
        )
    )

    fig.update_layout(
        title="Water Network Balance: Input vs Output vs Losses",
        xaxis_title="Time",
        yaxis_title="Flow Rate (L/S)",
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

# Consumption patterns heatmap
st.subheader("🔥 Consumption Patterns")
with st.spinner("Loading consumption patterns..."):
    patterns_df = load_hourly_patterns()

if not patterns_df.empty:
    # Create heatmap
    heatmap_pivot = patterns_df.pivot(
        index="day_name", columns="hour_of_day", values="avg_flow_rate"
    )

    # Reorder days
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    heatmap_pivot = heatmap_pivot.reindex(day_order)

    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Hour of Day", y="Day of Week", color="Flow Rate (L/S)"),
        title="Average Water Consumption Patterns",
        color_continuous_scale="Blues",
        aspect="auto",
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Key performance indicators
st.markdown("---")
st.subheader("📋 Key Performance Indicators")

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_flow = df["sant_anna_flow"].mean()
        st.metric("📊 Average Flow Rate", f"{avg_flow:.1f} L/S")

    with col2:
        max_flow = df["sant_anna_flow"].max()
        st.metric("📈 Peak Flow Rate", f"{max_flow:.1f} L/S")

    with col3:
        total_volume = (
            df["sant_anna_flow"].sum() * 0.5 / 1000
        )  # Assuming 30-min intervals, convert to m³
        st.metric("🏺 Total Volume", f"{total_volume:.1f} m³")

    with col4:
        efficiency = (
            (df["tank_output"].sum() / df["sant_anna_flow"].sum() * 100)
            if df["sant_anna_flow"].sum() > 0
            else 0
        )
        st.metric("⚡ Network Efficiency", f"{efficiency:.1f}%")

# Recent alerts/anomalies
st.markdown("---")
st.subheader("🚨 Recent Alerts")

# Find anomalies in recent data
if not df.empty:
    alerts = []
    for idx, row in df.head(20).iterrows():
        flow = row["sant_anna_flow"]
        temp = row["sant_anna_temp"]
        time = row["datetime"]

        if not pd.isna(flow):
            if flow > 120:
                alerts.append(
                    f"🔴 {time.strftime('%H:%M %d/%m')} - High flow alert: {flow:.1f} L/S"
                )
            elif flow < 30:
                alerts.append(
                    f"🟠 {time.strftime('%H:%M %d/%m')} - Low flow warning: {flow:.1f} L/S"
                )

        if not pd.isna(temp) and temp > 25:
            alerts.append(
                f"🟠 {time.strftime('%H:%M %d/%m')} - High temperature: {temp:.1f}°C"
            )

    if alerts:
        for alert in alerts[:5]:  # Show last 5 alerts
            st.warning(alert)
    else:
        st.success("✅ No recent alerts - System operating normally")

# Data quality section
with st.expander("📊 Data Quality & Raw Data"):
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Data Quality Metrics:**")
        total_records = len(df)
        missing_flow = df["sant_anna_flow"].isna().sum()
        missing_temp = df["sant_anna_temp"].isna().sum()

        st.write(f"• Total records: {total_records}")
        st.write(
            f"• Missing flow data: {missing_flow} ({missing_flow/total_records*100:.1f}%)"
        )
        st.write(
            f"• Missing temperature data: {missing_temp} ({missing_temp/total_records*100:.1f}%)"
        )
        st.write(
            f"• Data completeness: {(total_records-missing_flow)/total_records*100:.1f}%"
        )

    with col2:
        st.write("**Time Range:**")
        if not df.empty:
            st.write(f"• From: {df['datetime'].min().strftime('%Y-%m-%d %H:%M')}")
            st.write(f"• To: {df['datetime'].max().strftime('%Y-%m-%d %H:%M')}")
            st.write(f"• Duration: {time_range}")
            st.write("• Update frequency: ~30 minutes")

    # Raw data table
    st.write("**Raw Data Preview:**")
    st.dataframe(
        df[
            [
                "datetime",
                "sant_anna_flow",
                "tank_output",
                "sant_anna_temp",
                "external_supply",
            ]
        ].head(20),
        use_container_width=True,
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🌊 Abbanoa Water Infrastructure Dashboard | 
        Data refreshes every 5 minutes | 
        Built with Streamlit & BigQuery
    </div>
    """,
    unsafe_allow_html=True,
)

# Auto-refresh notification
st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Tip:** Dashboard auto-refreshes cached data every 5 minutes. Use the refresh button for immediate updates."
)
