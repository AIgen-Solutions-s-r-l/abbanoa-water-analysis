# Analyze Consumption Patterns Use Case

This document provides a detailed overview of the `AnalyzeConsumptionPatternsUseCase`, which is responsible for analyzing water consumption patterns from sensor readings.

## Use Case Description

The `AnalyzeConsumptionPatternsUseCase` analyzes historical sensor data for a specific monitoring node to identify consumption patterns. It can analyze data on an hourly, daily, weekly, or monthly basis.

## API Endpoint

The use case is exposed through the following API endpoint:

`POST /api/v1/consumption/analyze`

### Request Body

```json
{
  "node_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2023-01-31T23:59:59Z",
  "pattern_type": "daily"
}
```

*   `node_id` (string, required): The UUID of the monitoring node to analyze.
*   `start_date` (string, required): The start date of the analysis period in ISO 8601 format.
*   `end_date` (string, required): The end date of the analysis period in ISO 8601 format.
*   `pattern_type` (string, required): The type of pattern to analyze. Must be one of `hourly`, `daily`, `weekly`, or `monthly`.

### Response Body

```json
{
  "node_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "pattern_type": "daily",
  "average_consumption": {
    "Monday": 150.5,
    "Tuesday": 160.2,
    "Wednesday": 155.8,
    "Thursday": 158.1,
    "Friday": 165.4,
    "Saturday": 140.9,
    "Sunday": 135.7
  },
  "peak_hours": ["Friday"],
  "off_peak_hours": ["Sunday"],
  "variability_coefficient": 8.5
}
```

*   `node_id` (string): The UUID of the monitoring node.
*   `pattern_type` (string): The type of pattern that was analyzed.
*   `average_consumption` (object): An object containing the average consumption for each period (e.g., hour, day of the week).
*   `peak_hours` (array): A list of the periods with the highest consumption.
*   `off_peak_hours` (array): A list of the periods with the lowest consumption.
*   `variability_coefficient` (float): The coefficient of variation of the consumption data.

## Implementation Details

The use case is implemented in the `src/application/use_cases/analyze_consumption_patterns.py` file. It uses the `SensorReadingRepository` to fetch the sensor data from the database and then performs the analysis in memory.
