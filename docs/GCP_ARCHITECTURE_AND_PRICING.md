# Architettura GCP e Analisi dei Costi - Abbanoa Water Analysis

## Documento di Architettura per Deployment su Google Cloud Platform

**Data**: 2025-10-02
**Versione**: 1.0.0
**Progetto**: Abbanoa Water Infrastructure Monitoring System

---

## 1. Panoramica Sistema

### 1.1 Stack Tecnologico Attuale

**Backend:**
- Python 3.12
- FastAPI (framework API REST)
- SQLAlchemy (ORM)
- Pydantic (validazione dati)
- asyncpg (driver PostgreSQL asincrono)

**Frontend:**
- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Leaflet (mappe)
- Recharts (grafici)

**Database & Storage:**
- PostgreSQL/TimescaleDB (dati transazionali + time-series)
- Google BigQuery (analytics warehouse)
- Redis (caching & session management)

**Monitoring:**
- Prometheus
- Grafana

---

## 2. Architettura GCP Proposta

### 2.1 Diagramma Architetturale

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLOUD LOAD BALANCER                        │
│                    (Global HTTPS LB)                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ├──────────────────────┐
                       │                      │
                       ▼                      ▼
            ┌──────────────────┐  ┌──────────────────┐
            │  Cloud Run       │  │  Cloud Run       │
            │  (Frontend)      │  │  (Backend API)   │
            │  Next.js 15      │  │  FastAPI         │
            └────────┬─────────┘  └────────┬─────────┘
                     │                     │
                     │                     │
                     ├─────────────────────┴──────────┐
                     │                                │
                     ▼                                ▼
          ┌─────────────────────┐       ┌────────────────────┐
          │  Cloud SQL          │       │  Memorystore       │
          │  PostgreSQL         │       │  (Redis)           │
          │  + TimescaleDB      │       │  4GB Standard      │
          └─────────────────────┘       └────────────────────┘
                     │
                     │
                     ▼
          ┌─────────────────────┐
          │   BigQuery          │
          │   Analytics DW      │
          └─────────────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  Cloud Storage      │
          │  (Backups & Logs)   │
          └─────────────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │  Cloud Monitoring   │
          │  (Prometheus +      │
          │   Grafana)          │
          └─────────────────────┘
```

### 2.2 Componenti GCP

#### A. **Cloud Run** (Compute)
- **Frontend Service**: Next.js 15 containerizzato
  - Auto-scaling: 0-10 istanze
  - CPU: 1 vCPU
  - Memory: 512 MB
  - Concurrent requests: 80

- **Backend API Service**: FastAPI containerizzato
  - Auto-scaling: 1-20 istanze
  - CPU: 2 vCPU
  - Memory: 2 GB
  - Concurrent requests: 100

- **ETL Scheduler Service**: BigQuery → PostgreSQL sync
  - Scheduled jobs (Cloud Scheduler)
  - CPU: 1 vCPU
  - Memory: 1 GB
  - Runs: 4 volte/giorno (ogni 6 ore)

#### B. **Cloud SQL for PostgreSQL**
- **Instance Type**: db-custom-2-8192 (2 vCPU, 8 GB RAM)
- **Storage**: 50 GB SSD (auto-scaling fino a 500 GB)
- **Backup**: Automatico giornaliero (7 giorni retention)
- **High Availability**: Standby instance in zona diversa
- **Extensions**: TimescaleDB per time-series

#### C. **Memorystore for Redis**
- **Tier**: Standard (HA con replica)
- **Capacity**: 4 GB
- **Region**: europe-west1 (Belgio) o europe-west6 (Svizzera)

#### D. **BigQuery**
- **Dataset**: water_infrastructure
- **Storage**: ~5 GB logical storage
- **Queries**: ~100 GB/mese di data processing
- **Partitioning**: Per timestamp (riduce costi query)

#### E. **Cloud Storage**
- **Bucket 1**: Backups database (Standard Storage)
  - Retention: 30 giorni
  - Size: ~20 GB
- **Bucket 2**: Application logs (Nearline Storage)
  - Retention: 90 giorni
  - Size: ~10 GB

#### F. **Cloud Load Balancer**
- **Type**: Global HTTPS Load Balancer
- **SSL**: Google-managed certificate
- **Cloud Armor**: DDoS protection (opzionale)

#### G. **Cloud Monitoring & Logging**
- Prometheus self-hosted su Cloud Run (opzionale)
- Grafana su Cloud Run (opzionale)
- Cloud Monitoring nativo GCP (incluso)

#### H. **Networking**
- **VPC**: VPC privata dedicata
- **Cloud NAT**: Per egress traffic
- **VPC Peering**: Connessione tra servizi

---

## 3. Prezzi GCP (Aggiornati al 2025)

### 3.1 Listino Prezzi Componenti

#### Cloud Run
- **vCPU**: $0.00002400/vCPU-second
- **Memory**: $0.00000250/GiB-second
- **Requests**: $0.40 per milione di richieste
- **Free Tier**: 180,000 vCPU-seconds, 360,000 GiB-seconds, 2M requests/mese

#### Cloud SQL PostgreSQL
- **vCPU**: $0.0413/vCPU-hour
- **Memory**: $0.0070/GB-hour
- **Storage SSD**: $0.222/GB-mese
- **Backup**: $0.105/GB-mese

#### Memorystore Redis
- **Standard Tier**: ~$0.049/GB-hour (varia per regione)
- **Replica**: Inclusa nel Standard Tier

#### BigQuery
- **Storage (Active)**: $0.02/GB-mese
- **Storage (Long-term)**: $0.01/GB-mese (dopo 90 giorni)
- **Query**: $5/TB di dati processati
- **Free Tier**: 10 GB storage, 1 TB query/mese

#### Cloud Storage
- **Standard Storage**: $0.020/GB-mese (US) / $0.023/GB-mese (EU)
- **Nearline Storage**: $0.010/GB-mese
- **Operations**: $0.05 per 10,000 Class A ops

#### Cloud Load Balancer
- **Forwarding Rules**: $0.025/hour per rule
- **Data Processing**: $0.008-$0.012/GB (regionale)

#### Cloud NAT
- **NAT Gateway**: $0.044/hour
- **Data Processing**: $0.045/GB

#### Networking
- **Egress Internet (EU)**: $0.12/GB (primi 1TB), $0.11/GB (1-10TB)
- **Inter-region**: $0.02/GB

---

## 4. Stima Costi Mensili (Con 1 GB di Dati nel Database)

### 4.1 Assunzioni Base

**Traffico & Utilizzo:**
- **Utenti attivi**: 50 utenti/giorno
- **Requests/mese**: ~200,000 (frontend + API)
- **Database size**: 1 GB (baseline)
- **BigQuery storage**: 5 GB
- **BigQuery queries**: 100 GB/mese processati
- **Uptime**: 24/7 con traffico variabile
- **Egress Internet**: ~50 GB/mese

**Cloud Run (Frontend):**
- Avg instances: 1
- Peak instances: 3
- CPU time/mese: ~200 hours
- Memory: 512 MB

**Cloud Run (Backend API):**
- Avg instances: 2
- Peak instances: 5
- CPU time/mese: ~600 hours
- Memory: 2 GB

**Cloud Run (ETL Scheduler):**
- Runs: 4 volte/giorno × 30 giorni = 120 runs
- Duration: 15 min/run = 30 hours/mese
- Memory: 1 GB

### 4.2 Calcolo Dettagliato Costi

#### A. Cloud Run - Frontend
```
vCPU time: 200 hours = 720,000 seconds
Memory: 512 MB = 0.5 GiB

vCPU cost: 720,000 × $0.00002400 = $17.28
Memory cost: 720,000 × 0.5 × $0.00000250 = $0.90
Requests: 100,000 × $0.40/1M = $0.04

Subtotal Frontend: $18.22/mese
(Free tier copre ~$4.32, quindi costo effettivo: ~$14)
```

#### B. Cloud Run - Backend API
```
vCPU time: 600 hours = 2,160,000 seconds
Memory: 2 GiB

vCPU cost: 2,160,000 × $0.00002400 = $51.84
Memory cost: 2,160,000 × 2 × $0.00000250 = $10.80
Requests: 100,000 × $0.40/1M = $0.04

Subtotal Backend: $62.68/mese
```

#### C. Cloud Run - ETL Scheduler
```
vCPU time: 30 hours = 108,000 seconds
Memory: 1 GiB

vCPU cost: 108,000 × $0.00002400 = $2.59
Memory cost: 108,000 × 1 × $0.00000250 = $0.27

Subtotal ETL: $2.86/mese
```

**Total Cloud Run**: $14 + $62.68 + $2.86 = **$79.54/mese**

#### D. Cloud SQL PostgreSQL (db-custom-2-8192)
```
Instance:
- 2 vCPU × 730 hours × $0.0413 = $60.30
- 8 GB RAM × 730 hours × $0.0070 = $40.88

Storage:
- 50 GB SSD × $0.222 = $11.10

Backup:
- 10 GB backup × $0.105 = $1.05

Total Cloud SQL: $113.33/mese
```

#### E. Memorystore Redis (4 GB Standard Tier)
```
4 GB × 730 hours × $0.049 = $143.08/mese
```

#### F. BigQuery
```
Storage:
- 5 GB × $0.02 = $0.10/mese

Queries:
- 100 GB processati = 0.1 TB
- Free tier: 1 TB/mese
- Costo: $0 (coperto da free tier)

Total BigQuery: $0.10/mese
```

#### G. Cloud Storage
```
Backups (Standard):
- 20 GB × $0.023 = $0.46/mese

Logs (Nearline):
- 10 GB × $0.010 = $0.10/mese

Total Cloud Storage: $0.56/mese
```

#### H. Cloud Load Balancer
```
Forwarding rules:
- 1 rule × 730 hours × $0.025 = $18.25

Data processing:
- 50 GB × $0.010 = $0.50

Total Load Balancer: $18.75/mese
```

#### I. Cloud NAT
```
Gateway: 730 hours × $0.044 = $32.12
Data processing: 50 GB × $0.045 = $2.25

Total Cloud NAT: $34.37/mese
```

#### J. Networking (Egress)
```
Internet egress (EU): 50 GB × $0.12 = $6.00/mese
```

#### K. Cloud Monitoring & Logging
```
Stima (logs + metrics + traces): $10-20/mese
Assumiamo: $15/mese
```

### 4.3 **TOTALE COSTO MENSILE (1 GB Database)**

| Componente | Costo Mensile |
|------------|---------------|
| Cloud Run (Frontend) | $14.00 |
| Cloud Run (Backend API) | $62.68 |
| Cloud Run (ETL Scheduler) | $2.86 |
| Cloud SQL PostgreSQL | $113.33 |
| Memorystore Redis | $143.08 |
| BigQuery | $0.10 |
| Cloud Storage | $0.56 |
| Cloud Load Balancer | $18.75 |
| Cloud NAT | $34.37 |
| Networking (Egress) | $6.00 |
| Monitoring & Logging | $15.00 |
| **TOTALE** | **$410.73/mese** |

**Arrotondamento**: ~**$411/mese** o **€377/mese** (cambio 1.09)

---

## 5. Costo per GB Aggiuntivo di Dati

### 5.1 Impatto Storage Incrementale

Quando il database cresce da 1 GB a X GB, i costi aggiuntivi per ogni GB sono:

#### A. Cloud SQL Storage (Primario)
```
1 GB × $0.222/mese = $0.222/GB/mese
```

#### B. Cloud SQL Backup
```
Assumendo backup ratio 20%:
0.2 GB backup × $0.105 = $0.021/GB/mese
```

#### C. Cloud Storage Backup (ridondanza)
```
1 GB backup × $0.023 = $0.023/GB/mese
```

#### D. BigQuery Storage (ETL sync)
```
Se il dato viene sincronizzato in BigQuery:
1 GB × $0.02 = $0.020/GB/mese
```

#### E. BigQuery Queries (Incrementale)
```
Assunzione: ogni GB di storage genera 5 GB di query/mese
5 GB query = 0.005 TB
Costo: 0.005 TB × $5 = $0.025/GB/mese

(sotto free tier fino a 200 GB storage)
```

#### F. Egress Network (Incrementale)
```
Assunzione: 2% del dato viene scaricato/mese
0.02 GB × $0.12 = $0.0024/GB/mese
```

#### G. Cloud Run CPU/Memory (Processing)
```
Incremento marginale processing per query più pesanti:
Stima conservativa: $0.05/GB/mese
```

### 5.2 **COSTO TOTALE PER GB AGGIUNTIVO**

| Componente | Costo per GB/mese |
|------------|-------------------|
| Cloud SQL Storage | $0.222 |
| Cloud SQL Backup | $0.021 |
| Cloud Storage Backup | $0.023 |
| BigQuery Storage | $0.020 |
| BigQuery Queries | $0.025 |
| Network Egress | $0.002 |
| Cloud Run Processing | $0.050 |
| **TOTALE** | **$0.363/GB/mese** |

**Arrotondamento**: ~**$0.36/GB/mese** o **€0.33/GB/mese**

### 5.3 Proiezione Costi con Database Più Grandi

| DB Size | Costo Base | Costo Incrementale | **Totale/mese** |
|---------|------------|--------------------|--------------------|
| 1 GB | $410.73 | $0 | **$410.73** |
| 10 GB | $410.73 | $3.27 (9 GB × $0.363) | **$414.00** |
| 50 GB | $410.73 | $17.79 (49 GB × $0.363) | **$428.52** |
| 100 GB | $410.73 | $35.94 (99 GB × $0.363) | **$446.67** |
| 500 GB | $410.73 | $181.14 (499 GB × $0.363) | **$591.87** |
| 1 TB (1024 GB) | $410.73 | $371.35 (1023 GB × $0.363) | **$782.08** |

**Note:**
- Con database > 100 GB, conviene considerare commitment discounts (fino a 52% risparmio con 3 anni)
- BigQuery query cost aumenta significativamente con dataset grandi (rimuovere free tier)
- Cloud SQL potrebbe richiedere instance più grande (db-custom-4-16384) per DB > 500 GB

---

## 6. Ottimizzazioni Costi

### 6.1 Immediate (Senza Impatto Performance)

1. **Cloud SQL**:
   - Committed Use Discounts: -25% (1 anno), -52% (3 anni)
   - Schedule instance stop durante off-hours (se applicabile)
   - Usa HDD invece di SSD per storage non critico: risparmio 47%

2. **Memorystore Redis**:
   - CUD: -20% (1 anno), -40% (3 anni)
   - Valuta Basic Tier (no HA) per dev/staging: -50%

3. **Cloud Run**:
   - Set min instances = 0 per frontend: risparmio ~$10/mese
   - Usa Cloud CDN per static assets: riduce compute e egress

4. **BigQuery**:
   - Partitioning & Clustering: -70% query cost
   - Flat-rate pricing se queries > 400 TB/mese
   - Usa physical storage billing: -30% storage cost

5. **Cloud Storage**:
   - Lifecycle policies: auto-move logs a Coldline dopo 90 giorni
   - Compression per backups: -50% storage

6. **Networking**:
   - Cloud CDN: riduce egress fino a -80%
   - Regionalize traffic: evita inter-region charges

### 6.2 Stima con Ottimizzazioni Base

| Componente | Originale | Ottimizzato | Risparmio |
|------------|-----------|-------------|-----------|
| Cloud Run | $79.54 | $69.54 | -$10 |
| Cloud SQL | $113.33 | $85.00 | -$28.33 (CUD 1y) |
| Memorystore | $143.08 | $114.46 | -$28.62 (CUD 1y) |
| Cloud Storage | $0.56 | $0.35 | -$0.21 |
| Egress | $6.00 | $3.00 | -$3.00 (CDN) |
| **TOTALE** | **$410.73** | **$340.62** | **-$70.11 (-17%)** |

**Costo ottimizzato**: ~**$341/mese** o **€313/mese**

---

## 7. Alternative & Trade-offs

### 7.1 Opzione Low-Cost (Startup)

**Modifiche:**
- Cloud Run: min instances = 0, CPU always allocated = false
- Cloud SQL: db-f1-micro (0.6 GB RAM, shared vCPU) + HDD
- Memorystore: Basic Tier 1 GB
- No Cloud NAT (usa external IPs)
- Self-hosted Prometheus/Grafana su Cloud Run (spot instances)

**Costo stimato**: ~**$150-200/mese**

### 7.2 Opzione High-Performance (Production)

**Modifiche:**
- Cloud SQL: db-custom-4-16384 (4 vCPU, 16 GB) + Read Replicas
- Memorystore: 8 GB Standard Tier
- Cloud Run: min instances = 2 (backend), CPU always allocated = true
- Cloud CDN + Cloud Armor
- Multi-region setup

**Costo stimato**: ~**$800-1,200/mese**

### 7.3 Opzione Hybrid (GCP + On-Premise)

**Scenario:**
- Database PostgreSQL on-premise o VPS economico (Hetzner, OVH)
- Cloud Run per API e Frontend (burst capacity)
- BigQuery per analytics (keep)
- Redis self-hosted

**Costo GCP**: ~**$100-150/mese**
**Costo VPS**: ~€50-100/mese
**Totale**: ~**$200-250/mese**

---

## 8. Migration Plan

### 8.1 Fase 1: Setup Infrastruttura (Settimana 1-2)

1. **Progetto GCP**:
   - Crea progetto GCP "abbanoa-water-analysis-prod"
   - Abilita API necessarie (Cloud Run, Cloud SQL, Memorystore, BigQuery)
   - Setup billing alerts (€400/mese threshold)

2. **Networking**:
   - Crea VPC dedicata
   - Configura Cloud NAT
   - Setup firewall rules

3. **Database**:
   - Provision Cloud SQL PostgreSQL
   - Abilita TimescaleDB extension
   - Importa schema da `postgres_schema.sql`

4. **Redis**:
   - Provision Memorystore Redis 4 GB Standard Tier

5. **BigQuery**:
   - Crea dataset "water_infrastructure"
   - Setup partitioning su timestamp
   - Importa dati storici

### 8.2 Fase 2: Containerization (Settimana 2-3)

1. **Backend**:
   - Build Docker image FastAPI
   - Push to Google Container Registry (GCR)
   - Test localmente

2. **Frontend**:
   - Build Next.js Docker image (production)
   - Push to GCR
   - Validate build

3. **ETL**:
   - Containerizza ETL scheduler
   - Setup Cloud Scheduler triggers

### 8.3 Fase 3: Deploy & Testing (Settimana 3-4)

1. **Cloud Run Deploy**:
   - Deploy backend service
   - Deploy frontend service
   - Deploy ETL scheduler
   - Configure environment variables

2. **Load Balancer**:
   - Setup global HTTPS LB
   - Configure SSL certificate
   - Map custom domain

3. **Testing**:
   - Integration tests
   - Load testing (100 concurrent users)
   - Security audit

### 8.4 Fase 4: Monitoring & Go-Live (Settimana 4-5)

1. **Monitoring**:
   - Setup Cloud Monitoring dashboards
   - Configure alerts (error rate, latency, costs)
   - Prometheus/Grafana deployment (opzionale)

2. **Backup & DR**:
   - Validate automated backups
   - Test restore procedure
   - Document disaster recovery plan

3. **Go-Live**:
   - DNS cutover
   - Monitor per 48 ore
   - Rollback plan pronto

---

## 9. Checklist Sicurezza

- [ ] Cloud SQL: Private IP only
- [ ] IAM: Least privilege roles
- [ ] VPC: Firewall rules restrittive
- [ ] Cloud Armor: DDoS protection
- [ ] Secrets Manager: Per credentials
- [ ] Cloud KMS: Encryption at rest
- [ ] Audit Logging: Abilitato
- [ ] SSL/TLS: Certificate management
- [ ] Vulnerability scanning: Container images
- [ ] Compliance: GDPR data residency (EU region)

---

## 10. Conclusioni

### 10.1 Riepilogo Costi

| Scenario | Costo Mensile | Costo Annuale |
|----------|---------------|---------------|
| **Base (1 GB DB)** | €377/mese | €4,524/anno |
| **Ottimizzato (1 GB DB)** | €313/mese | €3,756/anno |
| **Low-Cost** | €165/mese | €1,980/anno |
| **High-Performance** | €920/mese | €11,040/anno |

### 10.2 Costo Incrementale Storage

- **Per GB aggiuntivo**: €0.33/GB/mese
- **Proiezione 100 GB DB**: €413/mese (ottimizzato)
- **Proiezione 1 TB DB**: €718/mese (ottimizzato)

### 10.3 Raccomandazioni

1. **Start con scenario Ottimizzato** (€313/mese):
   - Copertura adeguata per produzione
   - Costi prevedibili
   - Scalabilità garantita

2. **Implementa CUD (Committed Use Discounts)**:
   - 1 anno commitment per Cloud SQL e Memorystore
   - Risparmio immediato -17%

3. **Monitor costi settimanalmente**:
   - Setup billing alerts a €350/mese
   - Review mensile dettagliato
   - Ottimizza basandosi su dati reali

4. **Pianifica scaling**:
   - Database growth previsto?
   - User growth roadmap
   - Budget per Q2-Q4 2025

### 10.4 Next Steps

1. **Approvazione budget**: Presentare documento a stakeholders
2. **GCP credits**: Verificare eligibilità startup credits (fino a $100k)
3. **POC**: Deploy ambiente staging (low-cost) per validazione
4. **Timeline**: Pianificare migration completa in 4-5 settimane

---

**Autore**: Claude Code
**Revisione**: v1.0.0
**Contatto**: Team Abbanoa
