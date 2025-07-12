import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Configure matplotlib for better display
plt.style.use("seaborn-v0_8-darkgrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10

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

# Read the CSV with proper parameters
df = pd.read_csv(
    file_path,
    sep=";",
    decimal=",",
    skiprows=1,  # Skip the first row with units
    parse_dates={"DATA_RIFERIMENTO": ["DATA", "ORA"]},
    dayfirst=True,
)

print(f"\nDimensioni del dataset: {df.shape}")
print(
    f"Periodo dati: dal {df['DATA_RIFERIMENTO'].min()} al {df['DATA_RIFERIMENTO'].max()}"
)

# Initial inspection
print("\n--- Informazioni generali sul dataset ---")
print(df.info())

print("\n--- Prime 5 righe del dataset ---")
print(df.head())

print("\n--- Statistiche descrittive ---")
print(df.describe())

# Data cleaning and formatting
print("\n--- Pulizia e formattazione dei dati ---")

# Set datetime as index
df.set_index("DATA_RIFERIMENTO", inplace=True)

# Check for missing values
missing_values = df.isnull().sum()
print("\nValori mancanti per colonna:")
print(missing_values[missing_values > 0])

if df.isnull().any().any():
    print("\nApplicazione interpolazione lineare per gestire valori mancanti...")
    df = df.interpolate(method="linear")
    print("Interpolazione completata.")

# Check for duplicates
duplicates = df.index.duplicated().sum()
print(f"\nRighe duplicate trovate: {duplicates}")
if duplicates > 0:
    df = df[~df.index.duplicated(keep="first")]
    print(f"Rimosse {duplicates} righe duplicate.")

# Sort by index
df.sort_index(inplace=True)
print("\nDataFrame ordinato per data.")

# Identify numeric columns for analysis
numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
print(f"\nColonne numeriche identificate per l'analisi: {len(numeric_columns)}")
for i, col in enumerate(numeric_columns[:10]):
    print(f"  {i+1}. {col}")
if len(numeric_columns) > 10:
    print(f"  ... e altre {len(numeric_columns) - 10} colonne")

# Save cleaned data
df.to_csv("cleaned_data.csv", sep=";", decimal=",")
print("\nDati puliti salvati in 'cleaned_data.csv'")

print("\n✓ FASE 1 COMPLETATA")
