"""
Improved Data Normalizer with Better Quality Score Handling
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedWaterDataNormalizer:
    """Enhanced normalizer with selective column import and better quality metrics"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self.get_default_config()

    @staticmethod
    def get_default_config() -> Dict:
        return {
            "timestamp_formats": ["%d/%m/%Y %H:%M:%S"],
            "decimal_separator": ",",
            "thousands_separator": ".",
            "csv_separator": ";",
            "min_coverage_threshold": 0.10,  # Minimum 10% data coverage to include column
            "exclude_patterns": ["unnamed", "unknown"],  # Patterns to exclude
            "group_by_node": True,  # Create separate tables per node
        }

    def analyze_and_normalize(
        self, file_path: str
    ) -> Dict[str, Tuple[pd.DataFrame, Dict]]:
        """Analyze CSV and create normalized datasets grouped by node/sensor"""
        logger.info(f"Analyzing file: {file_path}")

        # Read headers
        with open(file_path, "r") as f:
            headers = f.readline().strip().split(self.config["csv_separator"])
            units = f.readline().strip().split(self.config["csv_separator"])

        # Parse nodes and metrics
        node_structure = self._parse_node_structure(headers, units)

        # Read data
        df = pd.read_csv(
            file_path,
            sep=self.config["csv_separator"],
            decimal=self.config["decimal_separator"],
            thousands=self.config["thousands_separator"],
            skiprows=2,
            header=None,
            names=headers,
        )

        # Process timestamp
        if "DATA" in df.columns and "ORA" in df.columns:
            df["timestamp"] = pd.to_datetime(
                df["DATA"] + " " + df["ORA"], format=self.config["timestamp_formats"][0]
            )
            df.set_index("timestamp", inplace=True)
            df.drop(["DATA", "ORA"], axis=1, inplace=True)

        # Convert numeric columns
        for col in df.columns:
            if col not in ["timestamp"]:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "."), errors="coerce"
                )

        # Group by node and create separate datasets
        results = {}

        if self.config["group_by_node"]:
            for node_name, node_info in node_structure.items():
                results[node_name] = self._create_node_dataset(
                    df, node_info, node_name, file_path
                )
        else:
            # Single dataset with quality filtering
            results["all_sensors"] = self._create_filtered_dataset(
                df, node_structure, file_path
            )

        return results

    def _parse_node_structure(self, headers: List[str], units: List[str]) -> Dict:
        """Parse headers to identify nodes and their metrics"""
        nodes = {}

        for i, (header, unit) in enumerate(zip(headers, units)):
            if not header or header.startswith("Unnamed") or header in ["DATA", "ORA"]:
                continue

            # Extract node name and metric
            if "(" in header and ")" in header:
                parts = header.split(")")
                node_name = parts[0] + ")"
                metric_name = parts[-1].strip(" -") if len(parts) > 1 else "UNKNOWN"
            else:
                node_name = "GENERIC"
                metric_name = header

            # Clean names for BigQuery
            clean_node = self._clean_name(node_name)
            clean_metric = self._clean_name(metric_name)

            if clean_node not in nodes:
                nodes[clean_node] = {"original_name": node_name, "metrics": []}

            nodes[clean_node]["metrics"].append(
                {
                    "column_name": header,
                    "metric_name": metric_name,
                    "clean_name": clean_metric,
                    "unit": unit,
                    "index": i,
                }
            )

        return nodes

    def _create_node_dataset(
        self, df: pd.DataFrame, node_info: Dict, node_name: str, file_path: str
    ) -> Tuple[pd.DataFrame, Dict]:
        """Create dataset for a specific node with quality checks"""

        # Select columns for this node
        columns = [m["column_name"] for m in node_info["metrics"]]
        node_df = df[columns].copy()

        # Rename columns to clean names
        column_mapping = {
            m["column_name"]: m["clean_name"] for m in node_info["metrics"]
        }
        node_df.rename(columns=column_mapping, inplace=True)

        # Calculate coverage for each metric
        coverage_stats = {}
        columns_to_keep = []

        for metric in node_info["metrics"]:
            clean_name = metric["clean_name"]
            non_null = node_df[clean_name].notna().sum()
            coverage = non_null / len(node_df)

            coverage_stats[clean_name] = {
                "coverage": coverage,
                "non_null_count": non_null,
                "unit": metric["unit"],
                "original_name": metric["metric_name"],
            }

            if coverage >= self.config["min_coverage_threshold"]:
                columns_to_keep.append(clean_name)

        # Filter dataset
        filtered_df = node_df[columns_to_keep].copy()

        # Add metadata
        filtered_df["_node"] = node_info["original_name"]
        filtered_df["_ingestion_timestamp"] = datetime.now()
        filtered_df["_source_file"] = file_path.split("/")[-1]

        # Calculate quality score
        if columns_to_keep:
            total_expected = len(filtered_df) * len(columns_to_keep)
            total_actual = sum(
                filtered_df[col].notna().sum() for col in columns_to_keep
            )
            quality_score = (total_actual / total_expected) * 100
        else:
            quality_score = 0

        metadata = {
            "node_name": node_name,
            "original_name": node_info["original_name"],
            "metrics_total": len(node_info["metrics"]),
            "metrics_kept": len(columns_to_keep),
            "metrics_dropped": len(node_info["metrics"]) - len(columns_to_keep),
            "rows": len(filtered_df),
            "quality_score": quality_score,
            "coverage_stats": coverage_stats,
            "timestamp_range": {"min": str(df.index.min()), "max": str(df.index.max())},
        }

        return filtered_df, metadata

    def _create_filtered_dataset(
        self, df: pd.DataFrame, node_structure: Dict, file_path: str
    ) -> Tuple[pd.DataFrame, Dict]:
        """Create single dataset with quality-filtered columns"""

        # Analyze all columns
        columns_analysis = []

        for node_name, node_info in node_structure.items():
            for metric in node_info["metrics"]:
                col = metric["column_name"]
                if col in df.columns:
                    non_null = df[col].notna().sum()
                    coverage = non_null / len(df)

                    if coverage >= self.config["min_coverage_threshold"]:
                        columns_analysis.append(
                            {
                                "column": col,
                                "clean_name": f"{node_name}_{metric['clean_name']}",
                                "coverage": coverage,
                                "node": node_info["original_name"],
                                "metric": metric["metric_name"],
                                "unit": metric["unit"],
                            }
                        )

        # Sort by coverage
        columns_analysis.sort(key=lambda x: x["coverage"], reverse=True)

        # Create filtered dataset
        column_mapping = {col["column"]: col["clean_name"] for col in columns_analysis}
        columns_to_keep = list(column_mapping.keys())

        filtered_df = df[columns_to_keep].copy()
        filtered_df.rename(columns=column_mapping, inplace=True)

        # Add metadata
        filtered_df["_ingestion_timestamp"] = datetime.now()
        filtered_df["_source_file"] = file_path.split("/")[-1]

        # Quality score
        total_expected = len(filtered_df) * len(columns_to_keep)
        total_actual = sum(
            filtered_df[col].notna().sum() for col in column_mapping.values()
        )
        quality_score = (total_actual / total_expected) * 100

        metadata = {
            "dataset_type": "filtered_all_sensors",
            "total_columns_original": sum(
                len(n["metrics"]) for n in node_structure.values()
            ),
            "columns_kept": len(columns_to_keep),
            "min_coverage_threshold": self.config["min_coverage_threshold"],
            "quality_score": quality_score,
            "nodes_included": list(set(col["node"] for col in columns_analysis)),
            "column_details": columns_analysis,
        }

        return filtered_df, metadata

    def _clean_name(self, name: str) -> str:
        """Clean name for BigQuery compatibility"""
        import re

        # Remove parentheses and special characters
        clean = re.sub(r"[^\w\s]", " ", name)
        clean = re.sub(r"\s+", "_", clean.strip())
        clean = clean.lower()

        # Remove common prefixes/suffixes
        clean = clean.replace("selargius_", "").replace("quartucciu_", "")

        # Limit length
        if len(clean) > 64:
            clean = clean[:64]

        return clean or "unknown"

    def generate_bigquery_configs(self, results: Dict) -> Dict:
        """Generate BigQuery table configurations for each dataset"""
        configs = {}

        for dataset_name, (df, metadata) in results.items():
            # Generate schema
            schema = []

            # Add timestamp if in index
            if isinstance(df.index, pd.DatetimeIndex):
                schema.append(
                    {
                        "name": "timestamp",
                        "type": "TIMESTAMP",
                        "mode": "REQUIRED",
                        "description": "Measurement timestamp",
                    }
                )

            # Add data columns
            for col in df.columns:
                if col.startswith("_"):
                    continue

                schema.append(
                    {
                        "name": col,
                        "type": "FLOAT64",
                        "mode": "NULLABLE",
                        "description": self._get_column_description(col, metadata),
                    }
                )

            # Add metadata columns
            schema.extend(
                [
                    {
                        "name": "_ingestion_timestamp",
                        "type": "TIMESTAMP",
                        "mode": "REQUIRED",
                    },
                    {"name": "_source_file", "type": "STRING", "mode": "REQUIRED"},
                ]
            )

            if "_node" in df.columns:
                schema.append({"name": "_node", "type": "STRING", "mode": "REQUIRED"})

            # Table configuration
            safe_name = dataset_name.replace(" ", "_").replace("-", "_").lower()
            table_config = {
                "dataset_id": "water_infrastructure",
                "table_id": f"sensor_{safe_name}_{datetime.now().strftime('%Y%m')}",
                "schema": schema,
                "time_partitioning": {"type": "DAY", "field": "timestamp"},
                "clustering_fields": ["_source_file"]
                + (["_node"] if "_node" in df.columns else []),
                "description": f"Water sensor data - {dataset_name}",
                "metadata": metadata,
            }

            configs[dataset_name] = table_config

        return configs

    def _get_column_description(self, col_name: str, metadata: Dict) -> str:
        """Get column description from metadata"""
        if "coverage_stats" in metadata and col_name in metadata["coverage_stats"]:
            info = metadata["coverage_stats"][col_name]
            return f"{info['original_name']} ({info['unit']})"
        elif "column_details" in metadata:
            for col_info in metadata["column_details"]:
                if col_info["clean_name"] == col_name:
                    return f"{col_info['metric']} ({col_info['unit']})"
        return col_name


# Example usage
if __name__ == "__main__":
    # Initialize improved normalizer
    config = ImprovedWaterDataNormalizer.get_default_config()
    config.update(
        {
            "min_coverage_threshold": 0.5,  # Require at least 50% data coverage
            "group_by_node": True,  # Create separate datasets per node
        }
    )
    normalizer = ImprovedWaterDataNormalizer(config)

    # Process file
    file_path = "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv"
    results = normalizer.analyze_and_normalize(file_path)

    # Generate BigQuery configurations
    bq_configs = normalizer.generate_bigquery_configs(results)

    # Save results
    print("\n=== RISULTATI NORMALIZZAZIONE MIGLIORATA ===\n")

    for dataset_name, (df, metadata) in results.items():
        print(f"\nDataset: {dataset_name}")
        print(f"  - Righe: {metadata['rows']}")
        print(f"  - Quality Score: {metadata['quality_score']:.1f}%")

        if "metrics_kept" in metadata:
            print(
                f"  - Metriche mantenute: {metadata['metrics_kept']}/{metadata['metrics_total']}"
            )

        # Save dataset
        output_file = f"normalized_{dataset_name.replace(' ', '_')}.csv"
        df.to_csv(output_file)
        print(f"  - Salvato in: {output_file}")

        # Save metadata
        meta_file = f"metadata_{dataset_name.replace(' ', '_')}.json"
        with open(meta_file, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

    # Save BigQuery configs
    with open("bigquery_configs_improved.json", "w") as f:
        json.dump(bq_configs, f, indent=2, default=str)

    print("\n✓ Normalizzazione completata con quality score migliorato!")
    print("✓ Configurazioni BigQuery salvate in: bigquery_configs_improved.json")
