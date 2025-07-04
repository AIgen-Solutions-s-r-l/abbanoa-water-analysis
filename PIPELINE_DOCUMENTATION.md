# Pipeline di Ingestion Dati per BigQuery

## Overview

Abbiamo creato un sistema completo per normalizzare e caricare dati CSV di infrastrutture idriche in BigQuery. Il sistema è progettato per essere:

- **Generico**: Gestisce qualsiasi formato CSV con header multipli
- **Scalabile**: Pronto per BigQuery con partitioning e clustering
- **Validato**: Include controlli di qualità dei dati
- **Automatizzabile**: Può essere schedulato con Cloud Scheduler/Airflow

## Componenti Principali

### 1. **Data Normalizer** (`data_normalizer.py`)

Normalizza i CSV con strutture complesse:
- Gestisce header multipli (nomi colonne + unità di misura)
- Converte nomi colonne per compatibilità BigQuery
- Crea timestamp unificati da colonne data/ora separate
- Calcola metriche di qualità dei dati

```python
# Utilizzo
normalizer = WaterDataNormalizer()
df, metadata = normalizer.normalize_data("file.csv")
```

### 2. **BigQuery Pipeline** (`bigquery_pipeline.py`)

Orchestratore per il caricamento in BigQuery:
- Crea dataset e tabelle automaticamente
- Gestisce schema versioning
- Supporta dry-run per testing
- Genera comandi CLI alternativi

```python
# Utilizzo
pipeline = BigQueryPipeline("project-id")
results = pipeline.run_pipeline(["file1.csv", "file2.csv"])
```

### 3. **Schema BigQuery**

Schema ottimizzato per time series:
```json
{
  "name": "timestamp",
  "type": "TIMESTAMP",
  "mode": "REQUIRED"
},
{
  "name": "selargius_nodo_via_sant_anna_portata_w_istantanea_diretta",
  "type": "FLOAT64",
  "mode": "NULLABLE",
  "description": "Portata istantanea (L/S)"
}
```

## Setup Completo

### 1. Preparazione Ambiente

```bash
# Installa dipendenze
pip install pandas google-cloud-bigquery

# Autenticazione Google Cloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Prima Esecuzione

```bash
# 1. Normalizza i dati
python3 data_normalizer.py

# 2. Verifica il risultato
head -20 normalized_data.csv

# 3. Esegui pipeline (dry-run)
python3 bigquery_pipeline.py
```

### 3. Caricamento in BigQuery

```bash
# Opzione A: Usa i comandi generati
bash bigquery_commands.sh

# Opzione B: Usa Python (modifica PROJECT_ID nel codice)
python3 bigquery_pipeline.py --no-dry-run
```

## Struttura Dati Normalizzata

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| timestamp | TIMESTAMP | Data/ora misurazione |
| metric_3 | FLOAT64 | Portata istantanea (L/S) |
| metric_4 | FLOAT64 | Portata totale (M³) |
| metric_5 | FLOAT64 | Pressione (BAR) |
| _ingestion_timestamp | TIMESTAMP | Quando caricato |
| _source_file | STRING | File origine |
| _row_hash | INT64 | Hash per deduplicazione |

## Query di Monitoraggio

### Verifica Freschezza Dati
```sql
SELECT 
  MAX(timestamp) as latest_data,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(timestamp), MINUTE) as minutes_behind
FROM `project.water_infrastructure.sensor_data`
```

### Rilevamento Anomalie
```sql
-- Query completa in bigquery_monitoring_queries.sql
-- Identifica valori fuori 3 deviazioni standard
```

## Automazione

### Cloud Scheduler (Giornaliero)
```yaml
schedule: "0 6 * * *"  # Ogni giorno alle 6:00
target:
  uri: https://your-cloud-function-url
  httpMethod: POST
  body:
    files: ["gs://bucket/new-files/*.csv"]
```

### Cloud Function
```python
def process_new_files(request):
    pipeline = BigQueryPipeline(PROJECT_ID)
    files = request.json['files']
    results = pipeline.run_pipeline(files)
    return results
```

## Prossimi Passi

1. **Configurare PROJECT_ID** nei file
2. **Testare con dati reali** in BigQuery
3. **Aggiungere monitoring** con Cloud Monitoring
4. **Schedulare ingestion** giornaliera
5. **Connettere a dashboard** (Data Studio/Looker)

## File Generati

- `normalized_data.csv` - Dati pronti per BigQuery
- `bigquery_schema.json` - Schema tabella
- `bigquery_commands.sh` - Comandi CLI per setup
- `bigquery_monitoring_queries.sql` - Query utili
- `normalization_metadata.json` - Report qualità dati

## Troubleshooting

### Errore: "Invalid column name"
- I nomi colonne vengono normalizzati (solo lettere/numeri/underscore)
- Controlla `column_mapping` in metadata per mappatura originale

### Errore: "Timestamp parsing failed"
- Verifica formato data/ora nel config
- Default: `DD/MM/YYYY HH:MM:SS`

### Dati mancanti dopo caricamento
- Controlla `validation.quality_score` nel metadata
- Valori < 50% indicano molti dati mancanti

## Contatti e Support

Per assistenza o miglioramenti, aprire issue su GitHub o contattare il team data engineering.