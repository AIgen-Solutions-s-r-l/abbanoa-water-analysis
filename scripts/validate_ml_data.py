#!/usr/bin/env python3
"""
Validate ML-ready data in BigQuery and generate quality report.

This script checks data completeness, quality, and readiness for ML/AI algorithms.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from google.cloud import bigquery
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration
PROJECT_ID = os.environ.get("BIGQUERY_PROJECT_ID", "abbanoa-464816")
DATASET_ID = os.environ.get("BIGQUERY_DATASET_ID", "water_infrastructure")
OUTPUT_DIR = project_root / "reports" / "ml_data_validation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class MLDataValidator:
    """Validate ML-ready data in BigQuery."""

    def __init__(self, client: bigquery.Client):
        self.client = client
        self.validation_results = {}

    def run_all_validations(self) -> Dict:
        """Run all validation checks."""
        print("Running ML data validation checks...")

        # 1. Check data availability
        self.validate_data_availability()

        # 2. Check data completeness
        self.validate_data_completeness()

        # 3. Check data quality
        self.validate_data_quality()

        # 4. Check temporal coverage
        self.validate_temporal_coverage()

        # 5. Check feature distributions
        self.validate_feature_distributions()

        # 6. Check for anomalies
        self.validate_anomaly_detection()

        # 7. Generate ML readiness score
        self.calculate_ml_readiness_score()

        return self.validation_results

    def validate_data_availability(self):
        """Check if ML tables and views exist."""
        print("\n1. Checking data availability...")

        tables_to_check = [
            "sensor_readings_ml",
            "v_sensor_readings_normalized",
            "v_daily_metrics_ml",
        ]

        results = {}
        for table_name in tables_to_check:
            query = f"""
            SELECT COUNT(*) as row_count
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            """

            try:
                result = self.client.query(query).result()
                row_count = list(result)[0].row_count
                results[table_name] = {
                    "exists": True,
                    "row_count": row_count,
                    "status": "OK" if row_count > 0 else "EMPTY",
                }
                print(f"  ✓ {table_name}: {row_count:,} rows")
            except Exception as e:
                results[table_name] = {
                    "exists": False,
                    "row_count": 0,
                    "status": "NOT_FOUND",
                    "error": str(e),
                }
                print(f"  ✗ {table_name}: NOT FOUND")

        self.validation_results["data_availability"] = results

    def validate_data_completeness(self):
        """Check data completeness by node and metric."""
        print("\n2. Checking data completeness...")

        query = f"""
        WITH completeness AS (
            SELECT
                node_id,
                district_id,
                COUNT(*) as total_readings,
                COUNT(flow_rate) as flow_rate_count,
                COUNT(pressure) as pressure_count,
                COUNT(temperature) as temperature_count,
                COUNT(volume) as volume_count,
                MIN(timestamp) as earliest_reading,
                MAX(timestamp) as latest_reading,
                DATE_DIFF(MAX(DATE(timestamp)), MIN(DATE(timestamp)), DAY) + 1 as days_span,
                COUNT(DISTINCT DATE(timestamp)) as days_with_data
            FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
            GROUP BY node_id, district_id
        )
        SELECT
            *,
            ROUND(flow_rate_count / total_readings * 100, 2) as flow_rate_completeness,
            ROUND(pressure_count / total_readings * 100, 2) as pressure_completeness,
            ROUND(temperature_count / total_readings * 100, 2) as temperature_completeness,
            ROUND(volume_count / total_readings * 100, 2) as volume_completeness,
            ROUND(days_with_data / days_span * 100, 2) as temporal_completeness
        FROM completeness
        ORDER BY node_id
        """

        df = self.client.query(query).to_dataframe()

        # Summary statistics
        summary = {
            "total_nodes": len(df),
            "avg_completeness": {
                "flow_rate": df["flow_rate_completeness"].mean(),
                "pressure": df["pressure_completeness"].mean(),
                "temperature": df["temperature_completeness"].mean(),
                "volume": df["volume_completeness"].mean(),
                "temporal": df["temporal_completeness"].mean(),
            },
            "nodes_with_gaps": len(df[df["temporal_completeness"] < 90]),
            "detailed_by_node": df.to_dict("records"),
        }

        self.validation_results["data_completeness"] = summary

        print(f"  Total nodes: {summary['total_nodes']}")
        print(f"  Average completeness:")
        for metric, pct in summary["avg_completeness"].items():
            print(f"    - {metric}: {pct:.1f}%")

    def validate_data_quality(self):
        """Check data quality scores and anomalies."""
        print("\n3. Checking data quality...")

        query = f"""
        SELECT
            district_id,
            AVG(data_quality_score) as avg_quality_score,
            MIN(data_quality_score) as min_quality_score,
            MAX(data_quality_score) as max_quality_score,
            COUNTIF(data_quality_score < 0.5) as low_quality_count,
            COUNTIF(data_quality_score >= 0.8) as high_quality_count,
            COUNT(*) as total_count
        FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
        GROUP BY district_id
        """

        df = self.client.query(query).to_dataframe()

        quality_summary = {
            "overall_avg_quality": df["avg_quality_score"].mean(),
            "low_quality_percentage": (
                df["low_quality_count"].sum() / df["total_count"].sum() * 100
            ),
            "high_quality_percentage": (
                df["high_quality_count"].sum() / df["total_count"].sum() * 100
            ),
            "by_district": df.to_dict("records"),
        }

        self.validation_results["data_quality"] = quality_summary

        print(
            f"  Overall average quality score: {quality_summary['overall_avg_quality']:.3f}"
        )
        print(
            f"  High quality readings: {quality_summary['high_quality_percentage']:.1f}%"
        )
        print(
            f"  Low quality readings: {quality_summary['low_quality_percentage']:.1f}%"
        )

    def validate_temporal_coverage(self):
        """Check temporal coverage and gaps."""
        print("\n4. Checking temporal coverage...")

        query = f"""
        WITH daily_counts AS (
            SELECT
                DATE(timestamp) as date,
                district_id,
                COUNT(DISTINCT node_id) as nodes_reporting,
                COUNT(*) as reading_count
            FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
            GROUP BY date, district_id
        ),
        expected_nodes AS (
            SELECT
                district_id,
                COUNT(DISTINCT node_id) as expected_nodes
            FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
            GROUP BY district_id
        )
        SELECT
            dc.date,
            dc.district_id,
            dc.nodes_reporting,
            en.expected_nodes,
            dc.reading_count,
            ROUND(dc.nodes_reporting / en.expected_nodes * 100, 2) as coverage_percentage
        FROM daily_counts dc
        JOIN expected_nodes en ON dc.district_id = en.district_id
        WHERE dc.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        ORDER BY dc.date DESC, dc.district_id
        """

        df = self.client.query(query).to_dataframe()

        # Identify gaps
        gaps = df[df["coverage_percentage"] < 80]

        temporal_summary = {
            "date_range": {
                "start": df["date"].min().isoformat() if not df.empty else None,
                "end": df["date"].max().isoformat() if not df.empty else None,
            },
            "avg_daily_coverage": df["coverage_percentage"].mean(),
            "days_with_gaps": len(gaps),
            "gap_dates": gaps[["date", "district_id", "coverage_percentage"]].to_dict(
                "records"
            )[
                :10
            ],  # First 10
        }

        self.validation_results["temporal_coverage"] = temporal_summary

        print(
            f"  Date range: {temporal_summary['date_range']['start']} to {temporal_summary['date_range']['end']}"
        )
        print(
            f"  Average daily coverage: {temporal_summary['avg_daily_coverage']:.1f}%"
        )
        print(f"  Days with gaps: {temporal_summary['days_with_gaps']}")

    def validate_feature_distributions(self):
        """Analyze feature distributions for ML suitability."""
        print("\n5. Checking feature distributions...")

        query = f"""
        SELECT
            flow_rate,
            pressure,
            temperature,
            volume,
            data_quality_score
        FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        LIMIT 10000
        """

        df = self.client.query(query).to_dataframe()

        # Calculate distribution statistics
        features = ["flow_rate", "pressure", "temperature", "volume"]
        distribution_stats = {}

        for feature in features:
            if feature in df.columns:
                clean_data = df[feature].dropna()
                if len(clean_data) > 0:
                    distribution_stats[feature] = {
                        "mean": clean_data.mean(),
                        "std": clean_data.std(),
                        "min": clean_data.min(),
                        "max": clean_data.max(),
                        "q25": clean_data.quantile(0.25),
                        "q50": clean_data.quantile(0.50),
                        "q75": clean_data.quantile(0.75),
                        "skewness": clean_data.skew(),
                        "kurtosis": clean_data.kurtosis(),
                        "null_percentage": (df[feature].isna().sum() / len(df) * 100),
                    }

        self.validation_results["feature_distributions"] = distribution_stats

        # Generate distribution plots
        self._plot_distributions(df, features)

        print("  Feature statistics:")
        for feature, stats in distribution_stats.items():
            print(f"    {feature}:")
            print(f"      - Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
            print(f"      - Mean ± Std: {stats['mean']:.2f} ± {stats['std']:.2f}")
            print(f"      - Null %: {stats['null_percentage']:.1f}%")

    def validate_anomaly_detection(self):
        """Check for anomalies in the data."""
        print("\n6. Checking for anomalies...")

        query = f"""
        WITH stats AS (
            SELECT
                node_id,
                AVG(flow_rate) as mean_flow,
                STDDEV(flow_rate) as std_flow,
                AVG(pressure) as mean_pressure,
                STDDEV(pressure) as std_pressure
            FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
            GROUP BY node_id
        ),
        anomalies AS (
            SELECT
                s.timestamp,
                s.node_id,
                s.flow_rate,
                s.pressure,
                st.mean_flow,
                st.std_flow,
                st.mean_pressure,
                st.std_pressure,
                ABS(s.flow_rate - st.mean_flow) / NULLIF(st.std_flow, 0) as flow_z_score,
                ABS(s.pressure - st.mean_pressure) / NULLIF(st.std_pressure, 0) as pressure_z_score
            FROM `{PROJECT_ID}.{DATASET_ID}.sensor_readings_ml` s
            JOIN stats st ON s.node_id = st.node_id
            WHERE s.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        )
        SELECT
            COUNT(*) as total_readings,
            COUNTIF(flow_z_score > 3) as flow_anomalies,
            COUNTIF(pressure_z_score > 3) as pressure_anomalies,
            COUNTIF(flow_z_score > 3 OR pressure_z_score > 3) as total_anomalies
        FROM anomalies
        """

        result = list(self.client.query(query).result())[0]

        anomaly_summary = {
            "total_readings": result.total_readings,
            "flow_anomalies": result.flow_anomalies,
            "pressure_anomalies": result.pressure_anomalies,
            "total_anomalies": result.total_anomalies,
            "anomaly_percentage": (
                (result.total_anomalies / result.total_readings * 100)
                if result.total_readings > 0
                else 0
            ),
        }

        self.validation_results["anomaly_detection"] = anomaly_summary

        print(f"  Total recent readings: {anomaly_summary['total_readings']:,}")
        print(
            f"  Anomalies detected: {anomaly_summary['total_anomalies']:,} ({anomaly_summary['anomaly_percentage']:.2f}%)"
        )

    def calculate_ml_readiness_score(self):
        """Calculate overall ML readiness score."""
        print("\n7. Calculating ML readiness score...")

        score_components = {
            "data_availability": 0,
            "completeness": 0,
            "quality": 0,
            "temporal_coverage": 0,
            "anomaly_rate": 0,
        }

        # Data availability score
        if "data_availability" in self.validation_results:
            available_tables = sum(
                1
                for t in self.validation_results["data_availability"].values()
                if t["exists"]
            )
            score_components["data_availability"] = (available_tables / 3) * 100

        # Completeness score
        if "data_completeness" in self.validation_results:
            avg_completeness = np.mean(
                list(
                    self.validation_results["data_completeness"][
                        "avg_completeness"
                    ].values()
                )
            )
            score_components["completeness"] = avg_completeness

        # Quality score
        if "data_quality" in self.validation_results:
            score_components["quality"] = (
                self.validation_results["data_quality"]["overall_avg_quality"] * 100
            )

        # Temporal coverage score
        if "temporal_coverage" in self.validation_results:
            score_components["temporal_coverage"] = self.validation_results[
                "temporal_coverage"
            ]["avg_daily_coverage"]

        # Anomaly rate score (inverse - lower is better)
        if "anomaly_detection" in self.validation_results:
            anomaly_pct = self.validation_results["anomaly_detection"][
                "anomaly_percentage"
            ]
            score_components["anomaly_rate"] = max(
                0, 100 - (anomaly_pct * 10)
            )  # Penalize high anomaly rates

        # Calculate weighted overall score
        weights = {
            "data_availability": 0.2,
            "completeness": 0.25,
            "quality": 0.25,
            "temporal_coverage": 0.2,
            "anomaly_rate": 0.1,
        }

        overall_score = sum(score_components[k] * weights[k] for k in weights)

        ml_readiness = {
            "overall_score": overall_score,
            "component_scores": score_components,
            "recommendation": self._get_ml_recommendation(overall_score),
            "improvement_areas": [k for k, v in score_components.items() if v < 70],
        }

        self.validation_results["ml_readiness"] = ml_readiness

        print(f"\n  Overall ML Readiness Score: {overall_score:.1f}/100")
        print(f"  Recommendation: {ml_readiness['recommendation']}")
        if ml_readiness["improvement_areas"]:
            print(
                f"  Areas for improvement: {', '.join(ml_readiness['improvement_areas'])}"
            )

    def _get_ml_recommendation(self, score: float) -> str:
        """Get ML recommendation based on score."""
        if score >= 85:
            return "Excellent - Data is highly suitable for ML/AI processing"
        elif score >= 70:
            return "Good - Data is suitable for ML/AI with minor improvements"
        elif score >= 55:
            return "Fair - Data needs improvement before ML/AI processing"
        else:
            return "Poor - Significant data quality issues need to be addressed"

    def _plot_distributions(self, df: pd.DataFrame, features: List[str]):
        """Generate distribution plots for features."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()

        for i, feature in enumerate(features):
            if feature in df.columns and i < len(axes):
                data = df[feature].dropna()
                if len(data) > 0:
                    axes[i].hist(
                        data, bins=50, alpha=0.7, color="blue", edgecolor="black"
                    )
                    axes[i].set_title(f"{feature.title()} Distribution")
                    axes[i].set_xlabel(feature)
                    axes[i].set_ylabel("Frequency")

                    # Add statistics
                    axes[i].axvline(
                        data.mean(),
                        color="red",
                        linestyle="--",
                        linewidth=2,
                        label=f"Mean: {data.mean():.2f}",
                    )
                    axes[i].axvline(
                        data.median(),
                        color="green",
                        linestyle="--",
                        linewidth=2,
                        label=f"Median: {data.median():.2f}",
                    )
                    axes[i].legend()

        plt.tight_layout()
        plt.savefig(
            OUTPUT_DIR / "feature_distributions.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

    def generate_report(self):
        """Generate validation report."""
        report_path = (
            OUTPUT_DIR
            / f'ml_data_validation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )

        with open(report_path, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("ML DATA VALIDATION REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Overall ML Readiness
            if "ml_readiness" in self.validation_results:
                ml = self.validation_results["ml_readiness"]
                f.write("OVERALL ML READINESS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Score: {ml['overall_score']:.1f}/100\n")
                f.write(f"Recommendation: {ml['recommendation']}\n")
                f.write("\nComponent Scores:\n")
                for component, score in ml["component_scores"].items():
                    f.write(f"  - {component}: {score:.1f}\n")
                f.write("\n")

            # Data Availability
            if "data_availability" in self.validation_results:
                f.write("DATA AVAILABILITY\n")
                f.write("-" * 40 + "\n")
                for table, info in self.validation_results["data_availability"].items():
                    f.write(f"{table}: {info['status']} ({info['row_count']:,} rows)\n")
                f.write("\n")

            # Data Quality Summary
            if "data_quality" in self.validation_results:
                dq = self.validation_results["data_quality"]
                f.write("DATA QUALITY SUMMARY\n")
                f.write("-" * 40 + "\n")
                f.write(f"Overall Quality Score: {dq['overall_avg_quality']:.3f}\n")
                f.write(
                    f"High Quality Readings: {dq['high_quality_percentage']:.1f}%\n"
                )
                f.write(f"Low Quality Readings: {dq['low_quality_percentage']:.1f}%\n")
                f.write("\n")

            # Save full JSON results
            import json

            json_path = (
                OUTPUT_DIR
                / f'ml_validation_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
            with open(json_path, "w") as jf:
                json.dump(self.validation_results, jf, indent=2, default=str)

        print(f"\n✅ Validation report saved to: {report_path}")
        print(f"✅ Detailed results saved to: {json_path}")


def main():
    """Main validation function."""
    print("=== ML Data Validation Tool ===\n")

    # Initialize BigQuery client
    client = bigquery.Client(project=PROJECT_ID)

    # Run validation
    validator = MLDataValidator(client)
    results = validator.run_all_validations()

    # Generate report
    validator.generate_report()

    print("\n✅ ML data validation complete!")


if __name__ == "__main__":
    main()
