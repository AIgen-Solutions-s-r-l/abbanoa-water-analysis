"""
Unified data adapter that handles both original and new sensor nodes.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from uuid import UUID
import pandas as pd
from google.cloud import bigquery
import streamlit as st


class UnifiedDataAdapter:
    """Adapter that queries data from both sensor systems."""
    
    def __init__(self, bigquery_client: Optional[bigquery.Client] = None):
        self.client = bigquery_client or bigquery.Client()
        self.project_id = "abbanoa-464816"
        self.dataset_id = "water_infrastructure"
    
    def get_node_data(
        self,
        node_ids: List[Union[str, UUID]],
        start_time: datetime,
        end_time: datetime,
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Get data for nodes regardless of their ID type."""
        
        if not metrics:
            metrics = ["flow_rate", "pressure", "temperature", "volume"]
        
        # Separate UUID and string node IDs
        uuid_nodes = []
        string_nodes = []
        
        for node_id in node_ids:
            if isinstance(node_id, UUID) or (isinstance(node_id, str) and node_id.startswith("00000000")):
                uuid_nodes.append(str(node_id))
            else:
                string_nodes.append(str(node_id))
        
        dfs = []
        
        # Query original nodes
        if uuid_nodes:
            query1 = f"""
            SELECT 
                timestamp,
                node_id,
                node_name,
                {", ".join(metrics)}
            FROM `{self.project_id}.{self.dataset_id}.v_sensor_readings_normalized`
            WHERE node_id IN ({", ".join([f"'{n}'" for n in uuid_nodes])})
                AND timestamp >= @start_time
                AND timestamp <= @end_time
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                    bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
                ]
            )
            
            try:
                df1 = self.client.query(query1, job_config=job_config).to_dataframe()
                if not df1.empty:
                    dfs.append(df1)
            except Exception as e:
                st.error(f"Error querying original nodes: {e}")
        
        # Query new nodes
        if string_nodes:
            query2 = f"""
            SELECT 
                timestamp,
                node_id,
                node_name,
                {", ".join(metrics)},
                data_quality_score
            FROM `{self.project_id}.{self.dataset_id}.sensor_readings_ml`
            WHERE node_id IN ({", ".join([f"'{n}'" for n in string_nodes])})
                AND timestamp >= @start_time
                AND timestamp <= @end_time
                AND data_quality_score > 0.5
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                    bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
                ]
            )
            
            try:
                df2 = self.client.query(query2, job_config=job_config).to_dataframe()
                if not df2.empty:
                    dfs.append(df2)
            except Exception as e:
                st.error(f"Error querying new nodes: {e}")
        
        # Combine results
        if dfs:
            return pd.concat(dfs, ignore_index=True).sort_values("timestamp")
        
        return pd.DataFrame()
    
    def count_active_nodes(self, time_range_hours: int = 24) -> int:
        """Count nodes with recent data."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # Query both tables
        query = f"""
        WITH all_nodes AS (
            SELECT DISTINCT node_id
            FROM `{self.project_id}.{self.dataset_id}.v_sensor_readings_normalized`
            WHERE timestamp >= @start_time
                AND timestamp <= @end_time
            
            UNION DISTINCT
            
            SELECT DISTINCT node_id
            FROM `{self.project_id}.{self.dataset_id}.sensor_readings_ml`
            WHERE timestamp >= @start_time
                AND timestamp <= @end_time
                AND data_quality_score > 0.5
        )
        SELECT COUNT(*) as active_nodes
        FROM all_nodes
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
            ]
        )
        
        try:
            result = self.client.query(query, job_config=job_config).to_dataframe()
            return int(result.iloc[0]["active_nodes"]) if not result.empty else 0
        except Exception as e:
            st.error(f"Error counting active nodes: {e}")
            return 0
