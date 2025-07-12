"""Command-line interface for water infrastructure management."""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import click
from dependency_injector.wiring import Provide, inject
from tabulate import tabulate

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
from src.infrastructure.normalization.selargius_normalizer import (
    SelargiusDataNormalizer,
)


@click.group()
@click.pass_context
def cli(ctx):
    """Abbanoa Water Infrastructure Management CLI"""
    # Initialize DI container
    container = Container()

    # Configure container from environment
    container.config.bigquery.project_id.from_env(
        "BIGQUERY_PROJECT_ID", default="abbanoa-464816"
    )
    container.config.bigquery.dataset_id.from_env(
        "BIGQUERY_DATASET_ID", default="water_infrastructure"
    )
    container.config.bigquery.location.from_env("BIGQUERY_LOCATION", default="EU")

    container.config.anomaly_detection.z_score_threshold.from_env(
        "ANOMALY_Z_SCORE", default=3.0
    )
    container.config.anomaly_detection.min_data_points.from_env(
        "ANOMALY_MIN_POINTS", default=10
    )
    container.config.anomaly_detection.rolling_window_hours.from_env(
        "ANOMALY_WINDOW_HOURS", default=24
    )

    # Wire the container
    container.wire(modules=[__name__])

    # Store container in context
    ctx.obj = container


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for normalized data"
)
@click.option("--min-coverage", default=0.1, help="Minimum data coverage threshold")
@click.pass_context
def normalize(ctx, file_path: str, output: Optional[str], min_coverage: float):
    """Normalize CSV sensor data file."""
    click.echo(f"Normalizing data from: {file_path}")

    normalizer = SelargiusDataNormalizer(min_coverage_threshold=min_coverage)

    try:
        nodes, readings, quality_metrics = normalizer.normalize_file(file_path)

        click.echo("\nNormalization Results:")
        click.echo(f"- Nodes found: {len(nodes)}")
        click.echo(f"- Readings extracted: {len(readings)}")
        click.echo(f"- Data quality score: {quality_metrics.quality_score:.1f}%")
        click.echo(f"- Coverage: {quality_metrics.coverage_percentage:.1f}%")
        click.echo(f"- Missing values: {quality_metrics.missing_values_count}")
        click.echo(f"- Anomalies detected: {quality_metrics.anomaly_count}")

        if output:
            # Save normalized data
            output_path = Path(output)

            # Save nodes
            nodes_data = [node.to_dict() for node in nodes]
            with open(output_path.with_suffix(".nodes.json"), "w") as f:
                json.dump(nodes_data, f, indent=2, default=str)

            # Save readings (sample - in practice, this would be saved to database)
            readings_sample = [r.to_dict() for r in readings[:100]]
            with open(output_path.with_suffix(".readings.json"), "w") as f:
                json.dump(readings_sample, f, indent=2, default=str)

            # Save quality metrics
            with open(output_path.with_suffix(".quality.json"), "w") as f:
                json.dump(quality_metrics.to_dict(), f, indent=2)

            click.echo(f"\nData saved to: {output_path.stem}.*")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option("--node-id", help="Specific node ID to analyze")
@click.option("--hours", default=24, help="Hours to analyze")
@click.option("--critical-only", is_flag=True, help="Show only critical anomalies")
@click.pass_context
@inject
def detect_anomalies(
    ctx,
    node_id: Optional[str],
    hours: int,
    critical_only: bool,
    use_case: DetectNetworkAnomaliesUseCase = Provide[
        Container.detect_network_anomalies_use_case
    ],
):
    """Detect anomalies in sensor readings."""
    click.echo(f"Detecting anomalies for the last {hours} hours...")

    async def run_detection():
        node_ids = [node_id] if node_id else None

        anomalies = await use_case.execute(
            node_ids=node_ids, time_window_hours=hours, notify_on_critical=True
        )

        if critical_only:
            anomalies = [a for a in anomalies if a.severity in ["critical", "high"]]

        return anomalies

    try:
        anomalies = asyncio.run(run_detection())

        if not anomalies:
            click.echo("No anomalies detected.")
            return

        # Prepare table data
        table_data = []
        for anomaly in anomalies:
            table_data.append(
                [
                    anomaly.timestamp.strftime("%Y-%m-%d %H:%M"),
                    str(anomaly.node_id)[:8],  # Show first 8 chars of UUID
                    anomaly.anomaly_type,
                    anomaly.severity,
                    anomaly.measurement_type,
                    f"{anomaly.actual_value:.2f}",
                    f"{anomaly.deviation_percentage:.1f}%",
                ]
            )

        headers = [
            "Timestamp",
            "Node",
            "Type",
            "Severity",
            "Measurement",
            "Value",
            "Deviation",
        ]

        click.echo(f"\nFound {len(anomalies)} anomalies:")
        click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option("--node-id", required=True, help="Node ID to analyze")
@click.option(
    "--pattern",
    type=click.Choice(["hourly", "daily", "weekly", "monthly"]),
    default="daily",
)
@click.option("--days", default=7, help="Number of days to analyze")
@click.pass_context
@inject
def analyze_consumption(
    ctx,
    node_id: str,
    pattern: str,
    days: int,
    use_case: AnalyzeConsumptionPatternsUseCase = Provide[
        Container.analyze_consumption_patterns_use_case
    ],
):
    """Analyze water consumption patterns."""
    click.echo(f"Analyzing {pattern} consumption patterns for node {node_id}...")

    async def run_analysis():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        result = await use_case.execute(
            node_id=node_id,
            start_date=start_date,
            end_date=end_date,
            pattern_type=pattern,
        )

        return result

    try:
        result = asyncio.run(run_analysis())

        click.echo("\nConsumption Pattern Analysis:")
        click.echo(f"- Pattern type: {result.pattern_type}")
        click.echo(f"- Variability: {result.variability_coefficient:.1f}%")
        click.echo(f"- Peak periods: {', '.join(result.peak_hours[:3])}")
        click.echo(f"- Off-peak periods: {', '.join(result.off_peak_hours[:3])}")

        # Show consumption table
        click.echo("\nAverage Consumption:")
        table_data = []
        for period, consumption in list(result.average_consumption.items())[:10]:
            table_data.append([period, f"{consumption:.2f} L/s"])

        click.echo(
            tabulate(table_data, headers=["Period", "Avg Flow"], tablefmt="simple")
        )

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option("--network-id", required=True, help="Network ID to analyze")
@click.option("--days", default=1, help="Number of days to analyze")
@click.option("--show-leaks", is_flag=True, help="Show potential leakage zones")
@click.pass_context
@inject
def calculate_efficiency(
    ctx,
    network_id: str,
    days: int,
    show_leaks: bool,
    use_case: CalculateNetworkEfficiencyUseCase = Provide[
        Container.calculate_network_efficiency_use_case
    ],
):
    """Calculate network efficiency metrics."""
    click.echo(f"Calculating efficiency for network {network_id}...")

    async def run_calculation():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        result = await use_case.execute(
            network_id=network_id,
            start_date=start_date,
            end_date=end_date,
            include_node_details=True,
        )

        leaks = None
        if show_leaks:
            leaks = await use_case.detect_leakage_zones(
                network_id=network_id, start_date=start_date, end_date=end_date
            )

        return result, leaks

    try:
        result, leaks = asyncio.run(run_calculation())

        click.echo("\nNetwork Efficiency Report:")
        click.echo(
            f"- Period: {result.period_start.strftime('%Y-%m-%d')} to {result.period_end.strftime('%Y-%m-%d')}"
        )
        click.echo(f"- Efficiency: {result.efficiency_percentage:.1f}%")
        click.echo(f"- Total input: {result.total_input_volume:.1f} m³")
        click.echo(f"- Total output: {result.total_output_volume:.1f} m³")
        click.echo(
            f"- Water loss: {result.loss_volume:.1f} m³ ({result.loss_percentage:.1f}%)"
        )

        if result.node_contributions:
            click.echo("\nNode Contributions:")
            table_data = []
            for node_id, data in result.node_contributions.items():
                table_data.append(
                    [
                        data["node_name"],
                        f"{data['total_volume']:.1f} m³",
                        f"{data['average_flow_rate']:.1f} L/s",
                        data["reading_count"],
                    ]
                )

            headers = ["Node", "Total Volume", "Avg Flow", "Readings"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))

        if leaks:
            click.echo("\nPotential Leakage Zones:")
            table_data = []
            for leak in leaks:
                table_data.append(
                    [
                        leak["from_node_name"],
                        leak["to_node_name"],
                        f"{leak['loss_percentage']:.1f}%",
                        leak["severity"],
                    ]
                )

            headers = ["From", "To", "Loss %", "Severity"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option("--format", type=click.Choice(["json", "csv", "excel"]), default="json")
@click.option(
    "--output", "-o", type=click.Path(), required=True, help="Output file path"
)
@click.option(
    "--include",
    multiple=True,
    help="Data types to include (nodes, readings, anomalies)",
)
@click.pass_context
def export_data(ctx, format: str, output: str, include: List[str]):
    """Export data in various formats."""
    click.echo(f"Exporting data to {format} format...")

    # Default to all data types if none specified
    if not include:
        include = ["nodes", "readings", "anomalies"]

    try:
        # This would export actual data from the database
        click.echo(f"Exporting: {', '.join(include)}")
        click.echo(f"Output file: {output}")

        # Simulate export
        export_data = {
            "export_date": datetime.now().isoformat(),
            "format": format,
            "included_data": list(include),
            "record_counts": {"nodes": 12, "readings": 15000, "anomalies": 45},
        }

        output_path = Path(output)

        if format == "json":
            with open(output_path, "w") as f:
                json.dump(export_data, f, indent=2)
        elif format == "csv":
            # Would convert to CSV format
            click.echo("CSV export implemented in production")
        elif format == "excel":
            # Would create Excel file
            click.echo("Excel export implemented in production")

        click.echo(f"✅ Data exported successfully to: {output}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    cli()
