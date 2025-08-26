# Abbanoa Water Infrastructure Management CLI

The Abbanoa Water Infrastructure Management CLI is a powerful tool for interacting with the system from the command line. It allows you to perform various tasks, such as data normalization, anomaly detection, and data export.

## Getting Started

To use the CLI, you need to have the project's dependencies installed. You can then run the CLI using the following command:

```bash
poetry run python src/presentation/cli/main.py [COMMAND] [OPTIONS]
```

## Commands

### `normalize`

Normalizes CSV sensor data from a file.

**Usage:**

```bash
poetry run python src/presentation/cli/main.py normalize [OPTIONS] FILE_PATH
```

**Arguments:**

*   `FILE_PATH`: The path to the CSV file to normalize.

**Options:**

*   `--output, -o`: The output file for the normalized data.
*   `--min-coverage`: The minimum data coverage threshold.

**Example:**

```bash
poetry run python src/presentation/cli/main.py normalize data.csv -o normalized_data.json
```

### `detect-anomalies`

Detects anomalies in sensor readings.

**Usage:**

```bash
poetry run python src/presentation/cli/main.py detect-anomalies [OPTIONS]
```

**Options:**

*   `--node-id`: The specific node ID to analyze.
*   `--hours`: The number of hours to analyze.
*   `--critical-only`: Show only critical anomalies.

**Example:**

```bash
poetry run python src/presentation/cli/main.py detect-anomalies --node-id 1234-5678-9012-3456 --hours 48
```

### `analyze-consumption`

Analyzes water consumption patterns.

**Usage:**

```bash
poetry run python src/presentation/cli/main.py analyze-consumption [OPTIONS]
```

**Options:**

*   `--node-id`: The node ID to analyze.
*   `--pattern`: The pattern to analyze (hourly, daily, weekly, monthly).
*   `--days`: The number of days to analyze.

**Example:**

```bash
poetry run python src/presentation/cli/main.py analyze-consumption --node-id 1234-5678-9012-3456 --pattern daily --days 7
```

### `calculate-efficiency`

Calculates network efficiency metrics.

**Usage:**

```bash
poetry run python src/presentation/cli/main.py calculate-efficiency [OPTIONS]
```

**Options:**

*   `--network-id`: The network ID to analyze.
*   `--days`: The number of days to analyze.
*   `--show-leaks`: Show potential leakage zones.

**Example:**

```bash
poetry run python src/presentation/cli/main.py calculate-efficiency --network-id 1234-5678-9012-3456 --days 30
```

### `export-data`

Exports data in various formats.

**Usage:**

```bash
poetry run python src/presentation/cli/main.py export-data [OPTIONS]
```

**Options:**

*   `--format`: The output format (json, csv, excel).
*   `--output, -o`: The output file path.
*   `--include`: The data types to include (nodes, readings, anomalies).

**Example:**

```bash
poetry run python src/presentation/cli/main.py export-data --format json --output data.json --include nodes readings
```
