import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

# Crea una dashboard semplice
print("Generazione Dashboard Operativa...")

df = pd.read_csv(
    "cleaned_data.csv", sep=";", decimal=",", index_col=0, parse_dates=True
)

# Carica insights
with open("operational_insights.json", "r") as f:
    insights = json.load(f)

# Crea figura con 4 subplot
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle("Dashboard Operativa - Rete Idrica Selargius", fontsize=16)

# 1. Ultimi 7 giorni di portata
last_week = df.index >= df.index[-1] - timedelta(days=7)
ax1.plot(df[last_week].index, df[last_week]["L/S"], "b-", linewidth=1)
ax1.set_title("Portata Ultima Settimana")
ax1.set_ylabel("Portata (L/S)")
ax1.grid(True, alpha=0.3)

# 2. Pattern orario medio
hourly_data = pd.DataFrame(insights["hourly_pattern"]["mean"], index=[0])
hours = list(range(24))
means = [insights["hourly_pattern"]["mean"][str(h)] for h in hours]
ax2.bar(hours, means, color="skyblue", edgecolor="navy")
ax2.set_title("Pattern Orario Medio")
ax2.set_xlabel("Ora del Giorno")
ax2.set_ylabel("Portata Media (L/S)")
ax2.axhline(y=sum(means) / len(means), color="r", linestyle="--", label="Media")

# 3. Alert zone - identifica valori anomali
threshold_high = df["L/S"].mean() + 2 * df["L/S"].std()
threshold_low = df["L/S"].mean() - 2 * df["L/S"].std()
recent_data = df[last_week]["L/S"]
anomalies = (recent_data > threshold_high) | (recent_data < threshold_low)

ax3.scatter(
    df[last_week].index,
    df[last_week]["L/S"],
    c=["red" if a else "green" for a in anomalies],
    s=10,
    alpha=0.6,
)
ax3.axhline(y=threshold_high, color="r", linestyle="--", label="Soglia Alta")
ax3.axhline(y=threshold_low, color="r", linestyle="--", label="Soglia Bassa")
ax3.set_title(f"Alert Anomalie (Trovate: {anomalies.sum()})")
ax3.set_ylabel("Portata (L/S)")
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Raccomandazioni operative
ax4.axis("off")
ax4.text(0.1, 0.9, "RACCOMANDAZIONI OPERATIVE", fontsize=14, fontweight="bold")
y_pos = 0.7
for i, rec in enumerate(insights["recommendations"], 1):
    ax4.text(0.1, y_pos - i * 0.15, f"{i}. {rec}", fontsize=11)

# Info box
info_text = f"Ultimo aggiornamento: {df.index[-1].strftime('%d/%m/%Y %H:%M')}"
ax4.text(0.1, 0.2, info_text, fontsize=10, style="italic")

plt.tight_layout()
plt.savefig("dashboard_operativa.png", dpi=150, bbox_inches="tight")
print("✓ Dashboard salvata in 'dashboard_operativa.png'")

# Genera report testuale
print("\n=== REPORT OPERATIVO GIORNALIERO ===")
print(f"Data: {datetime.now().strftime('%d/%m/%Y')}")
print(f"\nUltima lettura: {df.index[-1]}")
print(f"Portata attuale: {df['L/S'].iloc[-1]:.2f} L/S")
print("\nStatistiche ultime 24h:")
last_24h = df[df.index >= df.index[-1] - timedelta(hours=24)]
print(f"  - Media: {last_24h['L/S'].mean():.2f} L/S")
print(
    f"  - Massimo: {last_24h['L/S'].max():.2f} L/S alle {last_24h['L/S'].idxmax().strftime('%H:%M')}"
)
print(
    f"  - Minimo: {last_24h['L/S'].min():.2f} L/S alle {last_24h['L/S'].idxmin().strftime('%H:%M')}"
)

if anomalies.sum() > 0:
    print(
        f"\n⚠️  ATTENZIONE: Rilevate {anomalies.sum()} anomalie negli ultimi 7 giorni!"
    )
else:
    print("\n✅ Nessuna anomalia rilevata negli ultimi 7 giorni")
