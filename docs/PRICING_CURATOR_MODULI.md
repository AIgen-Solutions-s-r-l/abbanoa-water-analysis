# Pricing Curator - Struttura Modulare

## Piattaforma Modulare per Gestione Reti Idriche

**Data**: 2025-10-02
**Prodotto**: Curator by Abbanoa Analytics
**Modello**: Pay-per-module SaaS

---

## 1. Mapping Funzionalità su Moduli

### 📦 MODULO BASE - "Curator Foundation"

**Incluso**:

✅ **Piattaforma in Cloud**
- Hosting GCP/cloud managed
- Uptime 99.5%
- Backup automatici giornalieri
- SSL/TLS security

✅ **Integrazioni, Ingestione dei Dati**
- API REST per import dati
- ETL pipeline BigQuery ↔ PostgreSQL
- Connettori standard (CSV, JSON, SQL)
- Supporto SCADA integration
- Time-series database (TimescaleDB)

✅ **Mappatura della Rete Idrica**
- Visualizzazione topologia rete (mappe interattive Leaflet)
- Gestione nodi e connessioni
- Geolocalizzazione elementi rete
- Layer infrastrutturale

✅ **Analisi e Monitoraggio Base**
- Dashboard real-time
- Monitoring sensori (flow, pressure, temperature)
- KPI base (perdite, consumi, efficienza)
- Report standard
- Alerting base (soglie statiche)

✅ **Modelli Predittivi Base per Operations**
- **Domanda**: Forecast consumi (7 giorni)
- **Pressione**: Monitoraggio pressione zone
- **Portata**: Analisi portate istantanee
- **Costi di esercizio**: Dashboard costi operativi
- **Consumi energetici**: Monitoring energia base
- **Performance tecnico-economica**: KPI dashboard

**Features Tecniche Mappate**:
```
Backend:
- dashboard_router.py (core KPIs)
- infrastructure_router.py (network topology)
- network_topology_router.py (mapping)
- nodes_router.py (nodes management)
- pressure_router.py (pressure monitoring)
- consumption_analytics_router.py (basic analytics)
- reports_router.py (standard reports)

Frontend:
- /infrastructure (network management)
- /infrastructure-map (topology visualization)
- /monitoring (real-time dashboard)
- /consumption (basic consumption analytics)
- /analytics (basic analytics)
```

**Limiti Modulo Base**:
- No anomaly detection avanzata
- No ML-based forecasting (solo statistical)
- No causa-effetto analysis
- No efficientamento energetico
- No correlazioni esterne

---

### 🔬 MODULO AVANZATO - "Curator Intelligence"

**Richiede**: MODULO BASE (add-on)

✅ **Supporto alla Decisione**

**Anomaly Detection (ML-powered)**:
- Algoritmi machine learning per rilevamento anomalie
- Pattern recognition su consumi, portate, pressioni
- Scoring anomalie (severity, probability)
- Alert intelligenti (riduzione falsi positivi)
- Root cause analysis

**Elaborazione Modelli Comportamentali Attesi**:
- Profili di consumo per tipologia utente
- Baseline comportamentale per nodo/zona
- Seasonal patterns e trend analysis
- Predictive maintenance scheduling

**Divergenza Comportamentale (ML + Algoritmi)**:
- Confronto real-time vs atteso
- Drift detection (scostamenti graduali)
- Anomaly timeline & tracking
- Prediction tracking (accuracy analysis)

✅ **Analisi Causa-Effetto**

**Matrici di Correlazione**:
- Cross-correlation tra eventi operations
- Dependency graph elementi rete
- Impact analysis (cascading effects)
- Time-lagged correlations
- Network effect modeling

**Features Tecniche Mappate**:
```
Backend:
- anomaly_router.py (anomaly detection)
- anomaly_predictions.py (ML predictions)
- prediction_tracking.py (tracking accuracy)
- predictions.py (ML models)
- efficiency_router.py (efficiency analysis)
- forecast_endpoint.py (advanced forecasting)

Frontend:
- /anomalies (anomaly detection dashboard)
- /predictions (ML predictions)
- /enhanced-overview (advanced analytics)

ML/Processing:
- src/processing/service/ml_manager.py
- src/application/services/anomaly_predictor.py
```

**Valore Aggiunto**:
- Riduzione perdite 10-15% (anomaly detection precoce)
- Riduzione falsi allarmi 60-70%
- Manutenzione predittiva (risparmio 20-30%)
- Ottimizzazione operations

---

### 🚀 MODULO PREMIUM - "Curator Optimize"

**Richiede**: MODULO BASE + MODULO AVANZATO (add-on)

✅ **Efficientamento Energetico**

**Algoritmi di Efficientamento**:
- Ottimizzazione consumi pompe
- Load balancing energetico
- Peak shaving algorithms
- Energy cost optimization

**Inerzia Meccanica della Rete**:
- Modellazione comportamento idraulico
- Simulazione scenari operativi
- Transient analysis (water hammer)
- Pressure wave propagation

**Programmazione Intelligente**:
- Scheduling ottimizzato pompe/valvole
- Algoritmi genetici per ottimizzazione
- Multi-objective optimization (energia vs QoS)
- Scenario planning & simulation

**Telegestione su Base Algoritmi**:
- Controllo remoto automatizzato
- Rule engine avanzato
- Adaptive control systems
- Integration con sistemi SCADA/PLC

✅ **Correlazione con Fonti Dati Esterne**

**Agricoltura**:
- Dati irrigazione (fabbisogni stagionali)
- Calendari colture
- Correlazione consumi agricoli

**Meteorologia**:
- Previsioni meteo (temperatura, precipitazioni)
- Correlazione consumi vs meteo
- Impact forecasting eventi meteo

**Dati Socio-Demografici**:
- Demografia territorio
- Eventi speciali (fiere, concerti)
- Turismo stagionale
- Pattern di crescita urbana

**Attività Industriali**:
- Cicli produttivi industrie
- Consumi industriali
- Shutdown/maintenance schedules

**Attività Commerciali**:
- Stagionalità commerciale
- Orari apertura/chiusura
- Eventi promozionali

**Features Tecniche Mappate**:
```
Backend:
- efficiency_router.py (full features)
- weather_router.py (meteo integration)
- optimization algorithms (custom development)
- external data connectors (API integrations)

Frontend:
- /energy-optimization (energy dashboard)
- /weather (weather correlations)
- External data dashboards (custom)

Processing:
- Advanced optimization algorithms
- Multi-source data fusion
- Real-time control systems
```

**Valore Aggiunto**:
- Riduzione costi energia 15-25%
- Ottimizzazione QoS (riduzione interruzioni)
- Predictive planning
- Compliance ambientale

---

## 2. Pricing Strategy per Moduli

### 💰 Proposta Pricing

#### 📦 MODULO BASE - "Curator Foundation"

**Target**: Utilities piccole/medie, pilot projects

**Prezzo**: **€1,299/mese**

**Include**:
- Fino a 50 nodi monitorati
- Fino a 10 utenti
- 50 GB storage database
- 500k API calls/mese
- Dashboard standard
- Report base
- Supporto email (48h)
- Backup 7 giorni
- Uptime SLA 99.5%

**Pagamento annuale**: €13,990/anno (sconto 10% = €1,165/mese)

---

#### 🔬 MODULO AVANZATO - "Curator Intelligence"

**Target**: Utilities medie, focus efficienza operations

**Prezzo Base**: **€1,299/mese**
**+ Add-on Avanzato**: **+€1,200/mese**

**TOTALE**: **€2,499/mese** (BASE + AVANZATO)

**Include** (aggiuntivo a BASE):
- Anomaly detection ML
- Advanced forecasting (30 giorni)
- Causa-effetto analysis
- 100 GB storage totale
- 2M API calls/mese
- Custom dashboards (2 inclusi)
- Supporto prioritario (24h)
- Training (8 ore/anno)

**Pagamento annuale**: €26,990/anno (sconto 10% = €2,249/mese)

---

#### 🚀 MODULO PREMIUM - "Curator Optimize"

**Target**: Utilities grandi, multi-site, focus energy

**Prezzo Base**: €1,299/mese
**+ Add-on Avanzato**: €1,200/mese
**+ Add-on Premium**: **+€2,000/mese**

**TOTALE**: **€4,499/mese** (BASE + AVANZATO + PREMIUM)

**Include** (aggiuntivo a AVANZATO):
- Energy optimization algorithms
- Programmazione intelligente
- Telegestione automatizzata
- External data integrations (5 fonti)
- Unlimited nodi/utenti
- 500 GB storage
- Unlimited API calls
- Custom dashboards illimitati
- Supporto 24/7 (4h response)
- Training (20 ore/anno)
- Dedicated account manager
- White-label option
- Uptime SLA 99.9%

**Pagamento annuale**: €48,990/anno (sconto 10% = €4,082/mese)

---

### 📊 Tabella Comparativa Moduli

| Feature | BASE | AVANZATO | PREMIUM |
|---------|------|----------|---------|
| **Prezzo/mese** | €1,299 | €2,499 | €4,499 |
| **Nodi monitorati** | 50 | 150 | Illimitati |
| **Utenti** | 10 | 30 | Illimitati |
| **Storage DB** | 50 GB | 100 GB | 500 GB |
| **API calls/mese** | 500k | 2M | Illimitati |
| **Piattaforma Cloud** | ✅ | ✅ | ✅ |
| **Ingestione dati** | ✅ | ✅ | ✅ |
| **Mappatura rete** | ✅ | ✅ | ✅ |
| **Monitoring base** | ✅ | ✅ | ✅ |
| **Forecast base (7gg)** | ✅ | ✅ | ✅ |
| **KPI Operations** | ✅ | ✅ | ✅ |
| **Anomaly Detection ML** | ❌ | ✅ | ✅ |
| **Forecast avanzato (30gg)** | ❌ | ✅ | ✅ |
| **Causa-effetto** | ❌ | ✅ | ✅ |
| **Modelli comportamentali** | ❌ | ✅ | ✅ |
| **Energy optimization** | ❌ | ❌ | ✅ |
| **Programmazione intelligente** | ❌ | ❌ | ✅ |
| **Telegestione** | ❌ | ❌ | ✅ |
| **Dati esterni (meteo, etc)** | ❌ | ❌ | ✅ |
| **Supporto** | Email 48h | Email 24h | 24/7 4h |
| **Training** | - | 8h/anno | 20h/anno |
| **SLA Uptime** | 99.5% | 99.7% | 99.9% |
| **Account Manager** | ❌ | ❌ | ✅ |

---

## 3. Analisi Costi vs Pricing

### 💸 Costo Gestione per Cliente

**Costi Medi per Cliente** (20 clienti scenario):
```
Infrastruttura: €700/20 = €35/cliente
Personale: €20,000/20 = €1,000/cliente
Tools: €300/20 = €15/cliente
──────────────────────────────────────
TOTALE: €1,050/cliente/mese
```

**Margini per Modulo**:

| Modulo | Prezzo | Costo | Margine € | Margine % |
|--------|--------|-------|-----------|-----------|
| BASE | €1,299 | €1,050 | €249 | 19% |
| AVANZATO | €2,499 | €1,200 | €1,299 | 52% |
| PREMIUM | €4,499 | €1,500 | €2,999 | 67% |

**Note**:
- Modulo BASE ha margine basso (19%) → **loss leader** per acquisizione
- Modulo AVANZATO margine sano (52%) → **sweet spot**
- Modulo PREMIUM margine alto (67%) → **premium positioning**

---

## 4. Strategia Go-to-Market

### 🎯 Positioning

**MODULO BASE**:
- **Positioning**: Entry-level, pilot project
- **Target**: Utilities 5-20k abitanti, water districts
- **Sales pitch**: "Digitalizza la tua rete in giorni, non anni"
- **Upsell path**: Dopo 6 mesi → Avanzato

**MODULO AVANZATO**:
- **Positioning**: Production-grade, AI-powered
- **Target**: Utilities 20-100k abitanti, multi-site
- **Sales pitch**: "Riduci perdite del 15% con AI"
- **Upsell path**: Dopo 12 mesi → Premium

**MODULO PREMIUM**:
- **Positioning**: Enterprise, full optimization
- **Target**: Utilities >100k abitanti, holding multi-utility
- **Sales pitch**: "Risparmia 20% energia, compliance ESG"
- **Differentiator**: Telegestione + external data

---

### 📈 Revenue Scenarios (20 clienti)

**Mix Conservativo** (50% BASE, 40% AVANZATO, 10% PREMIUM):
```
10 clienti BASE: 10 × €1,299 = €12,990
8 clienti AVANZATO: 8 × €2,499 = €19,992
2 clienti PREMIUM: 2 × €4,499 = €8,998
───────────────────────────────────────────
TOTALE REVENUE: €41,980/mese
Costi: €23,000/mese
Profitto: €18,980/mese (45% margin)
```

**Mix Ottimistico** (20% BASE, 60% AVANZATO, 20% PREMIUM):
```
4 clienti BASE: 4 × €1,299 = €5,196
12 clienti AVANZATO: 12 × €2,499 = €29,988
4 clienti PREMIUM: 4 × €4,499 = €17,996
───────────────────────────────────────────
TOTALE REVENUE: €53,180/mese
Costi: €23,000/mese
Profitto: €30,180/mese (57% margin)
```

---

## 5. Add-ons & Upsells

### 💼 Servizi Aggiuntivi (tutti i moduli)

**Nodi Extra**:
- BASE: +50 nodi = +€300/mese
- AVANZATO: +50 nodi = +€400/mese
- PREMIUM: incluso (illimitato)

**Storage Extra**:
- +50 GB = +€50/mese
- +100 GB = +€80/mese

**Utenti Extra**:
- +10 utenti = +€100/mese

**Custom Development**:
- Tariffa oraria: €120/h
- Pacchetto 40 ore: €4,500 (sconto 6%)
- Pacchetto 100 ore: €10,500 (sconto 13%)

**Custom Integration** (una tantum):
- SCADA/PLC integration: €3,000-5,000
- ERP integration: €2,500-4,000
- External API integration: €1,500-3,000

**Training**:
- On-site training (1 giorno): €1,500
- Remote training (4 ore): €800

**White-Label** (PREMIUM only):
- Setup fee: €5,000 (una tantum)
- Monthly fee: +€500/mese

**Multi-Site Discount**:
- 2-3 siti: 15% sconto dal secondo sito
- 4+ siti: 20% sconto dal terzo sito

---

## 6. Bundle Packages (Alternative)

### 🎁 Pacchetti Pre-Configurati

#### Package "Starter" (6 mesi)
```
MODULO BASE × 6 mesi
Prezzo: €7,000 (invece di €7,794)
Include: Setup, training 4h, 1 custom dashboard
Risparmio: 10% + setup gratis
```

#### Package "Growth" (12 mesi)
```
MODULO AVANZATO × 12 mesi
Prezzo: €27,000 (invece di €29,988)
Include: Setup, training 16h, 3 custom dashboards, 1 integration
Risparmio: 10% + €5k valore aggiunto
```

#### Package "Enterprise" (24 mesi)
```
MODULO PREMIUM × 24 mesi
Prezzo: €98,000 (invece di €107,976)
Include: Setup, training 40h, dashboards illimitati, 5 integrations, dedicated CSM
Risparmio: 9% + €15k valore aggiunto
```

---

## 7. Confronto con Sviluppo Custom

### 💡 Value Proposition per Cliente

**Per ottenere MODULO BASE custom**:
- Costo sviluppo: €120,000-150,000
- Timeline: 6-9 mesi
- Rischio: Alto
- **Con Curator**: €1,299/mese, disponibile subito
- **ROI**: 77 mesi (6.4 anni) payback vs custom

**Per ottenere MODULO AVANZATO custom**:
- Costo sviluppo: €250,000-300,000
- Timeline: 12-15 mesi
- **Con Curator**: €2,499/mese
- **ROI**: 100 mesi (8.3 anni) payback vs custom

**Per ottenere MODULO PREMIUM custom**:
- Costo sviluppo: €400,000-500,000
- Timeline: 18-24 mesi
- **Con Curator**: €4,499/mese
- **ROI**: 89 mesi (7.4 anni) payback vs custom

---

## 8. Strategia Pricing Flessibile

### 🔀 Modello "Pay-As-You-Grow"

**Alternative al pricing fisso**:

#### Opzione A: Pricing a Consumo
```
BASE: €999/mese base + variabile
  + €10/nodo/mese (oltre 20 inclusi)
  + €5/utente/mese (oltre 5 inclusi)
  + €1/GB storage/mese (oltre 20 GB)

AVANZATO: €1,999/mese base + variabile
  + €8/nodo/mese (oltre 50 inclusi)
  + €3/utente/mese (oltre 10 inclusi)

PREMIUM: €3,499/mese base (tutto illimitato)
```

#### Opzione B: Tier-Based (utility size)

| Utility Size | BASE | AVANZATO | PREMIUM |
|--------------|------|----------|---------|
| **Small** (<10k abitanti) | €899/mese | €1,799/mese | €3,299/mese |
| **Medium** (10-50k) | €1,299/mese | €2,499/mese | €4,499/mese |
| **Large** (50-200k) | €1,799/mese | €3,499/mese | €5,999/mese |
| **Enterprise** (>200k) | €2,499/mese | €4,999/mese | €8,999/mese |

---

## 9. Raccomandazioni Finali

### ✅ Pricing Consigliato (Launch)

**MODULO BASE**: **€1,299/mese**
- Competitivo vs mercato
- Margine sufficiente (19% a 20 clienti)
- Psicologicamente sotto €1,500
- Upsell facile (+€1,200 per Avanzato)

**MODULO AVANZATO**: **€2,499/mese**
- Sweet spot value/prezzo
- Margine sano (52%)
- Differenziatore ML/AI
- Under €2,500 psicologico

**MODULO PREMIUM**: **€4,499/mese**
- Premium positioning
- Margine alto (67%)
- Sotto €5k psicologico
- Enterprise features giustificano prezzo

### 🎯 Go-to-Market Priority

**Fase 1** (Mesi 1-6): Focus MODULO BASE
- Target: 10-15 clienti BASE
- Pricing aggressivo: €999/mese (early adopter -23%)
- Obiettivo: traction + case studies

**Fase 2** (Mesi 7-12): Upsell MODULO AVANZATO
- Convertire BASE → AVANZATO (target 50%)
- Acquisire 5-10 nuovi AVANZATO
- Pricing standard: €1,299 BASE, €2,499 AVANZATO

**Fase 3** (Mesi 13+): Launch MODULO PREMIUM
- Target: 2-5 clienti enterprise PREMIUM
- Focus su utilities >100k abitanti
- Full pricing: €4,499/mese

---

### 📊 Target Revenue Anno 1

**Conservativo**:
```
Q1: 3 clienti BASE @ €999 = €2,997/mese
Q2: 8 clienti BASE @ €1,299 = €10,392/mese
Q3: 12 clienti (8 BASE + 4 AVZ) = €20,388/mese
Q4: 18 clienti (6 BASE + 11 AVZ + 1 PREM) = €37,281/mese

Revenue Anno 1: €214,188
Costi Anno 1: €138,000 (team minimo)
Profitto Anno 1: €76,188 (36% margin)
```

**Ottimistico**:
```
Q4 Anno 1: 30 clienti (5 BASE + 20 AVZ + 5 PREM) = €78,985/mese

Revenue Anno 1: €380,000
Profitto Anno 1: €152,000 (40% margin)
```

---

**Prossimi Step**:
1. Validare pricing con 3-5 potenziali clienti (interviews)
2. Preparare materiale commerciale (pitch deck, demo)
3. Configurare billing system (Stripe/Chargebee)
4. Setup onboarding flow per moduli
5. Definire upsell automation (BASE → AVANZATO a 6 mesi)

---

**Documento per**: Sales Team / Commercial Strategy
**Versione**: 1.0.0
