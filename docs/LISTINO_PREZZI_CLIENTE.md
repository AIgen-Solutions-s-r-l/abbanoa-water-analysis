# Listino Prezzi - Abbanoa Water Analysis Platform

## Offerta Commerciale per Sistema di Monitoraggio Infrastrutture Idriche

**Data**: 2025-10-02
**Validità Offerta**: 90 giorni
**Versione**: 1.0.0

---

## 1. Executive Summary

### 1.1 Struttura dei Costi

La presente offerta si basa su un'architettura cloud moderna e scalabile ospitata su Google Cloud Platform (GCP), con i seguenti principi di pricing:

- **Costi Infrastruttura GCP**: €313/mese (scenario ottimizzato)
- **Margine Sicurezza**: 30% (buffer per sforamenti e picchi)
- **Margine Sviluppo & Supporto**: 40-60% (dipende dal tier)
- **Margine Commerciale**: 20-30%

---

## 2. Analisi Margini di Sicurezza

### 2.1 Breakdown Costi con Buffer

| Voce | Costo Base | Buffer 30% | Totale con Sicurezza |
|------|------------|------------|----------------------|
| **Infrastruttura GCP** | €313/mese | +€94/mese | **€407/mese** |

### 2.2 Scenari di Sforamento

**Sforamento Minimo (10-15%)**: €344-361/mese
- Cause: Picchi traffico temporanei, query BigQuery oltre previsioni
- Probabilità: 60%

**Sforamento Moderato (20-30%)**: €376-407/mese
- Cause: Crescita utenti inattesa, storage oltre 10 GB, egress elevato
- Probabilità: 30%

**Sforamento Significativo (40-50%)**: €438-470/mese
- Cause: Database oltre 50 GB, necessità upgrade instance, traffico 3x
- Probabilità: 10%

**Margine 30% copre il 90% degli scenari di sforamento**

### 2.3 Costi Nascosti da Considerare

1. **Support & Maintenance** (non incluso in infrastruttura):
   - Monitoring alerts: €10-20/mese
   - Security patches & updates: 4-8 ore/mese sviluppo
   - Bug fixes: 8-16 ore/mese
   - Incident response: variabile

2. **Feature Requests & Enhancements**:
   - Minor updates: 16-24 ore/mese
   - Major features: preventivi separati

3. **SLA & Uptime Garantito**:
   - 99.5% uptime: incluso nel costo base
   - 99.9% uptime: +€100/mese (multi-region, HA)

---

## 3. Listino Prezzi Commerciale

### 3.1 Pacchetti Abbonamento (SaaS - Subscription Model)

#### 🟢 PIANO STARTER
**Target**: Piccole utilities, fase pilota, proof of concept

**Caratteristiche:**
- Utenti: fino a 10 utenti
- Database: fino a 5 GB
- Storage BigQuery: 10 GB
- Uptime SLA: 99.5%
- Supporto: Email (48h response time)
- Backup: Giornaliero (7 giorni retention)
- API calls: 500k/mese
- Dashboard: Standard

**Costo Infrastruttura**: €313/mese (base ottimizzata)
**Buffer 30%**: €94/mese
**Supporto & Manutenzione**: €150/mese (12 ore/mese)
**Margine Commerciale 25%**: €139/mese

**PREZZO CLIENTE: €699/mese**
**Pagamento annuale: €7,490/anno** (sconto 10% = €749 x 10 mesi)

---

#### 🔵 PIANO PROFESSIONAL (Raccomandato)
**Target**: Utilities medie, produzione standard

**Caratteristiche:**
- Utenti: fino a 50 utenti
- Database: fino a 50 GB
- Storage BigQuery: 50 GB
- Uptime SLA: 99.7%
- Supporto: Email + Telefono (24h response time)
- Backup: Giornaliero (30 giorni retention)
- API calls: 2M/mese
- Dashboard: Standard + Custom reports
- Integrazioni: 2 custom integrations
- Training: 4 ore formazione/anno

**Costo Infrastruttura**: €346/mese (DB 50 GB)
**Buffer 30%**: €104/mese
**Supporto & Manutenzione**: €400/mese (32 ore/mese)
**Feature Development**: €200/mese (16 ore/mese)
**Margine Commerciale 30%**: €315/mese

**PREZZO CLIENTE: €1,399/mese**
**Pagamento annuale: €14,990/anno** (sconto 10% = €1,399 x 10.7 mesi)

---

#### 🟣 PIANO ENTERPRISE
**Target**: Grandi utilities, multi-tenant, high availability

**Caratteristiche:**
- Utenti: illimitati
- Database: fino a 500 GB
- Storage BigQuery: 200 GB
- Uptime SLA: 99.9% (multi-region)
- Supporto: 24/7 telefono/email (4h response time)
- Backup: Continuo (90 giorni retention)
- API calls: illimitate
- Dashboard: Custom completo + white label
- Integrazioni: illimitate custom integrations
- Training: 16 ore formazione/anno
- Dedicated account manager
- Custom SLA agreements
- Priority feature development

**Costo Infrastruttura**: €545/mese (DB 500 GB + HA)
**Buffer 30%**: €164/mese
**Supporto & Manutenzione**: €800/mese (64 ore/mese)
**Feature Development**: €600/mese (48 ore/mese)
**Account Management**: €200/mese
**Margine Commerciale 35%**: €811/mese

**PREZZO CLIENTE: €3,199/mese**
**Pagamento annuale: €34,990/anno** (sconto 8% = €3,199 x 10.9 mesi)

---

### 3.2 Modello On-Premise (Licenza Perpetua + Manutenzione)

#### 💼 LICENZA SOFTWARE PERPETUA

**One-time Setup Fee:**
- Licenza software: €45,000
- Installation & Configuration: €8,000
- Training (40 ore): €6,000
- Documentation & Handover: €3,000

**TOTALE SETUP: €62,000**

**Manutenzione Annuale (obbligatoria):**
- Software updates & patches: €8,000/anno
- Support (email 48h): €4,000/anno
- Security updates: €3,000/anno

**TOTALE MANUTENZIONE: €15,000/anno**

**Costi Infrastruttura (a carico cliente):**
- Server hardware/VPS: €100-300/mese
- Sistemista interno o esterno: variabile
- Backup & DR: variabile

**ROI Break-even vs PROFESSIONAL**: ~3.5 anni

---

### 3.3 Servizi Aggiuntivi à la Carte

#### Development & Customization

| Servizio | Tariffa |
|----------|---------|
| **Sviluppo custom features** | €120/ora |
| **Pacchetto 40 ore** | €4,500 (sconto 6%) |
| **Pacchetto 100 ore** | €10,500 (sconto 13%) |
| **Integrazioni API terze parti** | €2,500-5,000 (flat fee) |
| **Custom dashboard/report** | €1,500-3,000 (per dashboard) |
| **Mobile app (iOS/Android)** | €25,000-40,000 (sviluppo completo) |
| **White-label rebranding** | €5,000 (one-time) |

#### Support & Consulting

| Servizio | Tariffa |
|----------|---------|
| **Supporto priority (aggiunta a STARTER)** | +€200/mese |
| **SLA 99.9% upgrade** | +€150/mese |
| **Dedicated account manager** | +€300/mese |
| **On-site consulting (giornata)** | €1,200/giorno + spese |
| **Remote training (4 ore)** | €800/sessione |
| **Health check & optimization** | €2,500 (una tantum) |

#### Infrastructure & Scaling

| Servizio | Tariffa |
|----------|---------|
| **Database storage 100 GB → 500 GB** | +€150/mese |
| **Database storage 500 GB → 1 TB** | +€300/mese |
| **Utenti aggiuntivi (oltre limite piano)** | €10/utente/mese |
| **API calls extra (per 1M)** | €50/mese |
| **Multi-region deployment** | +€400/mese |
| **Disaster Recovery site** | +€350/mese |

---

## 4. Scenari di Pricing Consigliati

### 4.1 Scenario A: Cliente Small (10-15 utenti, 5-10 GB dati)

**Proposta**: PIANO STARTER
- Costo cliente: €699/mese
- Costo infrastruttura reale: ~€320/mese
- Margine lordo: €379/mese (54%)
- Ore supporto incluse: 12 ore/mese

**Upsell Opportunità**:
- Custom integration: +€2,500 (una tantum)
- Training: +€800 (una tantum)
- **Revenue Anno 1**: €11,790 (subscription + upsell)

---

### 4.2 Scenario B: Cliente Medium (30-50 utenti, 20-50 GB dati)

**Proposta**: PIANO PROFESSIONAL
- Costo cliente: €1,399/mese
- Costo infrastruttura reale: ~€360/mese
- Margine lordo: €1,039/mese (74%)
- Ore sviluppo/supporto incluse: 48 ore/mese

**Upsell Opportunità**:
- 2 custom dashboards: +€4,000 (una tantum)
- Priority support upgrade: +€200/mese
- Extra 40 ore sviluppo: +€4,500 (una tantum)
- **Revenue Anno 1**: €25,480 (subscription + upsell)

---

### 4.3 Scenario C: Cliente Enterprise (100+ utenti, multi-site)

**Proposta**: PIANO ENTERPRISE
- Costo cliente: €3,199/mese
- Costo infrastruttura reale: ~€600/mese
- Margine lordo: €2,599/mese (81%)
- Ore sviluppo/supporto incluse: 112 ore/mese

**Upsell Opportunità**:
- White-label: +€5,000 (una tantum)
- Mobile app: +€35,000 (una tantum)
- Multi-region: +€400/mese
- **Revenue Anno 1**: €82,380 (subscription + upsell)

---

### 4.4 Scenario D: Cliente On-Premise (requisiti compliance/security)

**Proposta**: LICENZA PERPETUA
- Setup: €62,000 (una tantum)
- Manutenzione: €15,000/anno
- Costo sviluppo reale: ~€30,000 (setup)
- Margine lordo Anno 1: €47,000 (61%)

**Upsell Opportunità**:
- Custom features: €10,500 (100 ore)
- On-site consulting: €3,600 (3 giorni)
- **Revenue Anno 1**: €91,100

---

## 5. Modello Pricing Flessibile

### 5.1 Pay-As-You-Grow (Alternativa SaaS)

**Pricing Variabile Basato su Utilizzo Effettivo**

**Base Fee**: €399/mese
- Include: infrastruttura base, 5 utenti, 5 GB storage
- Supporto: email 48h

**Costi Variabili**:
- **Utenti**: €8/utente/mese (oltre i 5 inclusi)
- **Storage**: €0.50/GB/mese (oltre i 5 GB inclusi)
- **API Calls**: €60 per 1M chiamate (oltre 500k incluse)
- **Support Hours**: €150/ora (on-demand)

**Esempio Cliente 25 utenti, 30 GB**:
```
Base: €399
Utenti: 20 × €8 = €160
Storage: 25 GB × €0.50 = €12.50
TOTALE: €571.50/mese
```

**Vantaggi**:
- Prezzo trasparente
- Cliente paga solo ciò che usa
- Facile upsell naturale

**Svantaggi**:
- Revenue imprevedibile
- Billing complexity
- Cliente potrebbe ottimizzare per ridurre costi

---

### 5.2 Modello Freemium (Lead Generation)

**Piano FREE (Tempo Indeterminato)**:
- 3 utenti
- 1 GB storage
- Dashboard base (read-only)
- Community support (forum)
- Watermark "Powered by Abbanoa Analytics"

**Conversione a STARTER**: 15-25% dopo 3-6 mesi

**Utilizzo**:
- Marketing tool
- Product-led growth
- Competizione con soluzioni gratuite

---

## 6. Strategie di Sconto & Incentivi

### 6.1 Sconti Volume

| Durata Contratto | Sconto | Note |
|------------------|--------|------|
| 1 anno prepagato | 10% | Standard |
| 2 anni prepagato | 18% | Raccomandato |
| 3 anni prepagato | 25% | Enterprise only |

### 6.2 Sconti Multi-Site

| Numero Installazioni | Sconto | Note |
|----------------------|--------|------|
| 2-3 siti | 15% | Sulla seconda installazione |
| 4-5 siti | 20% | Su terza e successive |
| 6+ siti | 25% | Negoziabile |

### 6.3 Incentivi Early Adopter

**Primi 5 Clienti**:
- Sconto 30% primo anno
- Sconto 15% secondo anno
- Sconto 10% terzo anno
- Riferimento marketing (con consenso)

**Beta Testers**:
- 50% sconto durante beta (3-6 mesi)
- 20% sconto lifetime dopo go-live

---

## 7. Confronto Competitivo (Benchmarking)

### 7.1 Posizionamento Mercato

| Competitor | Piano Base | Piano Professional | Piano Enterprise |
|------------|------------|--------------------| ----------------|
| **Noi (Abbanoa Analytics)** | €699/mese | €1,399/mese | €3,199/mese |
| **Competitor A (SCADA generico)** | €1,200/mese | €2,500/mese | €5,000/mese |
| **Competitor B (Water-specific)** | €850/mese | €1,800/mese | €4,200/mese |
| **Competitor C (Enterprise SAP)** | N/A | €3,500/mese | €8,000/mese |

**Nostro Vantaggio Competitivo**:
- 20-40% più economico
- Tecnologia moderna (React 19, Next.js 15)
- Time-to-market rapido (4-5 settimane)
- Personalizzabile
- Cloud-native scalabile

---

## 8. Calcolo Ritorno Investimento (ROI) per Cliente

### 8.1 Benefici Quantificabili

**Riduzione Perdite Idriche** (obiettivo 15% → 10%):
- Perdite attuali: 15% di 100M litri/giorno = 15M litri/giorno
- Riduzione: 5% = 5M litri/giorno risparmiati
- Valore acqua: €1.50/m³
- Risparmio annuo: 5,000 m³/giorno × 365 giorni × €1.50 = **€2,737,500/anno**

**Riduzione Tempo Risposta Anomalie**:
- Anomalie/anno: 200
- Tempo risposta attuale: 4 ore
- Tempo con sistema: 30 minuti
- Risparmio: 3.5 ore × 200 × €80/ora = **€56,000/anno**

**Riduzione Costi Manutenzione Predittiva**:
- Manutenzioni reattive: €200k/anno
- Risparmio con predittiva: 30% = **€60,000/anno**

**TOTALE BENEFICI**: €2,853,500/anno

**Costo Sistema** (Piano Professional): €16,788/anno

**ROI**: (€2,853,500 - €16,788) / €16,788 × 100 = **16,892% ROI**

**Payback Period**: < 1 settimana

---

## 9. Condizioni Contrattuali Standard

### 9.1 Termini di Pagamento

**Subscription (SaaS)**:
- Pagamento mensile: bonifico entro 30 gg fattura
- Pagamento annuale: bonifico entro 30 gg + sconto 10%
- Metodi accettati: Bonifico, Carta di Credito (Stripe), RID SEPA

**On-Premise**:
- Setup: 50% all'ordine, 50% al go-live
- Manutenzione annuale: anticipata, entro 30 gg fattura

### 9.2 Durata & Rinnovo

- **Durata minima**: 12 mesi
- **Rinnovo**: Automatico tacito (salvo disdetta 60 gg prima)
- **Disdetta**: Preavviso 60 giorni tramite PEC
- **Trial**: 30 giorni gratuiti (Piano Professional e Enterprise)

### 9.3 SLA & Uptime

| Piano | Uptime Garantito | Credito per Downtime |
|-------|------------------|----------------------|
| Starter | 99.5% (3.6h/mese) | Nessuno |
| Professional | 99.7% (2.2h/mese) | 10% canone mensile |
| Enterprise | 99.9% (43min/mese) | 25% canone mensile |

**Downtime = tempo totale inaccessibilità non pianificata**

### 9.4 Proprietà Dati

- **Dati cliente**: Proprietà esclusiva del cliente
- **Codice software**: Proprietà fornitore (licenza d'uso al cliente)
- **Export dati**: Garantito in qualsiasi momento (CSV, JSON, SQL dump)
- **Data retention**: 30 giorni dopo termine contratto

### 9.5 Clausola di Adeguamento Prezzi

- **Revisione annuale**: max +5% per inflazione (ISTAT)
- **Costi infrastruttura cloud**: se aumento GCP > 15%, possibile rinegoziazione
- **Preavviso**: 90 giorni per modifiche prezzo

---

## 10. Raccomandazioni di Vendita

### 10.1 Strategia Pricing Consigliata

**Fase 1 - Market Entry (Anno 1)**:
- Target: 10-15 clienti
- Focus: Piano PROFESSIONAL (sweet spot)
- Pricing: Aggressive (sconto early adopter 20%)
- Obiettivo revenue: €150k-200k

**Fase 2 - Growth (Anno 2-3)**:
- Target: 30-50 clienti
- Mix: 40% Starter, 50% Professional, 10% Enterprise
- Pricing: Standard (eliminare sconti early adopter)
- Obiettivo revenue: €600k-900k

**Fase 3 - Scale (Anno 4+)**:
- Target: 100+ clienti
- Mix: 30% Starter, 50% Professional, 20% Enterprise
- Pricing: Premium (aumenti 10-15%)
- Obiettivo revenue: €2M+

### 10.2 Priorità Acquisizione

1. **Quick Wins**: Clienti con budget, urgenza, decision maker disponibile
2. **Reference Customers**: Brand name per case studies
3. **Volume Players**: Grandi utilities per revenue

### 10.3 Red Flags (Clienti da Evitare)

- Budget < €500/mese (non sostenibile)
- Richieste custom > 80% (sviluppo ad hoc non scalabile)
- Payment terms > 60 giorni (cash flow risk)
- No decision maker access (sales cycle infinito)

---

## 11. Appendice: Calcolatore Prezzi

### 11.1 Formula Pricing Personalizzato

```
PREZZO_MENSILE = COSTO_INFRASTRUTTURA × (1 + BUFFER) + COSTO_SUPPORTO + MARGINE

Dove:
- COSTO_INFRASTRUTTURA = €313 base + €0.33 × (GB_DATABASE - 1)
- BUFFER = 30% (fisso)
- COSTO_SUPPORTO = ORE_SUPPORTO × €125/ora
- MARGINE = (COSTO_INFRASTRUTTURA + COSTO_SUPPORTO) × MARGINE_%

MARGINE_%:
- Starter: 25%
- Professional: 30%
- Enterprise: 35%
```

### 11.2 Esempio Calcolo Cliente Custom

**Requisiti**:
- 35 utenti
- 75 GB database
- 24 ore supporto/mese
- SLA 99.7%

**Calcolo**:
```
Infrastruttura: €313 + (€0.33 × 74) = €313 + €24.42 = €337.42
Buffer 30%: €337.42 × 0.30 = €101.23
Supporto: 24 ore × €125 = €3,000
Subtotale: €337.42 + €101.23 + €3,000 = €3,438.65
Margine 30%: €3,438.65 × 0.30 = €1,031.60

PREZZO FINALE: €4,470.25/mese
Arrotondato: €4,499/mese
```

**Posizionamento**: Tra Professional e Enterprise → **proporre €3,999/mese**

---

## 12. Contatti & Informazioni

**Per richieste commerciali**:
- Email: sales@abbanoa-analytics.com
- Telefono: +39 XXX XXX XXXX
- Web: www.abbanoa-analytics.com

**Per supporto tecnico pre-sales**:
- Email: presales@abbanoa-analytics.com
- Demo: Disponibile su richiesta (1 ora)

---

**Documento generato da**: Claude Code
**Versione**: 1.0.0
**Ultima revisione**: 2025-10-02

---

## Note Legali

Tutti i prezzi sono espressi in Euro (€) e sono da intendersi IVA esclusa.
I prezzi e le condizioni sono soggetti a modifica senza preavviso durante il periodo di validità dell'offerta.
Per offerte vincolanti è necessario richiedere un preventivo formale specifico.
