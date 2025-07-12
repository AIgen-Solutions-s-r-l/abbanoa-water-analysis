#!/usr/bin/env python3
"""
GCP Advanced Analytics Setup for Water Infrastructure Data
This script demonstrates how to use GCP tools for advanced analysis
"""

import pandas as pd
from google.cloud import bigquery
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta

# Configuration
PROJECT_ID = "abbanoa-464816"
DATASET_ID = "water_infrastructure"
TABLE_ID = "sensor_data"


def setup_bigquery_client():
    """Initialize BigQuery client"""
    client = bigquery.Client(project=PROJECT_ID)
    return client


def create_advanced_analysis_queries():
    """Advanced SQL queries for water infrastructure analysis"""

    queries = {
        "correlation_analysis": """
            -- Correlation analysis between different sensors
            WITH daily_metrics AS (
              SELECT 
                data,
                AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as avg_flow_sant_anna,
                AVG(selargius_nodo_via_seneca_portata_w_istantanea_diretta) as avg_flow_seneca,
                AVG(selargius_serbatoio_selargius_portata_uscita) as avg_flow_tank,
                AVG(quartucciu_serbatoio_cuccuru_linu_portata_selargius) as avg_flow_quartucciu,
                AVG(selargius_nodo_via_sant_anna_temperatura_interna) as avg_temp_sant_anna,
                AVG(selargius_nodo_via_seneca_temperatura_interna) as avg_temp_seneca
              FROM `{project}.{dataset}.{table}`
              WHERE data IS NOT NULL
              GROUP BY data
            )
            SELECT *
            FROM daily_metrics
            ORDER BY data
        """,
        "anomaly_detection": """
            -- Advanced anomaly detection using statistical methods
            WITH flow_stats AS (
              SELECT 
                AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as mean_flow,
                STDDEV(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as stddev_flow,
                APPROX_QUANTILES(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta, 100)[OFFSET(25)] as q25,
                APPROX_QUANTILES(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta, 100)[OFFSET(75)] as q75
              FROM `{project}.{dataset}.{table}`
              WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
            ),
            iqr_bounds AS (
              SELECT 
                *,
                q25 - 1.5 * (q75 - q25) as lower_bound,
                q75 + 1.5 * (q75 - q25) as upper_bound
              FROM flow_stats
            )
            SELECT 
              data,
              ora,
              selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow_rate,
              CASE 
                WHEN selargius_nodo_via_sant_anna_portata_w_istantanea_diretta < (SELECT lower_bound FROM iqr_bounds) 
                  OR selargius_nodo_via_sant_anna_portata_w_istantanea_diretta > (SELECT upper_bound FROM iqr_bounds)
                THEN 'ANOMALY'
                ELSE 'NORMAL'
              END as anomaly_status,
              ABS(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta - (SELECT mean_flow FROM flow_stats)) / 
                (SELECT stddev_flow FROM flow_stats) as z_score
            FROM `{project}.{dataset}.{table}`, flow_stats
            WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
            ORDER BY z_score DESC
            LIMIT 50
        """,
        "hourly_patterns": """
            -- Hourly consumption patterns analysis
            SELECT 
              EXTRACT(HOUR FROM PARSE_TIME('%H:%M:%S', ora)) as hour_of_day,
              EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data)) as day_of_week,
              AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as avg_flow_rate,
              STDDEV(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as stddev_flow_rate,
              MIN(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as min_flow_rate,
              MAX(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta) as max_flow_rate,
              COUNT(*) as measurements
            FROM `{project}.{dataset}.{table}`
            WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
              AND ora IS NOT NULL
              AND data IS NOT NULL
            GROUP BY hour_of_day, day_of_week
            ORDER BY day_of_week, hour_of_day
        """,
        "efficiency_metrics": """
            -- Network efficiency and loss analysis
            WITH flow_comparison AS (
              SELECT 
                data,
                ora,
                selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as input_flow_1,
                selargius_nodo_via_seneca_portata_w_istantanea_diretta as input_flow_2,
                selargius_serbatoio_selargius_portata_uscita as output_flow,
                quartucciu_serbatoio_cuccuru_linu_portata_selargius as external_supply
              FROM `{project}.{dataset}.{table}`
              WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
                AND selargius_serbatoio_selargius_portata_uscita IS NOT NULL
            )
            SELECT 
              data,
              AVG(input_flow_1 + COALESCE(input_flow_2, 0) + COALESCE(external_supply, 0)) as total_input,
              AVG(output_flow) as total_output,
              AVG(input_flow_1 + COALESCE(input_flow_2, 0) + COALESCE(external_supply, 0) - output_flow) as apparent_loss,
              SAFE_DIVIDE(
                AVG(input_flow_1 + COALESCE(input_flow_2, 0) + COALESCE(external_supply, 0) - output_flow),
                AVG(input_flow_1 + COALESCE(input_flow_2, 0) + COALESCE(external_supply, 0))
              ) * 100 as loss_percentage
            FROM flow_comparison
            GROUP BY data
            ORDER BY data
        """,
    }

    return {
        k: v.format(project=PROJECT_ID, dataset=DATASET_ID, table=TABLE_ID)
        for k, v in queries.items()
    }


def create_bigquery_ml_models():
    """Create ML models using BigQuery ML for predictive analytics"""

    ml_queries = {
        "time_series_forecasting": """
            -- Create time series forecasting model for flow prediction
            CREATE OR REPLACE MODEL `{project}.{dataset}.flow_forecasting_model`
            OPTIONS(
              model_type='ARIMA_PLUS',
              time_series_timestamp_col='datetime',
              time_series_data_col='flow_rate',
              time_series_id_col='sensor_id'
            ) AS
            SELECT
              DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora)) as datetime,
              'sant_anna' as sensor_id,
              selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow_rate
            FROM `{project}.{dataset}.{table}`
            WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
              AND data IS NOT NULL 
              AND ora IS NOT NULL
        """,
        "clustering_analysis": """
            -- Create clustering model to identify operational patterns
            CREATE OR REPLACE MODEL `{project}.{dataset}.operational_patterns_model`
            OPTIONS(
              model_type='KMEANS',
              num_clusters=5
            ) AS
            SELECT
              EXTRACT(HOUR FROM PARSE_TIME('%H:%M:%S', ora)) as hour_of_day,
              EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data)) as day_of_week,
              selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow_rate_1,
              COALESCE(selargius_nodo_via_seneca_portata_w_istantanea_diretta, 0) as flow_rate_2,
              selargius_serbatoio_selargius_portata_uscita as output_flow,
              COALESCE(quartucciu_serbatoio_cuccuru_linu_portata_selargius, 0) as external_supply
            FROM `{project}.{dataset}.{table}`
            WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
              AND selargius_serbatoio_selargius_portata_uscita IS NOT NULL
              AND data IS NOT NULL 
              AND ora IS NOT NULL
        """,
        "anomaly_detection_ml": """
            -- Create autoencoder for anomaly detection
            CREATE OR REPLACE MODEL `{project}.{dataset}.anomaly_detection_model`
            OPTIONS(
              model_type='AUTOENCODER',
              activation_fn='RELU',
              batch_size=32,
              dropout=0.2,
              hidden_units=[64, 32, 16, 32, 64],
              learn_rate=0.001,
              max_iterations=100
            ) AS
            SELECT
              selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as flow_1,
              COALESCE(selargius_nodo_via_seneca_portata_w_istantanea_diretta, 0) as flow_2,
              selargius_serbatoio_selargius_portata_uscita as output_flow,
              COALESCE(selargius_nodo_via_sant_anna_temperatura_interna, 20) as temp_1,
              COALESCE(selargius_nodo_via_seneca_temperatura_interna, 20) as temp_2,
              EXTRACT(HOUR FROM PARSE_TIME('%H:%M:%S', ora)) as hour_feature,
              EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data)) as day_feature
            FROM `{project}.{dataset}.{table}`
            WHERE selargius_nodo_via_sant_anna_portata_w_istantanea_diretta IS NOT NULL
              AND selargius_serbatoio_selargius_portata_uscita IS NOT NULL
        """,
    }

    return {
        k: v.format(project=PROJECT_ID, dataset=DATASET_ID, table=TABLE_ID)
        for k, v in ml_queries.items()
    }


def create_real_time_monitoring_setup():
    """Setup for real-time monitoring and alerting"""

    monitoring_queries = {
        "create_alerts_table": """
            -- Create table for storing alerts and notifications
            CREATE OR REPLACE TABLE `{project}.{dataset}.water_alerts` (
              alert_id STRING,
              timestamp TIMESTAMP,
              alert_type STRING,
              severity STRING,
              sensor_location STRING,
              current_value FLOAT64,
              threshold_value FLOAT64,
              message STRING,
              resolved BOOLEAN DEFAULT FALSE
            )
        """,
        "real_time_monitoring_view": """
            -- Create view for real-time monitoring dashboard
            CREATE OR REPLACE VIEW `{project}.{dataset}.real_time_dashboard` AS
            WITH latest_readings AS (
              SELECT 
                *,
                ROW_NUMBER() OVER (PARTITION BY _source_file ORDER BY _ingestion_timestamp DESC) as rn
              FROM `{project}.{dataset}.{table}`
            ),
            current_status AS (
              SELECT 
                'Sant Anna Flow' as metric_name,
                selargius_nodo_via_sant_anna_portata_w_istantanea_diretta as current_value,
                100.0 as threshold_high,
                20.0 as threshold_low,
                'L/S' as unit,
                CASE 
                  WHEN selargius_nodo_via_sant_anna_portata_w_istantanea_diretta > 100 THEN 'HIGH'
                  WHEN selargius_nodo_via_sant_anna_portata_w_istantanea_diretta < 20 THEN 'LOW'
                  ELSE 'NORMAL'
                END as status
              FROM latest_readings WHERE rn = 1
              
              UNION ALL
              
              SELECT 
                'Tank Output' as metric_name,
                selargius_serbatoio_selargius_portata_uscita as current_value,
                80.0 as threshold_high,
                10.0 as threshold_low,
                'L/S' as unit,
                CASE 
                  WHEN selargius_serbatoio_selargius_portata_uscita > 80 THEN 'HIGH'
                  WHEN selargius_serbatoio_selargius_portata_uscita < 10 THEN 'LOW'
                  ELSE 'NORMAL'
                END as status
              FROM latest_readings WHERE rn = 1
            )
            SELECT * FROM current_status
        """,
    }

    return {
        k: v.format(project=PROJECT_ID, dataset=DATASET_ID, table=TABLE_ID)
        for k, v in monitoring_queries.items()
    }


def generate_looker_studio_config():
    """Generate configuration for Looker Studio dashboard"""

    dashboard_config = {
        "data_source": {
            "type": "BigQuery",
            "project_id": PROJECT_ID,
            "dataset_id": DATASET_ID,
            "table_id": TABLE_ID,
        },
        "recommended_charts": [
            {
                "name": "Flow Rate Time Series",
                "type": "Time Series Chart",
                "x_axis": "DATETIME(PARSE_DATE('%d/%m/%Y', data), PARSE_TIME('%H:%M:%S', ora))",
                "y_axis": "selargius_nodo_via_sant_anna_portata_w_istantanea_diretta",
                "description": "Shows flow rate trends over time",
            },
            {
                "name": "Hourly Consumption Heatmap",
                "type": "Heatmap",
                "x_axis": "EXTRACT(HOUR FROM PARSE_TIME('%H:%M:%S', ora))",
                "y_axis": "EXTRACT(DAYOFWEEK FROM PARSE_DATE('%d/%m/%Y', data))",
                "metric": "AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta)",
                "description": "Shows consumption patterns by hour and day",
            },
            {
                "name": "Network Flow Balance",
                "type": "Combo Chart",
                "metrics": [
                    "selargius_nodo_via_sant_anna_portata_w_istantanea_diretta",
                    "selargius_serbatoio_selargius_portata_uscita",
                    "quartucciu_serbatoio_cuccuru_linu_portata_selargius",
                ],
                "description": "Compares input vs output flows",
            },
            {
                "name": "Efficiency KPIs",
                "type": "Scorecard",
                "metrics": [
                    "AVG(selargius_nodo_via_sant_anna_portata_w_istantanea_diretta)",
                    "SUM(selargius_nodo_via_sant_anna_portata_w_totale_diretta)",
                    "COUNT(*) as total_measurements",
                ],
                "description": "Key performance indicators",
            },
        ],
        "filters": [
            "Date range filter on data field",
            "Time filter on ora field",
            "Sensor location dropdown",
        ],
    }

    return dashboard_config


if __name__ == "__main__":
    print("🚀 GCP Advanced Analytics Setup for Water Infrastructure")
    print("=" * 60)

    # Create analysis queries
    analysis_queries = create_advanced_analysis_queries()
    ml_queries = create_bigquery_ml_models()
    monitoring_queries = create_real_time_monitoring_setup()
    dashboard_config = generate_looker_studio_config()

    print("✅ Advanced Analysis Queries Generated")
    print("✅ BigQuery ML Models Defined")
    print("✅ Real-time Monitoring Setup Created")
    print("✅ Looker Studio Configuration Ready")

    print("\n📊 Next Steps:")
    print("1. Run BigQuery ML models for predictive analytics")
    print("2. Set up Looker Studio dashboard")
    print("3. Configure Vertex AI Workbench for advanced analysis")
    print("4. Implement real-time monitoring and alerting")
