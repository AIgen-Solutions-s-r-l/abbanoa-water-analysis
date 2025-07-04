"""Streamlit dashboard for water infrastructure monitoring."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dependency_injector.wiring import Provide, inject

from src.application.dto.analysis_results_dto import (
    AnomalyDetectionResultDTO,
    ConsumptionPatternDTO,
    NetworkEfficiencyResultDTO,
)
from src.application.use_cases.analyze_consumption_patterns import (
    AnalyzeConsumptionPatternsUseCase,
)
from src.application.use_cases.calculate_network_efficiency import (
    CalculateNetworkEfficiencyUseCase,
)
from src.application.use_cases.detect_network_anomalies import (
    DetectNetworkAnomaliesUseCase,
)
from src.infrastructure.di_container import Container


# Page configuration
st.set_page_config(
    page_title="Abbanoa Water Infrastructure Monitor",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
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
""", unsafe_allow_html=True)


class WaterInfrastructureDashboard:
    """Main dashboard application."""
    
    @inject
    def __init__(
        self,
        analyze_consumption_use_case: AnalyzeConsumptionPatternsUseCase = Provide[Container.analyze_consumption_patterns_use_case],
        detect_anomalies_use_case: DetectNetworkAnomaliesUseCase = Provide[Container.detect_network_anomalies_use_case],
        calculate_efficiency_use_case: CalculateNetworkEfficiencyUseCase = Provide[Container.calculate_network_efficiency_use_case],
    ):
        self.analyze_consumption_use_case = analyze_consumption_use_case
        self.detect_anomalies_use_case = detect_anomalies_use_case
        self.calculate_efficiency_use_case = calculate_efficiency_use_case
    
    def run(self):
        """Run the dashboard application."""
        st.markdown('<h1 class="main-header">🌊 Abbanoa Water Infrastructure Monitor</h1>', unsafe_allow_html=True)
        
        # Sidebar configuration
        with st.sidebar:
            st.header("Configuration")
            
            # Time range selection
            time_range = st.selectbox(
                "Time Range",
                ["Last 6 Hours", "Last 24 Hours", "Last 3 Days", "Last Week"],
                index=1
            )
            
            # Node selection
            selected_nodes = st.multiselect(
                "Select Nodes",
                ["All Nodes", "Sant'Anna", "Seneca", "Selargius Tank", "External Supply"],
                default=["All Nodes"]
            )
            
            # Refresh button
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
            
            # Display last update time
            st.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "🔍 Anomaly Detection",
            "📈 Consumption Patterns",
            "🔗 Network Efficiency",
            "📋 Reports"
        ])
        
        with tab1:
            self._render_overview_tab(time_range, selected_nodes)
        
        with tab2:
            self._render_anomaly_tab(time_range)
        
        with tab3:
            self._render_consumption_tab(time_range, selected_nodes)
        
        with tab4:
            self._render_efficiency_tab(time_range)
        
        with tab5:
            self._render_reports_tab()
    
    def _render_overview_tab(self, time_range: str, selected_nodes: List[str]):
        """Render the overview tab."""
        st.header("System Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Active Nodes",
                value="12",
                delta="2 new this week"
            )
        
        with col2:
            st.metric(
                label="Total Flow (24h)",
                value="1,234 m³",
                delta="12% vs yesterday"
            )
        
        with col3:
            st.metric(
                label="Avg Pressure",
                value="4.2 bar",
                delta="-0.1 bar"
            )
        
        with col4:
            st.metric(
                label="System Efficiency",
                value="92.5%",
                delta="2.1%"
            )
        
        # Real-time monitoring chart
        st.subheader("Real-time Flow Monitoring")
        
        # Create sample data for demonstration
        time_data = pd.date_range(
            end=datetime.now(),
            periods=48,
            freq='30min'
        )
        
        flow_data = pd.DataFrame({
            'timestamp': time_data,
            'Sant\'Anna': 100 + 20 * pd.Series(range(48)).apply(lambda x: pd.np.sin(x/10)),
            'Seneca': 80 + 15 * pd.Series(range(48)).apply(lambda x: pd.np.cos(x/8)),
            'Tank Output': 180 + 25 * pd.Series(range(48)).apply(lambda x: pd.np.sin(x/12))
        })
        
        fig = px.line(
            flow_data,
            x='timestamp',
            y=['Sant\'Anna', 'Seneca', 'Tank Output'],
            title='Flow Rate Trends (L/s)',
            labels={'value': 'Flow Rate (L/s)', 'timestamp': 'Time'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Node status grid
        st.subheader("Node Status")
        
        node_cols = st.columns(4)
        nodes = [
            ("Sant'Anna", "Active", "normal", 102.5),
            ("Seneca", "Active", "warning", 78.3),
            ("Selargius Tank", "Active", "normal", 185.2),
            ("External Supply", "Maintenance", "alert", 0.0)
        ]
        
        for idx, (node, status, level, flow) in enumerate(nodes):
            with node_cols[idx % 4]:
                status_class = f"status-{level}"
                st.markdown(f"""
                <div class="metric-container">
                    <h4>{node}</h4>
                    <p class="{status_class}">{status}</p>
                    <p>Flow: {flow} L/s</p>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_anomaly_tab(self, time_range: str):
        """Render the anomaly detection tab."""
        st.header("Anomaly Detection")
        
        # Run anomaly detection
        if st.button("Run Anomaly Detection"):
            with st.spinner("Detecting anomalies..."):
                # This would call the actual use case
                st.success("Anomaly detection completed!")
        
        # Display recent anomalies
        st.subheader("Recent Anomalies")
        
        anomalies_data = pd.DataFrame({
            'Timestamp': pd.date_range(end=datetime.now(), periods=5, freq='H'),
            'Node': ['Sant\'Anna', 'Seneca', 'Sant\'Anna', 'Tank Output', 'Seneca'],
            'Type': ['High Flow', 'Low Pressure', 'Temperature', 'No Flow', 'High Pressure'],
            'Severity': ['Medium', 'High', 'Low', 'Critical', 'Medium'],
            'Value': ['156.2 L/s', '2.1 bar', '28.5°C', '0 L/s', '6.8 bar'],
            'Expected': ['80-120 L/s', '> 3.0 bar', '< 25°C', '> 150 L/s', '< 5.5 bar']
        })
        
        # Color code severity
        def severity_color(severity):
            colors = {
                'Low': 'background-color: #ffeaa7',
                'Medium': 'background-color: #fdcb6e',
                'High': 'background-color: #ff7675',
                'Critical': 'background-color: #d63031; color: white'
            }
            return colors.get(severity, '')
        
        styled_df = anomalies_data.style.applymap(
            severity_color,
            subset=['Severity']
        )
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Anomaly distribution chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                values=[3, 5, 2, 1],
                names=['Low', 'Medium', 'High', 'Critical'],
                title='Anomaly Distribution by Severity',
                color_discrete_map={
                    'Low': '#ffeaa7',
                    'Medium': '#fdcb6e',
                    'High': '#ff7675',
                    'Critical': '#d63031'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            anomaly_trend = pd.DataFrame({
                'Date': pd.date_range(end=datetime.now(), periods=7, freq='D'),
                'Count': [5, 8, 3, 12, 7, 4, 11]
            })
            
            fig_bar = px.bar(
                anomaly_trend,
                x='Date',
                y='Count',
                title='Daily Anomaly Trend',
                labels={'Count': 'Number of Anomalies'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    def _render_consumption_tab(self, time_range: str, selected_nodes: List[str]):
        """Render the consumption patterns tab."""
        st.header("Consumption Patterns Analysis")
        
        # Pattern type selection
        pattern_type = st.selectbox(
            "Analysis Type",
            ["Hourly", "Daily", "Weekly", "Monthly"],
            index=0
        )
        
        # Generate sample consumption pattern data
        if pattern_type == "Hourly":
            labels = [f"{i:02d}:00" for i in range(24)]
            values = [50 + 30 * abs(pd.np.sin(i/4)) for i in range(24)]
        elif pattern_type == "Daily":
            labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            values = [120, 115, 125, 130, 135, 90, 85]
        elif pattern_type == "Weekly":
            labels = [f"Week {i}" for i in range(1, 5)]
            values = [850, 870, 820, 890]
        else:  # Monthly
            labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            values = [3200, 3100, 3300, 3250, 3400, 3350]
        
        # Create pattern visualization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=labels,
                y=values,
                marker_color='lightblue',
                name='Average Consumption'
            ))
            
            # Add trend line
            fig.add_trace(go.Scatter(
                x=labels,
                y=values,
                mode='lines+markers',
                name='Trend',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title=f'{pattern_type} Consumption Pattern',
                xaxis_title='Period',
                yaxis_title='Consumption (m³)',
                showlegend=True,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Pattern Insights")
            
            # Peak and off-peak identification
            peak_idx = values.index(max(values))
            off_peak_idx = values.index(min(values))
            
            st.info(f"**Peak Period:** {labels[peak_idx]}")
            st.info(f"**Off-Peak Period:** {labels[off_peak_idx]}")
            st.info(f"**Variability:** {(max(values) - min(values)) / max(values) * 100:.1f}%")
            
            # Recommendations
            st.subheader("Recommendations")
            st.markdown("""
            - Consider pressure management during peak hours
            - Optimize pumping schedules for off-peak periods
            - Monitor for unusual consumption patterns
            """)
    
    def _render_efficiency_tab(self, time_range: str):
        """Render the network efficiency tab."""
        st.header("Network Efficiency Analysis")
        
        # Efficiency metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Current Efficiency",
                value="92.5%",
                delta="2.1% vs last period",
                help="Ratio of output to input flow"
            )
        
        with col2:
            st.metric(
                label="Water Loss",
                value="7.5%",
                delta="-2.1% improvement",
                help="Percentage of water lost in the network"
            )
        
        with col3:
            st.metric(
                label="Loss Volume (24h)",
                value="92.5 m³",
                delta="-12.3 m³",
                help="Absolute volume of water lost"
            )
        
        # Efficiency trend chart
        st.subheader("Efficiency Trend")
        
        efficiency_data = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=30, freq='D'),
            'Efficiency': 90 + 5 * pd.Series(range(30)).apply(lambda x: pd.np.sin(x/5)) + pd.Series(range(30)) * 0.1
        })
        
        fig = px.line(
            efficiency_data,
            x='Date',
            y='Efficiency',
            title='Network Efficiency Over Time (%)',
            labels={'Efficiency': 'Efficiency (%)'}
        )
        
        # Add threshold lines
        fig.add_hline(y=95, line_dash="dash", line_color="green", annotation_text="Target")
        fig.add_hline(y=90, line_dash="dash", line_color="orange", annotation_text="Minimum")
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Node contribution analysis
        st.subheader("Node Contribution to Network Loss")
        
        node_loss_data = pd.DataFrame({
            'Node': ['Sant\'Anna → Seneca', 'Tank → Sant\'Anna', 'External → Tank', 'Seneca → Distribution'],
            'Loss %': [2.1, 1.8, 3.2, 0.4]
        })
        
        fig_bar = px.bar(
            node_loss_data,
            x='Node',
            y='Loss %',
            title='Water Loss by Network Segment',
            color='Loss %',
            color_continuous_scale='Reds'
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Leakage detection zones
        st.subheader("Potential Leakage Zones")
        
        leakage_data = pd.DataFrame({
            'From Node': ['External Supply', 'Selargius Tank', 'Sant\'Anna'],
            'To Node': ['Selargius Tank', 'Sant\'Anna', 'Seneca'],
            'Loss %': [3.2, 1.8, 2.1],
            'Severity': ['High', 'Medium', 'Medium'],
            'Action': ['Immediate inspection', 'Schedule maintenance', 'Monitor closely']
        })
        
        st.dataframe(leakage_data, use_container_width=True)
    
    def _render_reports_tab(self):
        """Render the reports tab."""
        st.header("Reports & Analytics")
        
        # Report type selection
        report_type = st.selectbox(
            "Select Report Type",
            ["Daily Summary", "Weekly Analysis", "Monthly Report", "Custom Period"]
        )
        
        if report_type == "Custom Period":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
            with col2:
                end_date = st.date_input("End Date", datetime.now())
        
        # Generate report button
        if st.button("Generate Report", type="primary"):
            with st.spinner("Generating report..."):
                # Simulate report generation
                st.success("Report generated successfully!")
        
        # Sample report content
        st.subheader(f"{report_type} Report")
        
        # Executive summary
        with st.expander("Executive Summary", expanded=True):
            st.markdown("""
            ### Key Findings
            - **Network efficiency** improved by 2.1% compared to previous period
            - **Total consumption** increased by 5.3% due to seasonal factors
            - **3 critical anomalies** detected and resolved
            - **Maintenance** completed on 2 nodes
            
            ### Recommendations
            1. Focus on reducing water loss in External Supply → Tank segment
            2. Schedule preventive maintenance for Seneca node
            3. Implement real-time monitoring for high-risk zones
            """)
        
        # Detailed metrics
        with st.expander("Detailed Metrics"):
            metrics_df = pd.DataFrame({
                'Metric': ['Total Volume', 'Avg Flow Rate', 'Peak Flow', 'Min Pressure', 'Anomalies'],
                'Value': ['34,567 m³', '125.4 L/s', '189.2 L/s', '3.2 bar', '12'],
                'Change': ['+5.3%', '+2.1%', '+8.5%', '-0.3 bar', '-25%'],
                'Status': ['✅', '✅', '⚠️', '✅', '✅']
            })
            
            st.dataframe(metrics_df, use_container_width=True)
        
        # Export options
        st.subheader("Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📄 Download PDF Report",
                data=b"PDF report content",  # Would be actual PDF bytes
                file_name=f"water_infrastructure_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        
        with col2:
            st.download_button(
                label="📊 Download Excel Data",
                data=b"Excel data content",  # Would be actual Excel bytes
                file_name=f"water_infrastructure_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col3:
            st.download_button(
                label="📈 Download Charts",
                data=b"Charts content",  # Would be actual image/zip bytes
                file_name=f"water_infrastructure_charts_{datetime.now().strftime('%Y%m%d')}.zip",
                mime="application/zip"
            )


def main():
    """Main entry point for the dashboard."""
    # Initialize DI container
    container = Container()
    
    # Configure container
    container.config.bigquery.project_id.from_env("BIGQUERY_PROJECT_ID", default="abbanoa-464816")
    container.config.bigquery.dataset_id.from_env("BIGQUERY_DATASET_ID", default="water_infrastructure")
    container.config.bigquery.location.from_env("BIGQUERY_LOCATION", default="EU")
    
    container.config.anomaly_detection.z_score_threshold.from_env("ANOMALY_Z_SCORE", default=3.0)
    container.config.anomaly_detection.min_data_points.from_env("ANOMALY_MIN_POINTS", default=10)
    container.config.anomaly_detection.rolling_window_hours.from_env("ANOMALY_WINDOW_HOURS", default=24)
    
    # Wire the container
    container.wire(modules=[__name__])
    
    # Create and run dashboard
    dashboard = WaterInfrastructureDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()