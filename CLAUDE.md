# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a water infrastructure data analysis project for Abbanoa (Sardinian water utility company). The project contains monitoring data from water distribution nodes in Selargius, including temperature, flow rates, and pressure measurements.

## Data Structure

The main data is stored in CSV format in the `RAWDATA/` directory. The CSV files contain:
- Time-series data with 30-minute intervals
- Multiple sensor readings per node including:
  - Temperature (internal) in degrees Celsius
  - Instantaneous flow rate (L/S)
  - Total flow volume (M3)
  - Pressure (BAR)
- Data from multiple monitoring nodes in the Selargius area

The CSV uses semicolon (;) as delimiter and Italian date format (DD/MM/YYYY).

## Common Analysis Tasks

When working with this data, typical tasks might include:
- Time-series analysis of flow rates and pressures
- Anomaly detection in water distribution
- Aggregation and visualization of sensor data
- Data quality checks and cleaning

## Data Processing Considerations

- The CSV files use semicolon delimiters
- Date format is DD/MM/YYYY with HH:MM:SS time format
- Multiple measurement types are present in a single file (wide format)
- Column headers span multiple rows with units on the second row