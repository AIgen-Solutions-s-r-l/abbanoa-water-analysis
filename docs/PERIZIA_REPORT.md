# PERIZIA TECNICA DI STIMA
## Valutazione del Patrimonio Software per Capitalizzazione IP

—

Perito indipendente (CTU): AI assistant – relazione tecnica redatta secondo IVS/OIV/IAS 38  
Data di valutazione: 12 Settembre 2025  
Repo valutato: abbanoa-water-analysis  
Commit/Tag analizzato: 3b2f1a721ed723265e72ded0e4053054aed2a029 (3b2f1a7)

—

## 1) Incarico e Indipendenza
- Incarico: stima del fair value dell’IP software a fini di conferimento/capitalizzazione.
- Indipendenza: nessun interesse del perito nelle parti. Nota di contesto: lo sviluppo è eseguito da AIgenSolutions s.r.l.; il sig. Alessio Rocchi (socio) è contributor principale. Ciò riduce il rischio di titolarità, fermo restando il reperimento di accordi di cessione/assunzione e chain-of-title.

## 2) Oggetto e Perimetro
- Denominazione: Water Infrastructure Analysis API e Frontend
- Proprietario dichiarato: AIgenSolutions s.r.l. (licenza proprietaria “All Rights Reserved” in README/Licenza)
- Versioni: backend v2.1.0 (pyproject), frontend v2.0.0 (package.json)
- Ambito: codice in `src/` (FastAPI, DDD), `frontend/` (Next.js), test in `tests/`, configurazioni e ops in `docker/`, `config/`, `k8s/`, `nginx/`, `Makefile`.

Repo metrics (statiche):
- LOC backend (Python, `src/`): 39.844  
- LOC test (Python, `tests/`): 16.661  
- LOC frontend app (TS/JS, `frontend/src/`, escluso `__tests__`): 17.610  
- File Python in `src/`: 196  
- Test Python: 61  
- Frontend: test Jest presenti (`*.spec.tsx`, integrazioni)

## 3) Due Diligence
Tecnica
- Qualità: Black/isort, flake8, pylint, mypy configurati (pyproject). Struttura DDD chiara, moduli separati, Makefile con quality gates.
- Test: suite pytest organizzata (markers), report HTML/XML; soglia `cov-fail-under=80` in `pytest.ini`. Nota: policy in `PROTOCOL.yaml` indica target 90%: disallineamento da sanare.
- Security/SCM: Bandit e Safety presenti; nessuna SBOM formalizzata (richiesta). Type-check attivo (mypy). Frontend con ESLint/Jest/TS.
- Ops/Architettura: Docker/PM2, Nginx, k8s dir, docs tecniche in `docs/architecture` e guide.

Legale
- Licenza proprietaria, copyright 2025 AIgenSolutions s.r.l.; necessaria evidenza: contratti/lettere d’assunzione/cessione IP dei contributor (incluso socio) e chain-of-title.

Commerciale
- Mancano: forecast ricavi attribuibili, pricing, contratti, pipeline e churn/retention. Necessari per metodi reddituali/di mercato.

## 4) Metodologie e Calcoli
Approcci applicabili: Costo (RCN), Reddito (RfR/DCF, non calcolabili senza dati), Mercato (comparables, non calcolabile senza fonti).

4.1 Metodo del Costo – Replacement Cost New (RCN)
Assunzioni trasparenti (da confermare):
- LOC applicativa stimata (senza test): 39.844 (PY) + 17.610 (TS/JS) ≈ 57.454  
- Produttività: 400–800 LOC/FTE-mese per software production-grade  
- Effort: 57.454 / 800 ≈ 72 PM (basso) … 57.454 / 400 ≈ 144 PM (alto)
- Loaded rate medio (Italia/UE, mix seniority): 6.000–10.000 €/PM  
- Overhead allocabile (tooling, gestione): 15% dei costi lavoro  
- Tooling/dati una tantum: 25.000 €  
- Obsolescenza complessiva (funz., tecnol., econ.): 20–30%

Calcolo RCN (range):
- Basso: lavoro 72×6.000=432.000; overhead 64.800; tooling 25.000 → RCN=521.800; −20% obsolescenza → 417.440 €
- Alto: lavoro 144×10.000=1.440.000; overhead 216.000; tooling 25.000 → RCN=1.681.000; −30% obsolescenza → 1.176.700 €

Punto di stima preliminare (media semplice RCN post‑obsolescenza): ≈ 797.070 €  
Nota: valori indicativi, soggetti a conferma di effort storico e tariffe interne.

4.2 Relief-from-Royalty (Reddito)
Non calcolabile senza: forecast ricavi attribuibili, tasso di royalty di mercato, tax rate definitivo, WACC. Struttura di calcolo disponibile nel template (report).

4.3 DCF attribuito all’IP (Reddito)
Non calcolabile senza: FCF per linea prodotto, fattore di attribuzione all’IP (α), WACC, g, orizzonte n e TV.

4.4 Approccio di Mercato
Non calcolabile senza: set di comparables (licensing deal o M&A) normalizzati per dimensione/crescita/margini e ambito IP.

## 5) Riconciliazione e Sensitività
- Con soli risultati da costo, la riconciliazione inter‑metodo non è applicabile.  
- Sensitività esemplificativa su RCN:

| Parametro | -20% | -10% | Base | +10% | +20% |
|---|---:|---:|---:|---:|---:|
| Rate €/PM | ~637.600 € | ~717.300 € | ~797.100 € | ~876.800 € | ~956.500 € |
| Obsolescenza | ↑ Valore | — | Base | ↓ Valore | ↓↓ Valore |
| Produttività LOC/PM | ↑ Valore con minore produttività | — | Base | ↓ Valore con maggiore produttività | ↓↓ |

Nota: i valori di riga “Rate €/PM” mostrano la sensibilità sul punto di stima indicativo variando solo la tariffa (tenendo fissi gli altri parametri).

## 6) Conclusioni
- Scenario base (RCN con obsolescenza 20–30%): 0,42–1,18 M€; punto di stima: ~0,80 M€.
- Addendum “assenza ricavi” (RCN con maggiore obsolescenza economica 35–45%): 0,29–1,09 M€; punto di stima conservativo (Q1 medio): ~0,55 M€.
- Raccomandazione attuale (assenza ricavi): adottare in sede prudenziale il punto di stima conservativo ~0,55 M€, con range comunicato 0,29–1,09 M€.
- Incertezza: media/alta per mancanza dati economico‑commerciali e effort storico.
- Uso: stima tecnica prudenziale, finalizzabile a ricezione delle evidenze richieste.

### Addendum: assenza di ricavi (adeguamento obsolescenza)
In mancanza di vendite/ricavi, si applica un incremento dell’obsolescenza economica per riflettere il rischio di adozione/monetizzazione. A partire dai RCN lordi stimati:
- RCN basso: 521.800 € → con obsolescenza 35% → 339.170 €; con 45% → 286.990 €
- RCN alto: 1.681.000 € → con obsolescenza 35% → 1.092.650 €; con 45% → 924.550 €

Range “assenza ricavi”: ~0,29–1,09 M€
Selezione del punto: media dei primi quartili di scenario base e assenza ricavi (~0,61 M€ e ~0,49 M€) → ~0,55 M€.

## 7) Richieste Integrative (bloccanti per la stima definitiva)
- Contratti/lettere (assignment IP) e chain‑of‑title dei contributor (incl. socio).  
- SBOM (CycloneDX o analogo) e licenze terze parti.  
- Forecast ricavi attribuibili, tax rate, WACC, pricing e pipeline.  
- Dati interni su effort storico (timesheet, burn‑down, risorse impiegate) e tariffe/CTC.  
- Eventuali comparables (licensing/M&A) adottati come riferimento.

## 8) Allegati ed Evidenze (repository)
- Config qualità: `pyproject.toml`, `pytest.ini`, `Makefile`, `PROTOCOL.yaml`, `README.md`  
- Struttura codice: `src/`, `frontend/`, `tests/`, `docs/`  
- Sicurezza: bandit/safety configurati (pyproject/Makefile)  
- Test: markers e addopts; soglia coverage 80% (`pytest.ini`)  
- Frontend: Jest/TypeScript; test presenti in `frontend/src/**/__tests__/`  
- Commit analizzato: 3b2f1a7; badge CI presente in README (verifica stato su GitHub)

—

Avvertenze: la presente perizia è redatta su base documentale e analisi statica del repository. Ogni numero economico non desumibile dai file del repo è frutto di assunzioni esplicite e deve essere sostituito da dati verificati ai fini della capitalizzazione contabile.
