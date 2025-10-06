# Costo Sviluppo Interno - Abbanoa Water Analysis

## Quanto ci è costato (o costerebbe) sviluppare questo software internamente

**Data**: 2025-10-02
**Versione**: 1.0.0
**Scopo**: Valutazione investimento interno per sviluppo software

---

## 1. Analisi Codebase Reale

### 1.1 Dimensioni Progetto

**Lines of Code**:
```
Backend (Python):           40,067 righe
Frontend (TypeScript/React): 21,482 righe
SQL (Database):             27,282 righe
Tests:                      ~8,000 righe
Configuration/Scripts:      ~1,000 righe
───────────────────────────────────────
TOTALE:                     ~98,000 righe
```

**Struttura**:
```
File totali:                754 files
Moduli Python:              196 files
Componenti React:           37 componenti
API endpoints:              17 routers (~80 endpoints)
Database tables:            ~30 tabelle
Test coverage:              68 test files
```

---

## 2. Stima Effort con COCOMO II

### 2.1 Calcolo COCOMO (Semi-Detached Project)

**Formula**:
```
Effort (Person-Months) = 3.0 × (KLOC)^1.12 × EAF

Dove:
- KLOC = 98 (migliaia di righe)
- EAF = 1.28 (effort adjustment factor)
```

**Calcolo**:
```
Effort = 3.0 × (98)^1.12 × 1.28
Effort = 3.0 × 153.2 × 1.28
Effort = 588 Person-Months
```

**Conversione**:
- **Person-Years**: 49 anni-persona
- **Person-Hours**: 94,080 ore

**Timeline**:
```
Duration = 2.5 × (588)^0.38
Duration = 30 mesi (2.5 anni)
```

**Team Size**:
```
Team = 588 / 30 = ~20 persone (media)
```

---

## 3. Breakdown Effort Realistico

### 3.1 Distribuzione per Fase

| Fase | Person-Months | % |
|------|---------------|---|
| Requirements & Design | 88 PM | 15% |
| Backend Development | 235 PM | 40% |
| Frontend Development | 147 PM | 25% |
| Database & Infrastructure | 59 PM | 10% |
| Testing & QA | 59 PM | 10% |
| **TOTALE** | **588 PM** | **100%** |

---

### 3.2 Breakdown per Componente

| Componente | Person-Months | Person-Days |
|------------|---------------|-------------|
| **Backend API (FastAPI)** | 150 PM | 3,000 giorni |
| **Frontend (Next.js)** | 120 PM | 2,400 giorni |
| **Database (PostgreSQL + TimescaleDB)** | 70 PM | 1,400 giorni |
| **ETL Pipeline (BigQuery)** | 60 PM | 1,200 giorni |
| **ML Models (Anomaly/Forecast)** | 50 PM | 1,000 giorni |
| **Authentication & Security** | 30 PM | 600 giorni |
| **DevOps & Infrastructure** | 25 PM | 500 giorni |
| **Testing & QA** | 50 PM | 1,000 giorni |
| **Documentation** | 20 PM | 400 giorni |
| **Project Management** | 13 PM | 260 giorni |
| **TOTALE** | **588 PM** | **11,760 giorni** |

---

## 4. Costi Personale Interno

### 4.1 Team Necessario

**Composizione Team Medio (20 persone)**:
```
1 Tech Lead / Architect       (RAL €70k)
3 Senior Backend Developers    (RAL €55k × 3)
2 Senior Frontend Developers   (RAL €55k × 2)
2 Mid-level Full-stack Devs    (RAL €45k × 2)
1 ML Engineer                  (RAL €60k)
1 DevOps Engineer              (RAL €55k)
1 Database Administrator       (RAL €50k)
3 Junior Developers            (RAL €35k × 3)
2 QA Engineers                 (RAL €40k × 2)
1 UX/UI Designer               (RAL €45k)
1 Product Manager              (RAL €60k)
1 Project Manager              (RAL €55k)
```

### 4.2 Costo Totale Annuo Team

| Ruolo | RAL | Costo Aziendale* | Quantità | Totale/Anno |
|-------|-----|------------------|----------|-------------|
| Tech Lead | €70,000 | €112,000 | 1 | €112,000 |
| Senior Backend | €55,000 | €88,000 | 3 | €264,000 |
| Senior Frontend | €55,000 | €88,000 | 2 | €176,000 |
| Mid Full-stack | €45,000 | €72,000 | 2 | €144,000 |
| ML Engineer | €60,000 | €96,000 | 1 | €96,000 |
| DevOps | €55,000 | €88,000 | 1 | €88,000 |
| DBA | €50,000 | €80,000 | 1 | €80,000 |
| Junior Devs | €35,000 | €56,000 | 3 | €168,000 |
| QA Engineers | €40,000 | €64,000 | 2 | €128,000 |
| UX/UI Designer | €45,000 | €72,000 | 1 | €72,000 |
| Product Manager | €60,000 | €96,000 | 1 | €96,000 |
| Project Manager | €55,000 | €88,000 | 1 | €88,000 |
| **TOTALE** | | | **20** | **€1,512,000/anno** |

*Costo aziendale = RAL × 1.6 (contributi INPS 30%, TFR 7%, benefit, overhead)

---

### 4.3 Costo Totale Progetto (30 mesi)

**Personale**:
```
€1,512,000/anno × 2.5 anni = €3,780,000
```

**Altri Costi**:
```
Infrastruttura sviluppo/staging:    €20,000 (2.5 anni)
Software licenses (IDE, tools):     €40,000 (JetBrains, GitHub, etc.)
Hardware (laptop, workstation):     €60,000 (€3k/persona)
Ufficio (affitto, utenze):          €150,000 (€500/mese/persona × 30 mesi)
Recruiting (onboarding team):       €80,000 (4 mesi stipendi search)
Training & conferenze:              €50,000
Contingency 10%:                    €419,000
──────────────────────────────────────────────────────────
TOTALE ALTRI COSTI:                 €819,000
```

**COSTO TOTALE SVILUPPO**: **€4,599,000**

**Arrotondato**: **~€4.6 milioni**

---

## 5. Scenari Alternativi

### 5.1 Scenario A: Team Ridotto (12 persone, 40 mesi)

**Composizione**:
```
1 Tech Lead
2 Senior Backend
1 Senior Frontend
2 Mid Full-stack
1 DevOps
2 Junior Devs
1 QA
1 Product Manager
1 Project Manager
```

**Costo Annuo**: €900,000
**Durata**: 40 mesi (3.3 anni)
**Costo Totale**: €900k × 3.3 + €600k altri = **€3,570,000**

---

### 5.2 Scenario B: Team Founder-Led (5-6 persone, 50+ mesi)

**Composizione**:
```
1 Founder/CTO (part-time, sweat equity)
2 Senior Full-stack Developers
1 Frontend Developer
1 DevOps
1 Junior Developer
```

**Costo Annuo**: €450,000
**Durata**: 50+ mesi (~4 anni)
**Costo Totale**: €450k × 4.2 + €300k altri = **€2,190,000**

**Note**: Assume founder lavora "gratis" (opportunity cost non contato)

---

### 5.3 Scenario C: Outsourcing Parziale (Hybrid)

**Team Core Italia** (6 persone):
```
1 Tech Lead
1 Senior Backend
1 Senior Frontend
1 DevOps
1 Product Manager
1 Project Manager
```
**Costo**: €540,000/anno

**Team Outsourced Eastern Europe** (10 persone):
```
3 Mid Backend Developers @ €40k
2 Frontend Developers @ €35k
3 Junior Developers @ €25k
2 QA Engineers @ €30k
```
**Costo**: €310,000/anno

**Totale Annuo**: €850,000
**Durata**: 30 mesi
**Costo Totale**: €850k × 2.5 + €500k altri = **€2,625,000**

---

## 6. Analisi Costi per Fase (Timeline Realistica)

### 6.1 Anno 1: Foundations (Mesi 1-12)

**Team**: 8 persone (ramp-up graduale)
```
Q1 (Mesi 1-3): 4 persone
  - 1 Tech Lead
  - 1 Senior Backend
  - 1 Senior Frontend
  - 1 Product Manager

Q2-Q4 (Mesi 4-12): 8 persone
  + 2 Mid Developers
  + 1 DevOps
  + 1 Junior Developer
```

**Deliverables**:
- Architecture design
- Database schema
- Backend API (core endpoints)
- Frontend (basic UI)
- Authentication
- MVP funzionante

**Costo Anno 1**: €600,000 (personale) + €200,000 (altri) = **€800,000**

---

### 6.2 Anno 2: Feature Development (Mesi 13-24)

**Team**: 15 persone (full team)

**Deliverables**:
- ETL pipeline completo
- ML models (anomaly detection)
- Dashboard avanzate
- Testing completo
- DevOps pipeline
- Documentation

**Costo Anno 2**: €1,125,000 (personale) + €350,000 (altri) = **€1,475,000**

---

### 6.3 Anno 3: Polish & Launch (Mesi 25-30)

**Team**: 20 persone (peak)

**Deliverables**:
- Performance optimization
- Security hardening
- User testing & feedback
- Production deployment
- Training materiali
- Monitoring setup

**Costo Anno 3** (6 mesi): €756,000 (personale) + €150,000 (altri) = **€906,000**

---

**TOTALE 30 MESI**: €800k + €1,475k + €906k = **€3,181,000**

*Nota: Questo è più basso di €4.6M perché assume ramp-up graduale team*

---

## 7. Costo "Reale" Considerando Opportunità

### 7.1 Opportunity Cost

**Se invece di sviluppare internamente comprassimo SaaS**:
```
Piano Enterprise: €4,499/mese × 30 mesi = €134,970
Custom development needed: €50,000
──────────────────────────────────────────────
TOTALE ALTERNATIVA: €184,970
```

**Opportunity Cost Sviluppo Interno**:
```
Costo sviluppo: €3,181,000
Costo alternativa SaaS: €184,970
──────────────────────────────────────────────
OPPORTUNITY COST: €2,996,030
```

**In altre parole**: Sviluppando internamente "perdiamo" €3M che potremmo investire altrove.

---

### 7.2 Rischio & Contingency Reale

**Statistiche Industria**:
- 68% progetti software sforano budget (media +27%)
- 50% progetti sforano timeline (media +44%)
- 17% progetti falliscono completamente

**Applicando statistiche**:
```
Costo base: €3,181,000
Budget overrun 27%: +€858,870
Timeline overrun 44%: 30 mesi → 43 mesi (+€650k)
──────────────────────────────────────────────
COSTO REALISTICO: €4,689,870
```

**Arrotondato**: **€4.7 milioni** (pessimistico ma realistico)

---

## 8. Costo di Manutenzione Post-Launch

### 8.1 Team Manutenzione (Anno 1 post-launch)

**Minimo**:
```
1 Senior Developer (bug fixes, minor features): €88,000
1 DevOps (monitoring, updates): €88,000
0.5 QA (testing): €32,000
0.5 Product Manager (roadmap): €48,000
──────────────────────────────────────────────
TOTALE: €256,000/anno
```

**Ottimale**:
```
2 Developers: €176,000
1 DevOps: €88,000
1 QA: €64,000
1 Product Manager: €96,000
──────────────────────────────────────────────
TOTALE: €424,000/anno
```

### 8.2 TCO 5 Anni (Total Cost of Ownership)

**Scenario Realistico**:
```
Sviluppo iniziale (30 mesi):     €4,690,000
Manutenzione Anno 1:              €424,000
Manutenzione Anno 2:              €424,000
Manutenzione Anno 3:              €424,000
Infrastruttura 5 anni:            €185,000 (GCP)
──────────────────────────────────────────────
TOTALE 5 ANNI:                    €6,147,000
```

**Arrotondato**: **€6.1 milioni** per 5 anni

---

## 9. Breakdown Costo per Feature Major

### 9.1 Stima Costo Singole Features

| Feature | Person-Months | Costo | % Totale |
|---------|---------------|-------|----------|
| **Dashboard Real-time** | 40 PM | €320,000 | 6.8% |
| **Anomaly Detection (ML)** | 50 PM | €400,000 | 8.5% |
| **Network Topology Map** | 35 PM | €280,000 | 6.0% |
| **Forecasting (ML)** | 45 PM | €360,000 | 7.7% |
| **Weather Integration** | 25 PM | €200,000 | 4.2% |
| **Consumption Analytics** | 40 PM | €320,000 | 6.8% |
| **Reports & Export** | 30 PM | €240,000 | 5.1% |
| **Multi-tenant Auth** | 35 PM | €280,000 | 6.0% |
| **ETL Pipeline** | 60 PM | €480,000 | 10.2% |
| **API REST (completo)** | 80 PM | €640,000 | 13.6% |
| **Infrastructure & DevOps** | 35 PM | €280,000 | 6.0% |
| **Testing & QA** | 50 PM | €400,000 | 8.5% |
| **Database Design** | 45 PM | €360,000 | 7.7% |
| **Monitoring & Logging** | 18 PM | €144,000 | 3.1% |
| **TOTALE** | **588 PM** | **€4,704,000** | **100%** |

*Costo = PM × €8,000/month (fully loaded cost per persona)

---

## 10. Valore del Software Sviluppato

### 10.1 Valutazione Asset Software

**Metodi di Valutazione**:

#### A. Cost-Based (Costo di Sviluppo)
```
Valore = Costo Sviluppo
Valore = €4,690,000
```

#### B. Market-Based (Confronto Mercato)
```
Prezzo mercato software custom simile: €6.5-8M
Valore Asset = €7,250,000 (media)
```

#### C. Income-Based (Flusso di Cassa Futuro)
```
Revenue Annuo Potenziale (30 clienti @ €2,000/mese): €720,000
Multiple SaaS tipico: 5-10x ARR
Valore = €720k × 7 = €5,040,000
```

#### D. Replacement Cost (Costo Riscrittura)
```
Costo riscrivere oggi: €4,690,000
Valore = €4,690,000
```

**Valutazione Conservativa**: **€4.5-5 milioni**
**Valutazione Ottimistica**: **€6-7 milioni**

---

## 11. ROI Sviluppo Interno vs Alternatives

### 11.1 Scenario A: Sviluppo Interno

**Investimento**: €4,690,000 (30 mesi)
**Manutenzione**: €424k/anno
**Proprietà**: 100% nostra
**Time-to-market**: 30 mesi

**Revenue Potenziale** (30 clienti @ €2k/mese):
```
Anno 1: €0 (sviluppo)
Anno 2: €240k (10 clienti da mese 18)
Anno 3: €720k (30 clienti full year)
Anno 4: €1,080k (45 clienti)
Anno 5: €1,440k (60 clienti)
──────────────────────────────────────
TOTALE 5 ANNI: €3,480k revenue
```

**Costi 5 Anni**: €6,147,000
**Revenue 5 Anni**: €3,480,000
**NET**: -€2,667,000 (perdita)
**Break-even**: Anno 7-8

---

### 11.2 Scenario B: Buy SaaS + Rebrand

**Investimento**: €62,000 (licenza white-label)
**Manutenzione**: €15k/anno
**Proprietà**: 0% (licenza d'uso)
**Time-to-market**: Immediato

**Revenue Potenziale**:
```
Anno 1: €720k (30 clienti da subito)
Anno 2: €1,080k (45 clienti)
Anno 3: €1,440k (60 clienti)
Anno 4: €1,800k (75 clienti)
Anno 5: €2,160k (90 clienti)
──────────────────────────────────────
TOTALE 5 ANNI: €7,200k revenue
```

**Costi 5 Anni**: €137,000 (licenza + manutenzione)
**Revenue 5 Anni**: €7,200,000
**NET**: +€7,063,000 (profitto)
**Break-even**: Mese 1

**Vantaggio vs Scenario A**: +€9,730,000 su 5 anni

---

### 11.3 Scenario C: Hybrid (White-Label + Custom Features)

**Investimento**:
```
Licenza white-label: €62,000
Custom dev (20%): €470,000 (6 mesi, 4 persone)
──────────────────────────────────────
TOTALE: €532,000
```

**Manutenzione**: €15k (white-label) + €100k (custom) = €115k/anno
**Proprietà**: 100% custom features, 0% core
**Time-to-market**: 6 mesi

**Revenue Potenziale**:
```
Anno 1: €360k (20 clienti da mese 6)
Anno 2: €1,080k (45 clienti)
Anno 3: €1,440k (60 clienti)
Anno 4: €1,800k (75 clienti)
Anno 5: €2,160k (90 clienti)
──────────────────────────────────────
TOTALE 5 ANNI: €6,840k revenue
```

**Costi 5 Anni**: €1,107,000
**Revenue 5 Anni**: €6,840,000
**NET**: +€5,733,000 (profitto)
**Break-even**: Mese 8

**Vantaggio vs Scenario A**: +€8,400,000 su 5 anni

---

## 12. Conclusioni

### 12.1 Costo Sviluppo Interno da Zero

| Scenario | Costo | Timeline | Break-even |
|----------|-------|----------|------------|
| **Team Full (20 persone)** | €4.7M | 30 mesi | Anno 7-8 |
| **Team Ridotto (12 persone)** | €3.6M | 40 mesi | Anno 6-7 |
| **Team Founder-led (6 persone)** | €2.2M | 50+ mesi | Anno 5-6 |
| **Hybrid Outsourcing** | €2.6M | 30 mesi | Anno 6 |

**Realistically**: **€4.7 milioni** per sviluppo completo professionale

---

### 12.2 TCO Comparativo 5 Anni

| Opzione | Investimento | TCO 5 Anni | Revenue 5 Anni | ROI |
|---------|-------------|------------|----------------|-----|
| **Sviluppo Interno** | €4.7M | €6.1M | €3.5M | -43% |
| **Buy SaaS** | €137k | €137k | €7.2M | +5,151% |
| **Hybrid** | €532k | €1.1M | €6.8M | +517% |

---

### 12.3 Raccomandazioni

**Per Noi (Business Decision)**:

1. **NON sviluppare da zero** se:
   - Esiste già soluzione 80% completa sul mercato
   - Time-to-market è critico
   - Budget limitato (< €5M disponibile)
   - Focus è go-to-market, non R&D

2. **Sviluppare internamente** solo se:
   - IP strategico differenziante
   - No alternative sul mercato (0% overlap)
   - Budget > €5M disponibile
   - Timeline 3+ anni accettabile
   - Team già esistente (sunk cost)

3. **Hybrid approach** (nostro caso):
   - Partire da base white-label (€62k)
   - Sviluppare solo 20-30% features custom
   - Time-to-market 6 mesi vs 30 mesi
   - **Risparmio €4M** e **anticipo revenue 24 mesi**

---

### 12.4 Valore del Nostro Software (Per Bilancio)

**Asset Contabile**:
- Costo sviluppo capitalizzato: €4,690,000
- Ammortamento 5 anni: €938,000/anno
- Valore netto Anno 1: €3,752,000

**Fair Market Value**:
- Stima conservativa: €4.5M
- Stima ottimistica: €7.0M
- **Valutazione raccomandata**: **€5.0 milioni**

---

**Documento per**: Internal Use / Budget Planning / Investment Decision
**Metodologia**: COCOMO II + Market Analysis + Financial Modeling
