"""Data normalizer for Selargius water sensor data."""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd

from src.domain.entities.monitoring_node import MonitoringNode
from src.domain.entities.sensor_reading import SensorReading
from src.domain.value_objects.location import NodeLocation
from src.domain.value_objects.measurements import (
    FlowRate,
    Pressure,
    Temperature,
    Volume,
)
from src.domain.value_objects.quality_metrics import DataQualityMetrics
from src.domain.value_objects.sensor_type import SensorType


class SelargiusDataNormalizer:
    """Normalizes CSV data from Selargius monitoring nodes."""

    def __init__(
        self,
        decimal_separator: str = ",",
        thousands_separator: str = ".",
        csv_separator: str = ";",
        min_coverage_threshold: float = 0.10,
    ) -> None:
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator
        self.csv_separator = csv_separator
        self.min_coverage_threshold = min_coverage_threshold

    def normalize_file(
        self, file_path: str
    ) -> Tuple[List[MonitoringNode], List[SensorReading], DataQualityMetrics]:
        """Normalize CSV file and return domain entities."""
        # Read and parse file
        headers, units, df = self._read_csv_file(file_path)

        # Parse node structure
        node_structure = self._parse_node_structure(headers, units)

        # Create domain entities
        nodes = []
        readings = []

        for node_name, node_info in node_structure.items():
            # Create monitoring node
            node = self._create_monitoring_node(node_name, node_info)
            nodes.append(node)

            # Extract readings for this node
            node_readings = self._extract_node_readings(df, node, node_info)
            readings.extend(node_readings)

        # Calculate quality metrics
        quality_metrics = self._calculate_quality_metrics(df, readings, node_structure)

        return nodes, readings, quality_metrics

    def _read_csv_file(
        self, file_path: str
    ) -> Tuple[List[str], List[str], pd.DataFrame]:
        """Read CSV file with headers and units."""
        with open(file_path, "r") as f:
            headers = f.readline().strip().split(self.csv_separator)
            units = f.readline().strip().split(self.csv_separator)

        # Read data
        df = pd.read_csv(
            file_path,
            sep=self.csv_separator,
            decimal=self.decimal_separator,
            thousands=self.thousands_separator,
            skiprows=2,
            header=None,
            names=headers,
        )

        # Process timestamp
        if "DATA" in df.columns and "ORA" in df.columns:
            df["timestamp"] = pd.to_datetime(
                df["DATA"] + " " + df["ORA"], format="%d/%m/%Y %H:%M:%S"
            )
            df.set_index("timestamp", inplace=True)
            df.drop(["DATA", "ORA"], axis=1, inplace=True)

        # Convert numeric columns
        for col in df.columns:
            if col not in ["timestamp"]:
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "."), errors="coerce"
                )

        return headers, units, df

    def _parse_node_structure(self, headers: List[str], units: List[str]) -> Dict:
        """Parse headers to identify nodes and their metrics."""
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

            # Clean names
            clean_node = self._clean_name(node_name)

            if clean_node not in nodes:
                nodes[clean_node] = {"original_name": node_name, "metrics": []}

            nodes[clean_node]["metrics"].append(
                {
                    "column_name": header,
                    "metric_name": metric_name,
                    "unit": unit,
                    "index": i,
                }
            )

        return nodes

    def _create_monitoring_node(
        self, node_name: str, node_info: Dict
    ) -> MonitoringNode:
        """Create monitoring node entity from parsed data."""
        # Extract location info from node name
        location_parts = node_info["original_name"].split(" ")
        site_name = location_parts[0] if location_parts else node_name
        area = "Selargius"  # Default area

        # Try to extract PCR unit
        pcr_unit = None
        if "PCR" in node_info["original_name"]:
            pcr_match = re.search(r"PCR[\s-]?(\d+)", node_info["original_name"])
            if pcr_match:
                pcr_unit = pcr_match.group(1)

        location = NodeLocation(site_name=site_name, area=area, pcr_unit=pcr_unit)

        # Determine node type based on metrics
        node_type = self._determine_node_type(node_info["metrics"])

        return MonitoringNode(
            name=node_info["original_name"],
            location=location,
            node_type=node_type,
            description=f"Monitoring node with {len(node_info['metrics'])} sensors",
        )

    def _determine_node_type(self, metrics: List[Dict]) -> str:
        """Determine node type based on available metrics."""
        metric_names = [m["metric_name"].lower() for m in metrics]

        if any("input" in name or "ingresso" in name for name in metric_names):
            return "input"
        elif any("output" in name or "uscita" in name for name in metric_names):
            return "output"
        elif any("tank" in name or "serbatoio" in name for name in metric_names):
            return "storage"
        else:
            return "distribution"

    def _extract_node_readings(
        self, df: pd.DataFrame, node: MonitoringNode, node_info: Dict
    ) -> List[SensorReading]:
        """Extract sensor readings for a specific node."""
        readings = []

        for _, row in df.iterrows():
            timestamp = (
                row.name
                if isinstance(df.index, pd.DatetimeIndex)
                else row.get("timestamp")
            )

            if pd.isna(timestamp):
                continue

            # Extract measurements for this timestamp
            temperature = None
            flow_rate = None
            pressure = None
            volume = None

            for metric in node_info["metrics"]:
                col_name = metric["column_name"]
                if col_name not in row.index:
                    continue

                value = row[col_name]
                if pd.isna(value):
                    continue

                metric_lower = metric["metric_name"].lower()
                unit_lower = metric["unit"].lower()

                try:
                    if "temp" in metric_lower or "°c" in unit_lower:
                        temperature = Temperature(float(value))
                    elif (
                        "flow" in metric_lower
                        or "portata" in metric_lower
                        or "l/s" in unit_lower
                    ):
                        flow_rate = FlowRate(float(value))
                    elif "press" in metric_lower or "bar" in unit_lower:
                        pressure = Pressure(float(value))
                    elif (
                        "volum" in metric_lower
                        or "m3" in unit_lower
                        or "m³" in unit_lower
                    ):
                        volume = Volume(float(value))
                except ValueError:
                    # Skip invalid measurements
                    continue

            # Create reading if at least one measurement exists
            if any([temperature, flow_rate, pressure, volume]):
                reading = SensorReading(
                    node_id=node.id,
                    sensor_type=SensorType.MULTI_PARAMETER,
                    timestamp=(
                        timestamp.to_pydatetime()
                        if hasattr(timestamp, "to_pydatetime")
                        else timestamp
                    ),
                    temperature=temperature,
                    flow_rate=flow_rate,
                    pressure=pressure,
                    volume=volume,
                )
                readings.append(reading)

        return readings

    def _calculate_quality_metrics(
        self, df: pd.DataFrame, readings: List[SensorReading], node_structure: Dict
    ) -> DataQualityMetrics:
        """Calculate overall data quality metrics."""
        total_expected_cells = len(df) * sum(
            len(n["metrics"]) for n in node_structure.values()
        )

        # Count non-null values
        non_null_count = 0
        for node_info in node_structure.values():
            for metric in node_info["metrics"]:
                col_name = metric["column_name"]
                if col_name in df.columns:
                    non_null_count += df[col_name].notna().sum()

        coverage_percentage = (
            (non_null_count / total_expected_cells * 100)
            if total_expected_cells > 0
            else 0
        )

        # Count anomalies (simplified - just count extreme values)
        anomaly_count = 0
        for reading in readings:
            if (
                reading.flow_rate and reading.flow_rate.value > 1000
            ):  # Extreme flow rate
                anomaly_count += 1
            if reading.pressure and reading.pressure.value > 10:  # High pressure
                anomaly_count += 1

        missing_values_count = total_expected_cells - non_null_count

        return DataQualityMetrics(
            coverage_percentage=coverage_percentage,
            missing_values_count=missing_values_count,
            anomaly_count=anomaly_count,
            total_records=len(df),
        )

    def _clean_name(self, name: str) -> str:
        """Clean name for consistency."""
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
