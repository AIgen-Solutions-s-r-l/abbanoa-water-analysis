import pandas as pd
import numpy as np
import json
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import warnings

warnings.filterwarnings("ignore")

print("\n### FASE 2: ANALISI ESPLORATIVA DEI DATI (EDA) ###\n")

# Load cleaned data and info
df = pd.read_csv(
    "cleaned_data.csv", sep=";", decimal=",", index_col=0, parse_dates=True
)
with open("data_info.json", "r") as f:
    data_info = json.load(f)

print(f"Dataset caricato: {len(df)} righe, {len(df.columns)} colonne")

# Since column names are generic, let's read the original headers to understand them
with open(
    "RAWDATA/REPORT_NODI_SELARGIUS_AGGREGATI_30_MIN_20241113060000_20250331060000.csv",
    "r",
) as f:
    header_line = f.readline().strip().split(";")[2:]  # Skip DATA and ORA
    units_line = f.readline().strip().split(";")[2:]

# Map generic column names to descriptive names
column_mapping = {}
for i, (col, header, unit) in enumerate(zip(df.columns, header_line, units_line)):
    column_mapping[col] = f"{header} ({unit})" if unit else header

# Select key metrics for analysis
# Based on the original headers, we have temperature, flow rate, and pressure data
key_metrics = []
for col, desc in column_mapping.items():
    if any(
        keyword in desc.upper() for keyword in ["TEMPERATURA", "PORTATA", "PRESSIONE"]
    ):
        key_metrics.append((col, desc))

print("\nMetriche chiave identificate per l'analisi:")
for i, (col, desc) in enumerate(key_metrics[:5]):
    print(f"{i+1}. {desc}")

# 1. Time Series Visualization
print("\n--- Visualizzazione Serie Temporali ---")
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
fig.suptitle("Andamento Temporale delle Metriche Principali", fontsize=16)

# Plot first three key metrics
for idx, (col, desc) in enumerate(key_metrics[:3]):
    ax = axes[idx]
    df[col].plot(ax=ax, color=f"C{idx}", linewidth=0.5)
    ax.set_ylabel(desc[:50] + "..." if len(desc) > 50 else desc)
    ax.grid(True, alpha=0.3)
    ax.set_title(f"Serie temporale: {desc[:60]}...", fontsize=10)

plt.tight_layout()
plt.savefig("time_series_overview.png", dpi=150, bbox_inches="tight")
print("✓ Grafici serie temporali salvati in 'time_series_overview.png'")

# 2. Statistical Analysis per time period
print("\n--- Analisi Statistica per Periodo ---")
# Add time-based features
df["hour"] = df.index.hour
df["day_of_week"] = df.index.dayofweek
df["month"] = df.index.month

# Analyze patterns by hour of day
hourly_patterns = df.groupby("hour")[df.columns[:5]].mean()
print("\nPattern medi orari (prime 5 colonne):")
print(hourly_patterns.head())

# 3. Correlation Analysis
print("\n--- Analisi di Correlazione ---")
numeric_cols = df.select_dtypes(include=[np.number]).columns
# Remove time-based features for correlation
corr_cols = [col for col in numeric_cols if col not in ["hour", "day_of_week", "month"]]
correlation_matrix = df[corr_cols].corr()

# Plot correlation heatmap
plt.figure(figsize=(12, 10))
im = plt.imshow(
    correlation_matrix.values, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1
)
plt.colorbar(im, label="Correlazione")
plt.title("Matrice di Correlazione tra le Variabili", fontsize=14)

# Add labels
ax = plt.gca()
ax.set_xticks(range(len(corr_cols)))
ax.set_yticks(range(len(corr_cols)))
ax.set_xticklabels(
    [column_mapping.get(col, col)[:30] for col in corr_cols], rotation=45, ha="right"
)
ax.set_yticklabels([column_mapping.get(col, col)[:30] for col in corr_cols])

# Add correlation values
for i in range(len(corr_cols)):
    for j in range(len(corr_cols)):
        text = ax.text(
            j,
            i,
            f"{correlation_matrix.iloc[i, j]:.2f}",
            ha="center",
            va="center",
            color="black" if abs(correlation_matrix.iloc[i, j]) < 0.5 else "white",
            fontsize=8,
        )

plt.tight_layout()
plt.savefig("correlation_heatmap.png", dpi=150, bbox_inches="tight")
print("✓ Heatmap di correlazione salvata in 'correlation_heatmap.png'")

# Find high correlations
high_corr = []
for i in range(len(corr_cols)):
    for j in range(i + 1, len(corr_cols)):
        if abs(correlation_matrix.iloc[i, j]) > 0.7:
            high_corr.append(
                (corr_cols[i], corr_cols[j], correlation_matrix.iloc[i, j])
            )

if high_corr:
    print("\nCorrelazioni elevate trovate (|r| > 0.7):")
    for col1, col2, corr in high_corr[:5]:
        print(
            f"  {column_mapping.get(col1, col1)[:40]} <-> {column_mapping.get(col2, col2)[:40]}: {corr:.3f}"
        )

# 4. Basic Time Series Decomposition (simplified without statsmodels)
print("\n--- Analisi Trend e Pattern ---")
# Use rolling statistics for trend analysis
window_size = 24 * 7  # One week for 30-min data

for col, desc in key_metrics[:2]:
    plt.figure(figsize=(14, 8))

    # Original series
    plt.subplot(3, 1, 1)
    plt.plot(df.index, df[col], "b-", alpha=0.5, linewidth=0.5, label="Dati originali")
    plt.title(f"Decomposizione Serie Temporale: {desc[:60]}...", fontsize=12)
    plt.ylabel("Valore")
    plt.legend()

    # Trend (moving average)
    plt.subplot(3, 1, 2)
    trend = df[col].rolling(window=window_size, center=True).mean()
    plt.plot(
        df.index, trend, "r-", linewidth=2, label=f"Trend (MA {window_size} periodi)"
    )
    plt.ylabel("Trend")
    plt.legend()

    # Residuals
    plt.subplot(3, 1, 3)
    residuals = df[col] - trend
    plt.plot(df.index, residuals, "g-", alpha=0.7, linewidth=0.5, label="Residui")
    plt.ylabel("Residui")
    plt.xlabel("Data")
    plt.legend()

    plt.tight_layout()
    # Sanitize filename
    safe_col = col.replace("/", "_").replace(" ", "_").replace(".", "_")
    filename = f"decomposition_{safe_col}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"✓ Decomposizione salvata in '{filename}'")

# 5. Basic Stationarity Analysis
print("\n--- Analisi di Stazionarietà ---")
print("Test semplificato basato su statistiche rolling:")

for col, desc in key_metrics[:3]:
    # Split data into quarters
    n_quarters = 4
    quarter_size = len(df) // n_quarters

    means = []
    stds = []

    for i in range(n_quarters):
        start_idx = i * quarter_size
        end_idx = (i + 1) * quarter_size if i < n_quarters - 1 else len(df)
        quarter_data = df[col].iloc[start_idx:end_idx]
        means.append(quarter_data.mean())
        stds.append(quarter_data.std())

    # Check if mean and std are relatively constant
    mean_cv = np.std(means) / np.mean(means)  # Coefficient of variation
    std_cv = np.std(stds) / np.mean(stds)

    print(f"\n{desc[:50]}:")
    print(f"  Variazione della media: {mean_cv:.3f} (< 0.1 suggerisce stazionarietà)")
    print(f"  Variazione della deviazione standard: {std_cv:.3f}")
    print(
        f"  Stazionarietà probabile: {'Sì' if mean_cv < 0.1 and std_cv < 0.2 else 'No'}"
    )

# Save analysis results
analysis_results = {
    "key_metrics": [(col, desc) for col, desc in key_metrics],
    "high_correlations": high_corr,
    "hourly_patterns": hourly_patterns.to_dict(),
    "column_mapping": column_mapping,
}

with open("eda_results.json", "w") as f:
    json.dump(analysis_results, f, indent=2, default=str)

print("\n✓ FASE 2 COMPLETATA")
print("\nRisultati chiave dell'EDA:")
print("- Identificate pattern orarie nei dati")
print("- Analizzate correlazioni tra variabili")
print("- Eseguita decomposizione base delle serie temporali")
print("- Verificata stazionarietà delle serie principali")
