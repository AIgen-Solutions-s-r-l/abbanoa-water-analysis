"""
Enhanced data fetcher that supports both original and new sensor nodes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from google.cloud import bigquery
import streamlit as st

from src.presentation.streamlit.utils.node_mappings import (
    get_node_ids_from_selection,
    get_node_display_name
)


class EnhancedDataFetcher:
    """Enhanced data fetcher for all sensor nodes."""
    
    def __init__(self, bigquery_client: Optional[bigquery.Client] = None):
        """Initialize the data fetcher."""
        self.client = bigquery_client or bigquery.Client()
        self.project_id = "abbanoa-464816"
        self.dataset_id = "water_infrastructure"
        
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_sensor_data(
        self,
        selected_nodes: List[str],
        time_range: str = "Last 24 Hours",
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Fetch sensor data for selected nodes."""
        
        # Convert display names to node IDs
        node_ids = get_node_ids_from_selection(selected_nodes)
        
        if not node_ids:
            return pd.DataFrame()
        
        # Parse time range
        end_time = datetime.now()
        if time_range == "Last 6 Hours":
            start_time = end_time - timedelta(hours=6)
        elif time_range == "Last 24 Hours":
            start_time = end_time - timedelta(hours=24)
        elif time_range == "Last 3 Days":
            start_time = end_time - timedelta(days=3)
        elif time_range == "Last 7 Days":
            start_time = end_time - timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(hours=24)
        
        # Default metrics
        if not metrics:
            metrics = ["flow_rate", "pressure", "temperature", "volume"]
        
        # Build query for both tables
        queries = []
        
        # Query for original nodes (UUIDs)
        uuid_nodes = [nid for nid in node_ids if nid.startswith("00000000")]
        if uuid_nodes:
            uuid_list = ", ".join([f"'{nid}'" for nid in uuid_nodes])
            query1 = f"""
            SELECT 
                timestamp,
                node_id,
                node_name,
                {", ".join(metrics)}
            FROM `{self.project_id}.{self.dataset_id}.v_sensor_readings_normalized`
            WHERE node_id IN ({uuid_list})
                AND timestamp >= TIMESTAMP('{start_time.isoformat()}')
                AND timestamp <= TIMESTAMP('{end_time.isoformat()}')
            """
            queries.append(query1)
        
        # Query for new nodes (numeric IDs) from ML table
        numeric_nodes = [nid for nid in node_ids if nid.isdigit()]
        if numeric_nodes:
            node_list = ", ".join([f"'{nid}'" for nid in numeric_nodes])
            metric_cols = []
            for metric in metrics:
                if metric in ["flow_rate", "pressure", "temperature", "volume"]:
                    metric_cols.append(metric)
            
            query2 = f"""
            SELECT 
                timestamp,
                node_id,
                node_name,
                {", ".join(metric_cols)},
                data_quality_score
            FROM `{self.project_id}.{self.dataset_id}.sensor_readings_ml`
            WHERE node_id IN ({node_list})
                AND timestamp >= TIMESTAMP('{start_time.isoformat()}')
                AND timestamp <= TIMESTAMP('{end_time.isoformat()}')
                AND data_quality_score > 0.5
            """
            queries.append(query2)
        
        # Execute queries and combine results
        all_data = []
        for query in queries:
            try:
                df = self.client.query(query).to_dataframe()
                if not df.empty:
                    all_data.append(df)
            except Exception as e:
                st.error(f"Error fetching data: {e}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Add display names
            combined_df['display_name'] = combined_df['node_id'].apply(get_node_display_name)
            
            # Sort by timestamp
            combined_df = combined_df.sort_values('timestamp', ascending=False)
            
            return combined_df
        
        return pd.DataFrame()
    
    def get_latest_readings(self, selected_nodes: List[str]) -> Dict[str, Dict]:
        """Get latest readings for selected nodes."""
        df = self.fetch_sensor_data(selected_nodes, "Last 6 Hours")
        
        if df.empty:
            return {}
        
        # Get latest reading for each node
        latest_readings = {}
        for node_id in df['node_id'].unique():
            node_data = df[df['node_id'] == node_id].iloc[0]
            display_name = get_node_display_name(node_id)
            
            latest_readings[display_name] = {
                'timestamp': node_data['timestamp'],
                'flow_rate': node_data.get('flow_rate', 0),
                'pressure': node_data.get('pressure', 0),
                'temperature': node_data.get('temperature', 0),
                'volume': node_data.get('volume', 0),
                'quality_score': node_data.get('data_quality_score', 1.0)
            }
        
        return latest_readings
    
    def get_aggregated_metrics(self, selected_nodes: List[str], time_range: str) -> Dict[str, float]:
        """Get aggregated metrics for selected nodes."""
        df = self.fetch_sensor_data(selected_nodes, time_range)
        
        if df.empty:
            return {
                'total_flow': 0,
                'avg_pressure': 0,
                'avg_temperature': 0,
                'total_volume': 0,
                'active_nodes': 0
            }
        
        return {
            'total_flow': df['flow_rate'].sum() if 'flow_rate' in df else 0,
            'avg_pressure': df['pressure'].mean() if 'pressure' in df else 0,
            'avg_temperature': df['temperature'].mean() if 'temperature' in df else 0,
            'total_volume': df['volume'].sum() if 'volume' in df else 0,
            'active_nodes': df['node_id'].nunique()
        }