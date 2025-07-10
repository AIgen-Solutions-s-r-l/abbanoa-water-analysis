"""
Performance monitoring utility for Streamlit dashboard.

This module provides tools to measure and analyze loading times for different
tabs and time range combinations to identify performance bottlenecks.
"""

import time
import functools
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class PerformanceMonitor:
    """Performance monitoring utility for dashboard components."""
    
    def __init__(self):
        """Initialize the performance monitor."""
        if 'performance_data' not in st.session_state:
            st.session_state.performance_data = []
    
    def measure_time(self, component_name: str, time_range: str = None):
        """Decorator to measure execution time of functions."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error_msg = None
                except Exception as e:
                    result = None
                    success = False
                    error_msg = str(e)
                    raise
                finally:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    # Record performance data
                    self._record_performance(
                        component_name=component_name,
                        time_range=time_range or kwargs.get('time_range', 'Unknown'),
                        execution_time=execution_time,
                        success=success,
                        error_msg=error_msg,
                        timestamp=datetime.now()
                    )
                
                return result
            return wrapper
        return decorator
    
    def _record_performance(self, component_name: str, time_range: str, 
                          execution_time: float, success: bool, 
                          error_msg: Optional[str], timestamp: datetime):
        """Record performance data to session state."""
        performance_record = {
            'component': component_name,
            'time_range': time_range,
            'execution_time': execution_time,
            'success': success,
            'error_msg': error_msg,
            'timestamp': timestamp,
            'formatted_time': f"{execution_time:.2f}s"
        }
        
        st.session_state.performance_data.append(performance_record)
        
        # Keep only last 100 records to avoid memory issues
        if len(st.session_state.performance_data) > 100:
            st.session_state.performance_data = st.session_state.performance_data[-100:]
    
    def get_performance_data(self) -> List[Dict[str, Any]]:
        """Get all recorded performance data."""
        return st.session_state.performance_data
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not st.session_state.performance_data:
            return {}
        
        df = pd.DataFrame(st.session_state.performance_data)
        
        summary = {
            'total_measurements': len(df),
            'avg_execution_time': df['execution_time'].mean(),
            'max_execution_time': df['execution_time'].max(),
            'min_execution_time': df['execution_time'].min(),
            'success_rate': (df['success'].sum() / len(df)) * 100,
            'by_component': df.groupby('component')['execution_time'].agg(['mean', 'max', 'count']).to_dict(),
            'by_time_range': df.groupby('time_range')['execution_time'].agg(['mean', 'max', 'count']).to_dict(),
            'slowest_operations': df.nlargest(5, 'execution_time')[['component', 'time_range', 'execution_time', 'timestamp']].to_dict('records')
        }
        
        return summary
    
    def render_performance_dashboard(self):
        """Render a performance monitoring dashboard."""
        st.header("🔍 Performance Monitor")
        
        if not st.session_state.performance_data:
            st.info("No performance data collected yet. Navigate through different tabs and time ranges to collect data.")
            return
        
        df = pd.DataFrame(st.session_state.performance_data)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_time = df['execution_time'].mean()
            st.metric("Avg Load Time", f"{avg_time:.2f}s")
        
        with col2:
            max_time = df['execution_time'].max()
            st.metric("Max Load Time", f"{max_time:.2f}s")
        
        with col3:
            success_rate = (df['success'].sum() / len(df)) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col4:
            total_measurements = len(df)
            st.metric("Total Measurements", total_measurements)
        
        # Performance by component
        st.subheader("Performance by Component")
        component_stats = df.groupby('component')['execution_time'].agg(['mean', 'max', 'count']).reset_index()
        component_stats.columns = ['Component', 'Avg Time (s)', 'Max Time (s)', 'Count']
        component_stats['Avg Time (s)'] = component_stats['Avg Time (s)'].round(2)
        component_stats['Max Time (s)'] = component_stats['Max Time (s)'].round(2)
        
        fig_component = px.bar(
            component_stats, 
            x='Component', 
            y='Avg Time (s)',
            title="Average Loading Time by Component",
            color='Avg Time (s)',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_component, use_container_width=True)
        
        # Performance by time range
        st.subheader("Performance by Time Range")
        time_range_stats = df.groupby('time_range')['execution_time'].agg(['mean', 'max', 'count']).reset_index()
        time_range_stats.columns = ['Time Range', 'Avg Time (s)', 'Max Time (s)', 'Count']
        time_range_stats['Avg Time (s)'] = time_range_stats['Avg Time (s)'].round(2)
        time_range_stats['Max Time (s)'] = time_range_stats['Max Time (s)'].round(2)
        
        fig_time_range = px.bar(
            time_range_stats, 
            x='Time Range', 
            y='Avg Time (s)',
            title="Average Loading Time by Time Range",
            color='Avg Time (s)',
            color_continuous_scale='Reds'
        )
        fig_time_range.update_xaxes(tickangle=45)
        st.plotly_chart(fig_time_range, use_container_width=True)
        
        # Performance heatmap
        st.subheader("Performance Heatmap (Component vs Time Range)")
        pivot_data = df.pivot_table(
            values='execution_time', 
            index='component', 
            columns='time_range', 
            aggfunc='mean'
        ).fillna(0)
        
        if not pivot_data.empty:
            fig_heatmap = px.imshow(
                pivot_data,
                title="Average Loading Time Heatmap",
                color_continuous_scale='Reds',
                aspect='auto'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Timeline of performance
        st.subheader("Performance Timeline")
        df_recent = df.tail(50)  # Show last 50 measurements
        
        fig_timeline = px.scatter(
            df_recent,
            x='timestamp',
            y='execution_time',
            color='component',
            size='execution_time',
            title="Recent Performance Timeline",
            hover_data=['time_range', 'success']
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Slowest operations table
        st.subheader("Slowest Operations")
        slowest = df.nlargest(10, 'execution_time')[['component', 'time_range', 'execution_time', 'timestamp', 'success']]
        slowest['execution_time'] = slowest['execution_time'].round(2)
        slowest['timestamp'] = slowest['timestamp'].dt.strftime('%H:%M:%S')
        st.dataframe(slowest, use_container_width=True)
        
        # Performance recommendations
        st.subheader("🚀 Performance Recommendations")
        self._show_recommendations(df)
        
        # Clear data button
        if st.button("Clear Performance Data"):
            st.session_state.performance_data = []
            st.rerun()
    
    def _show_recommendations(self, df: pd.DataFrame):
        """Show performance recommendations based on collected data."""
        recommendations = []
        
        # Check for slow time ranges
        time_range_avg = df.groupby('time_range')['execution_time'].mean()
        slow_ranges = time_range_avg[time_range_avg > 10].index.tolist()
        
        if slow_ranges:
            recommendations.append(
                f"⚠️ **Slow Time Ranges**: {', '.join(slow_ranges)} are taking >10s to load. "
                f"Consider implementing data pagination or sampling for large datasets."
            )
        
        # Check for slow components
        component_avg = df.groupby('component')['execution_time'].mean()
        slow_components = component_avg[component_avg > 5].index.tolist()
        
        if slow_components:
            recommendations.append(
                f"⚠️ **Slow Components**: {', '.join(slow_components)} are taking >5s to load. "
                f"Consider optimizing queries or adding more aggressive caching."
            )
        
        # Check for failures
        failure_rate = (1 - df['success'].mean()) * 100
        if failure_rate > 10:
            recommendations.append(
                f"❌ **High Failure Rate**: {failure_rate:.1f}% of operations are failing. "
                f"Check error logs and improve error handling."
            )
        
        # Check for cache effectiveness
        if len(df) > 20:
            recent_times = df.tail(10)['execution_time'].mean()
            older_times = df.head(10)['execution_time'].mean()
            
            if recent_times > older_times * 0.8:  # If recent times aren't much faster
                recommendations.append(
                    "📈 **Cache Effectiveness**: Recent operations aren't significantly faster. "
                    "Cache might not be working effectively or data is changing frequently."
                )
        
        if not recommendations:
            st.success("✅ **Good Performance**: No major performance issues detected!")
        else:
            for rec in recommendations:
                st.warning(rec)


# Global performance monitor instance
performance_monitor = PerformanceMonitor() 