import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

print("=== PROTOTIPO PROPHET PER PREVISIONE PORTATE ===\n")

# Carica i dati puliti
df = pd.read_csv('cleaned_data.csv', sep=';', decimal=',', index_col=0, parse_dates=True)

# Carica mapping colonne
with open('eda_results.json', 'r') as f:
    eda_results = json.load(f)
    column_mapping = eda_results['column_mapping']

# Seleziona la colonna portata principale (L/S)
portata_col = 'L/S'  # Prima colonna portata
print(f"Colonna selezionata: {column_mapping[portata_col]}")

# Prepara dati per Prophet (formato richiesto: ds, y)
df_prophet = pd.DataFrame()
df_prophet['ds'] = df.index
df_prophet['y'] = df[portata_col].values

# Rimuovi eventuali NaN
df_prophet = df_prophet.dropna()

print(f"\nDati preparati: {len(df_prophet)} osservazioni")
print(f"Periodo: {df_prophet['ds'].min()} - {df_prophet['ds'].max()}")

# Dividi in train/test (ultimi 7 giorni per test)
split_date = df_prophet['ds'].max() - timedelta(days=7)
train = df_prophet[df_prophet['ds'] <= split_date]
test = df_prophet[df_prophet['ds'] > split_date]

print(f"\nTrain set: {len(train)} osservazioni")
print(f"Test set: {len(test)} osservazioni")

# Verifica se Prophet è disponibile
try:
    from prophet import Prophet
    
    print("\n⚠️  Prophet disponibile! Decommentare il codice sotto per eseguire:")
    print("""
    # Crea e addestra il modello
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=False,  # Non abbiamo un anno completo
        changepoint_prior_scale=0.05  # Più conservativo sui cambiamenti di trend
    )
    
    # Aggiungi regressori extra se necessario (es. temperatura)
    # model.add_regressor('temperature')
    
    # Training
    model.fit(train)
    
    # Crea dataframe per previsioni (48h nel futuro)
    future = model.make_future_dataframe(periods=48*2, freq='30min')
    
    # Genera previsioni
    forecast = model.predict(future)
    
    # Calcola metriche sul test set
    test_forecast = forecast[forecast['ds'].isin(test['ds'])]
    mae = np.mean(np.abs(test['y'].values - test_forecast['yhat'].values))
    mape = np.mean(np.abs((test['y'].values - test_forecast['yhat'].values) / test['y'].values)) * 100
    
    print(f"\\nPerformance sul test set:")
    print(f"MAE: {mae:.2f} L/S")
    print(f"MAPE: {mape:.2f}%")
    
    # Salva previsioni
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(48*2).to_csv('previsioni_48h.csv')
    
    # Visualizza
    fig1 = model.plot(forecast)
    fig1.savefig('prophet_forecast.png')
    
    fig2 = model.plot_components(forecast)
    fig2.savefig('prophet_components.png')
    """)
    
except ImportError:
    print("\n⚠️  Prophet non installato. Installare con:")
    print("pip install prophet")
    
# Analisi semplice senza Prophet
print("\n=== ANALISI ALTERNATIVA (senza Prophet) ===")

# Media mobile per trend
window = 48  # 24 ore
df_analysis = pd.DataFrame()
df_analysis['actual'] = df[portata_col]
df_analysis['trend'] = df[portata_col].rolling(window=window, center=True).mean()
df_analysis['daily_avg'] = df[portata_col].groupby([df.index.hour]).transform('mean')

# Calcola pattern orario medio
hourly_pattern = df.groupby(df.index.hour)[portata_col].agg(['mean', 'std'])
print("\nPattern orario medio:")
print(hourly_pattern)

# Identifica ore di picco
peak_hours = hourly_pattern.nlargest(3, 'mean').index.tolist()
print(f"\nOre di picco consumo: {peak_hours}")

# Calcola variazione weekend vs weekday
df['is_weekend'] = df.index.dayofweek >= 5
weekend_avg = df[df['is_weekend']][portata_col].mean()
weekday_avg = df[~df['is_weekend']][portata_col].mean()
print(f"\nMedia giorni feriali: {weekday_avg:.2f} L/S")
print(f"Media weekend: {weekend_avg:.2f} L/S")
print(f"Differenza: {(weekday_avg - weekend_avg)/weekday_avg * 100:.1f}%")

# Suggerimenti operativi
print("\n=== SUGGERIMENTI OPERATIVI ===")
print(f"1. Programmare manutenzioni nelle ore {hourly_pattern.nsmallest(3, 'mean').index.tolist()} (minimo consumo)")
print(f"2. Aumentare pressione/capacità nelle ore {peak_hours} (picco consumo)")
print(f"3. Considerare tariffe differenziate weekend (consumo -{(weekday_avg - weekend_avg)/weekday_avg * 100:.1f}%)")

# Salva risultati
results = {
    'hourly_pattern': hourly_pattern.to_dict(),
    'peak_hours': peak_hours,
    'weekend_reduction': (weekday_avg - weekend_avg)/weekday_avg * 100,
    'recommendations': [
        f"Manutenzioni ore: {hourly_pattern.nsmallest(3, 'mean').index.tolist()}",
        f"Rinforzo capacità ore: {peak_hours}",
        f"Ottimizzazione weekend: -{(weekday_avg - weekend_avg)/weekday_avg * 100:.1f}%"
    ]
}

with open('operational_insights.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print("\n✓ Analisi completata. Risultati salvati in 'operational_insights.json'")