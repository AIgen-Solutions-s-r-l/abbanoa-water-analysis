import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("ANALISI DATI SERIE STORICHE - NODI SELARGIUS")
print("=" * 80)

# Phase 1: Data Ingestion and Preparation
print("\n### FASE 1: CARICAMENTO E PREPARAZIONE DEI DATI ###\n")

# Load the CSV file
file_path = (
    "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv"
)
print(f"Caricamento del file: {file_path}")

# First, let's read the header to understand the structure
with open(file_path, "r") as f:
    header1 = f.readline().strip()
    header2 = f.readline().strip()

print("\nStruttura del file:")
print(f"Header 1 (nomi colonne): {header1[:100]}...")
print(f"Header 2 (unità misura): {header2[:100]}...")

# Read the CSV with proper parameters
df = pd.read_csv(
    file_path,
    sep=";",
    decimal=",",
    skiprows=1,  # Skip the units row
    thousands=".",
    encoding="utf-8",
)

# Check actual column names
print("\nPrime colonne del DataFrame:")
print(df.columns.tolist()[:5])

# Create datetime column - handle the actual column names
if "DATA" in df.columns and "ORA" in df.columns:
    df["DATA_RIFERIMENTO"] = pd.to_datetime(
        df["DATA"] + " " + df["ORA"], format="%d/%m/%Y %H:%M:%S"
    )
else:
    # Use the first two columns if they're not named DATA and ORA
    col1, col2 = df.columns[0], df.columns[1]
    print(f"\nUsando colonne {col1} e {col2} per data e ora")
    df["DATA_RIFERIMENTO"] = pd.to_datetime(
        df[col1] + " " + df[col2], format="%d/%m/%Y %H:%M:%S"
    )

print(f"\nDimensioni del dataset: {df.shape}")
print(
    f"Periodo dati: dal {df['DATA_RIFERIMENTO'].min()} al {df['DATA_RIFERIMENTO'].max()}"
)

# Show column names
print("\n--- Colonne disponibili ---")
for i, col in enumerate(df.columns[:20]):
    print(f"{i+1}. {col}")
if len(df.columns) > 20:
    print(f"... e altre {len(df.columns) - 20} colonne")

# Initial inspection
print("\n--- Prime 5 righe del dataset ---")
print(df[["DATA_RIFERIMENTO"] + list(df.columns[2:7])].head())

# Set datetime as index
df.set_index("DATA_RIFERIMENTO", inplace=True)
# Drop the date and time columns (first two columns)
df.drop(df.columns[:2], axis=1, inplace=True)

# Convert numeric columns
numeric_columns = []
for col in df.columns:
    try:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", "."), errors="coerce"
        )
        if df[col].notna().any():
            numeric_columns.append(col)
    except:
        pass

print(f"\nColonne numeriche identificate: {len(numeric_columns)}")

# Check for missing values
missing_values = df[numeric_columns].isnull().sum()
missing_summary = missing_values[missing_values > 0]
if len(missing_summary) > 0:
    print(f"\nValori mancanti trovati in {len(missing_summary)} colonne:")
    print(missing_summary.head())
    print("\nApplicazione interpolazione lineare...")
    df[numeric_columns] = df[numeric_columns].interpolate(method="linear")

# Basic statistics
print("\n--- Statistiche descrittive (prime 5 colonne numeriche) ---")
print(df[numeric_columns[:5]].describe())

# Identify key metrics
print("\n--- Identificazione metriche chiave ---")
# Look for temperature, flow, and pressure columns
temp_cols = [col for col in numeric_columns if "TEMPERATURA" in col]
flow_cols = [col for col in numeric_columns if "PORTATA" in col]
pressure_cols = [col for col in numeric_columns if "BAR" in col or "PRESSIONE" in col]

print(f"Colonne temperatura trovate: {len(temp_cols)}")
print(f"Colonne portata trovate: {len(flow_cols)}")
print(f"Colonne pressione trovate: {len(pressure_cols)}")

# Save cleaned data
df.to_csv("cleaned_data.csv", sep=";", decimal=",")
print("\nDati puliti salvati in 'cleaned_data.csv'")

# Save key information for next phases
data_info = {
    "n_rows": len(df),
    "n_cols": len(df.columns),
    "numeric_cols": numeric_columns,
    "temp_cols": temp_cols,
    "flow_cols": flow_cols,
    "pressure_cols": pressure_cols,
    "date_range": (df.index.min(), df.index.max()),
    "sampling_interval": "30 minutes",
}

import json

with open("data_info.json", "w") as f:
    json.dump(
        {
            k: v if not isinstance(v, tuple) else [str(v[0]), str(v[1])]
            for k, v in data_info.items()
        },
        f,
        indent=2,
    )

print("\n✓ FASE 1 COMPLETATA")
print(f"\nRiepilogo dataset:")
print(f"- Righe: {data_info['n_rows']:,}")
print(f"- Colonne totali: {data_info['n_cols']}")
print(f"- Colonne numeriche: {len(numeric_columns)}")
print(
    f"- Intervallo temporale: {data_info['date_range'][0]} - {data_info['date_range'][1]}"
)
print(f"- Frequenza campionamento: {data_info['sampling_interval']}")
