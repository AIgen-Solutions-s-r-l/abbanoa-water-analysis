"""
Analyze data quality issues and create an improved normalizer
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, List, Tuple

print("=== ANALISI QUALITY SCORE ===\n")

# Load the normalization metadata
with open("normalization_metadata.json", "r") as f:
    metadata = json.load(f)

print(f"Quality Score Attuale: {metadata['validation']['quality_score']:.1f}%\n")

# Analyze missing values
print("Analisi Valori Mancanti:")
print("-" * 50)
missing_data = metadata["validation"]["missing_values"]

if missing_data:
    for col, info in sorted(
        missing_data.items(), key=lambda x: x[1]["percentage"], reverse=True
    ):
        print(
            f"{col:30} {info['count']:6} valori mancanti ({info['percentage']:5.1f}%)"
        )
else:
    print("Nessun valore mancante rilevato")

# Load the original CSV to understand the structure better
print("\n\nAnalisi Struttura Dati Originale:")
print("-" * 50)

# Read with original structure
df_original = pd.read_csv(
    "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv",
    sep=";",
    nrows=5,
)

print("Prime righe del file originale:")
print(df_original)

# Read the header lines directly
with open(
    "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv",
    "r",
) as f:
    header1 = f.readline().strip().split(";")
    header2 = f.readline().strip().split(";")

print(f"\nNumero totale di colonne: {len(header1)}")

# Group columns by sensor/node
nodes = {}
for i, (h1, h2) in enumerate(
    zip(header1[2:], header2[2:]), start=2
):  # Skip DATA and ORA
    if h1 and not h1.startswith("Unnamed"):
        # Extract node name
        if "(" in h1 and ")" in h1:
            node_name = h1.split(")")[0] + ")"
            metric_name = h1.split(")")[-1].strip(" -")
        else:
            node_name = "UNKNOWN"
            metric_name = h1

        if node_name not in nodes:
            nodes[node_name] = []

        nodes[node_name].append(
            {"index": i, "metric": metric_name, "unit": h2, "full_name": h1}
        )

print(f"\nNodi/Sensori identificati: {len(nodes)}")
for node, metrics in nodes.items():
    print(f"\n{node}:")
    for m in metrics:
        print(f"  - {m['metric']} ({m['unit']})")

# Load normalized data to check actual values
df_norm = pd.read_csv("normalized_data.csv")

# Analyze which columns have actual data
print("\n\nAnalisi Colonne con Dati Effettivi:")
print("-" * 50)

columns_with_data = []
columns_empty = []

for col in df_norm.columns:
    if col.startswith("_") or col == "timestamp":
        continue

    non_null_count = df_norm[col].notna().sum()
    unique_values = df_norm[col].nunique()

    if non_null_count > 0 and unique_values > 1:  # Has data and variation
        columns_with_data.append(
            {
                "name": col,
                "non_null_count": non_null_count,
                "unique_values": unique_values,
                "coverage": non_null_count / len(df_norm) * 100,
            }
        )
    else:
        columns_empty.append(col)

print(f"\nColonne con dati significativi: {len(columns_with_data)}")
for col_info in sorted(columns_with_data, key=lambda x: x["coverage"], reverse=True):
    print(f"  {col_info['name']:30} Coverage: {col_info['coverage']:5.1f}%")

print(f"\nColonne vuote o senza variazione: {len(columns_empty)}")

# Create improved configuration
print("\n\n=== CONFIGURAZIONE MIGLIORATA ===")

# Find which nodes actually have data
active_nodes = set()
for col_info in columns_with_data:
    col_name = col_info["name"]
    # Map back to original node
    for node, metrics in nodes.items():
        if any(col_name in m["full_name"].lower() for m in metrics):
            active_nodes.add(node)

print(f"\nNodi attivi (con dati): {len(active_nodes)}")
for node in active_nodes:
    print(f"  - {node}")

# Calculate improved quality score
total_expected_values = len(df_norm) * len(columns_with_data)
total_actual_values = sum(col["non_null_count"] for col in columns_with_data)
improved_quality_score = (
    (total_actual_values / total_expected_values) * 100
    if total_expected_values > 0
    else 0
)

print(f"\nQuality Score se usiamo solo colonne attive: {improved_quality_score:.1f}%")

# Generate configuration for selective import
config = {
    "quality_analysis": {
        "original_quality_score": metadata["validation"]["quality_score"],
        "total_columns": len(header1),
        "columns_with_data": len(columns_with_data),
        "columns_empty": len(columns_empty),
        "improved_quality_score": improved_quality_score,
    },
    "active_nodes": list(active_nodes),
    "recommended_columns": [col["name"] for col in columns_with_data],
    "column_coverage": {col["name"]: col["coverage"] for col in columns_with_data},
}

# Save configuration
with open("quality_improvement_config.json", "w") as f:
    json.dump(config, f, indent=2)

print("\n\n=== RACCOMANDAZIONI ===")
print(
    f"1. Il file contiene dati per {len(nodes)} nodi, ma solo {len(active_nodes)} hanno dati"
)
print(
    f"2. Su {len(header1)} colonne totali, solo {len(columns_with_data)} contengono dati significativi"
)
print(
    f"3. Quality score può migliorare da {metadata['validation']['quality_score']:.1f}% a {improved_quality_score:.1f}%"
)
print("\nStrategia suggerita:")
print("- Creare tabelle separate per ogni nodo attivo")
print("- Importare solo le colonne con dati")
print("- Configurare alert per monitorare quando nuovi nodi iniziano a trasmettere")

# Create a sample filtered dataset
print("\n\nCreazione dataset filtrato di esempio...")
# Check if timestamp column exists
timestamp_cols = ["timestamp"] if "timestamp" in df_norm.columns else []
data_cols = [col["name"] for col in columns_with_data[:10]]
metadata_cols = [col for col in df_norm.columns if col.startswith("_")]
columns_to_keep = timestamp_cols + data_cols + metadata_cols

# Only create filtered dataset if we have columns to keep
if columns_to_keep:
    df_filtered = df_norm[columns_to_keep]
    df_filtered.to_csv("normalized_data_filtered.csv", index=False)
    print(
        f"✓ Dataset filtrato salvato: normalized_data_filtered.csv ({len(columns_to_keep)} colonne)"
    )
else:
    print("⚠️  Nessuna colonna selezionata per il dataset filtrato")
