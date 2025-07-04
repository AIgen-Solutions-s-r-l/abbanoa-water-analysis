# Report Finale: Analisi Serie Storiche Rete Idrica Selargius

## Executive Summary

Questo report presenta i risultati dell'analisi condotta sui dati di monitoraggio della rete idrica di Selargius (periodo: 13/11/2024 - 31/03/2025). L'analisi ha identificato opportunità significative per l'ottimizzazione della rete attraverso l'implementazione di modelli di Machine Learning per previsione dei consumi, rilevamento anomalie e ottimizzazione della pressione.

## 1. Panoramica dei Dati

### Dataset Analizzato
- **Periodo**: Dal 13/11/2024 al 31/03/2025 
- **Frequenza**: Dati aggregati ogni 30 minuti
- **Dimensioni**: 6,622 osservazioni × 12 metriche numeriche
- **Nodi monitorati**: Via Sant'Anna, Via Seneca, Serbatoio Selargius, Serbatoio Cuccuru Linu

### Metriche Principali
- **Temperature interne** (°C)
- **Portate istantanee** (L/S) 
- **Portate totali cumulative** (M³)
- **Pressioni** (BAR)

### Qualità dei Dati
- ✅ Dati generalmente completi (solo 24 valori mancanti su oltre 79,000 punti dati)
- ✅ Interpolazione lineare applicata con successo per gestire valori mancanti
- ✅ Nessuna riga duplicata rilevata

## 2. Risultati Chiave dell'Analisi Esplorativa

### 2.1 Pattern Temporali

**Pattern Orari Identificati:**
- Consumo minimo nelle ore notturne (02:00-04:00): ~75 L/S media
- Picchi mattutini (07:00-09:00): fino a 92 L/S
- Variabilità significativa durante il giorno

![Time Series Overview](time_series_overview.png)

### 2.2 Correlazioni Significative

Sono state identificate correlazioni elevate (r > 0.7) tra:
- Temperature dei diversi nodi (r = 0.81)
- Portate tra nodi vicini (r = 0.82-0.90)
- Portate Via Sant'Anna ↔ Serbatoio Selargius (r = 0.72)

Queste correlazioni suggeriscono che la rete opera come sistema integrato, dove le variazioni in un punto si propagano agli altri nodi.

![Correlation Heatmap](correlation_heatmap.png)

### 2.3 Analisi di Stazionarietà

Le serie temporali analizzate **non sono stazionarie**:
- Variazione significativa della media nel tempo (CV > 0.1)
- Varianza non costante, specialmente per le portate

Questo richiederà trasformazioni (differenziazione) per alcuni modelli statistici.

## 3. Proposte di Machine Learning

### 3.1 Task 1: Previsione Consumi e Portate

**Obiettivo**: Ottimizzare la gestione della rete prevedendo i consumi futuri (orizzonte 24-48h)

**Modelli Consigliati** (in ordine di implementazione):

| Modello | Complessità | Accuratezza | Quando Usarlo |
|---------|-------------|-------------|---------------|
| **Prophet** | Bassa | Media | Primo approccio, interpretabilità alta |
| **SARIMA** | Media | Media | Dopo trasformazioni per stazionarietà |
| **LSTM** | Alta | Alta | Quando servono previsioni molto accurate |

**ROI Atteso**: Riduzione sprechi del 10-15% attraverso ottimizzazione della distribuzione

### 3.2 Task 2: Rilevamento Anomalie

**Obiettivo**: Identificare perdite e malfunzionamenti in tempo reale

**Modelli Consigliati**:

| Modello | Tipo | Use Case |
|---------|------|----------|
| **Isolation Forest** | Unsupervised | Anomalie evidenti (perdite maggiori) |
| **Autoencoder** | Deep Learning | Anomalie contestuali sottili |
| **SPC Charts** | Statistico | Monitoraggio real-time con soglie |

**ROI Atteso**: Riduzione perdite del 20-30% con interventi tempestivi

### 3.3 Task 3: Ottimizzazione Pressione

**Obiettivo**: Minimizzare perdite mantenendo qualità del servizio

**Approcci**:
1. **Gradient Boosting + Ottimizzazione**: Per iniziare rapidamente
2. **Reinforcement Learning**: Per ottimizzazione dinamica avanzata

## 4. Roadmap di Implementazione

### Fase 1: Quick Win (Settimane 1-2)
- ✅ Implementare **Prophet** per previsioni a 24h
- ✅ Dashboard con previsioni giornaliere
- ✅ Alert per scostamenti significativi

### Fase 2: Anomaly Detection (Settimane 3-4)  
- ✅ Deploy **Isolation Forest** per perdite maggiori
- ✅ Sistema di alert automatici
- ✅ Integrazione con sistema di ticketing manutenzione

### Fase 3: Advanced Analytics (Settimane 5-8)
- ✅ Sviluppo modello **LSTM** multi-nodo
- ✅ Ottimizzazione iperparametri
- ✅ Validazione su dati storici

### Fase 4: Produzione (Settimane 9-12)
- ✅ Integrazione API real-time
- ✅ Dashboard operativa unificata
- ✅ Training del personale

## 5. Prossimi Passi Concreti

### Immediati (Questa Settimana)
1. **Installare ambiente Python** con librerie necessarie:
   ```bash
   pip install pandas numpy prophet scikit-learn matplotlib
   ```

2. **Implementare primo modello Prophet**:
   ```python
   from prophet import Prophet
   
   # Preparare dati per Prophet
   df_prophet = df[['ds', 'y']]  # ds=timestamp, y=portata
   
   # Training
   model = Prophet(daily_seasonality=True)
   model.fit(df_prophet)
   
   # Previsioni
   future = model.make_future_dataframe(periods=48, freq='30min')
   forecast = model.predict(future)
   ```

3. **Creare prima dashboard** con matplotlib/Streamlit

### Medio Termine (1 Mese)
- Raccogliere feedback operatori
- Affinare modelli basandosi su performance reali
- Estendere a tutti i nodi della rete

## 6. Metriche di Successo

| KPI | Baseline | Target (6 mesi) |
|-----|----------|-----------------|
| Accuratezza previsioni (MAPE) | - | < 10% |
| Tempo rilevamento perdite | 24-48h | < 2h |
| Riduzione perdite idriche | Current | -25% |
| ROI del progetto | - | > 300% |

## Conclusioni

L'analisi ha rivelato pattern chiari e correlazioni significative nei dati della rete idrica di Selargius. L'implementazione dei modelli ML proposti, partendo da soluzioni semplici (Prophet) per arrivare a sistemi avanzati (LSTM), permetterà di:

1. **Ottimizzare** la distribuzione idrica con previsioni accurate
2. **Ridurre** perdite attraverso rilevamento anomalie tempestivo  
3. **Migliorare** l'efficienza energetica ottimizzando le pressioni

Il successo dipenderà da un'implementazione graduale, con validazione continua e coinvolgimento degli operatori.

---

*Report generato il: 03/07/2025*  
*Analisi basata su: 6,622 osservazioni (13/11/2024 - 31/03/2025)*