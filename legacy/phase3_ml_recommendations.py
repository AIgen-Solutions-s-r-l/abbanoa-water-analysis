import pandas as pd
import numpy as np
import json

print("\n### FASE 3: RACCOMANDAZIONI MODELLI ML/AI ###\n")

# Load analysis results
with open("data_info.json", "r") as f:
    data_info = json.load(f)

with open("eda_results.json", "r") as f:
    eda_results = json.load(f)

# Load data for additional analysis
df = pd.read_csv(
    "cleaned_data.csv", sep=";", decimal=",", index_col=0, parse_dates=True
)

print(
    "Basandomi sull'analisi precedente, propongo i seguenti task di Machine Learning:\n"
)

# ML Task Recommendations
ml_tasks = []

# Task 1: Forecasting
task1 = {
    "nome": "Previsione Consumi e Portate",
    "tipo": "Time Series Forecasting",
    "obiettivo_business": "Ottimizzare la gestione della rete idrica prevedendo i consumi futuri per migliorare la distribuzione dell'acqua e ridurre gli sprechi",
    "variabili_target": [
        "Portata istantanea (L/S) - per prevedere il flusso d'acqua nei prossimi periodi",
        "Portata totale (M3) - per stimare i volumi cumulativi",
    ],
    "features": [
        "Ora del giorno (pattern orari identificati)",
        "Giorno della settimana (pattern settimanali)",
        "Mese/Stagione (pattern stagionali)",
        "Temperatura (correlazione con consumi)",
        "Valori storici (lag features)",
        "Media mobile delle ultime 24/48 ore",
    ],
    "modelli_consigliati": [
        {
            "nome": "Prophet",
            "vantaggi": [
                "Gestisce automaticamente trend e stagionalità multipla",
                "Robusto a dati mancanti",
                "Facile da interpretare e configurare",
                "Ottimo per previsioni a breve-medio termine (1-7 giorni)",
            ],
            "svantaggi": [
                "Meno accurato per previsioni a lungo termine",
                "Non cattura relazioni complesse non lineari",
            ],
            "quando_usarlo": "Ideale come primo approccio per la sua semplicità e interpretabilità",
        },
        {
            "nome": "SARIMA",
            "vantaggi": [
                "Modello statistico consolidato",
                "Cattura stagionalità e autocorrelazione",
                "Intervalli di confidenza ben definiti",
            ],
            "svantaggi": [
                "Richiede serie stazionarie (i dati non lo sono)",
                "Parametri difficili da ottimizzare",
                "Assume relazioni lineari",
            ],
            "quando_usarlo": "Dopo aver reso stazionarie le serie con differenziazione",
        },
        {
            "nome": "LSTM (Long Short-Term Memory)",
            "vantaggi": [
                "Cattura dipendenze complesse a lungo termine",
                "Gestisce multiple features in input",
                "Ottimo per pattern non lineari",
                "Può modellare relazioni tra diversi nodi della rete",
            ],
            "svantaggi": [
                "Richiede molti dati per training",
                "Difficile da interpretare (black box)",
                "Computazionalmente costoso",
            ],
            "quando_usarlo": "Per previsioni accurate quando si hanno almeno 2-3 anni di dati",
        },
    ],
}
ml_tasks.append(task1)

# Task 2: Anomaly Detection
task2 = {
    "nome": "Rilevamento Anomalie nella Rete",
    "tipo": "Anomaly Detection",
    "obiettivo_business": "Identificare perdite, guasti o comportamenti anomali nella rete idrica per interventi tempestivi e riduzione delle perdite",
    "variabili_target": [
        "Pattern anomali nelle portate",
        "Picchi/cali improvvisi di pressione",
        "Deviazioni dalla relazione normale temperatura-consumo",
    ],
    "features": [
        "Portata istantanea e sue variazioni",
        "Pressione e sue fluttuazioni",
        "Temperatura",
        "Differenza tra portata in ingresso e uscita nei nodi",
        "Deviazione dalla media storica per ora/giorno",
    ],
    "modelli_consigliati": [
        {
            "nome": "Isolation Forest",
            "vantaggi": [
                "Non richiede dati etichettati (unsupervised)",
                "Efficiente computazionalmente",
                "Buono per anomalie globali",
                "Facile da implementare e interpretare",
            ],
            "svantaggi": [
                "Meno efficace per anomalie contestuali",
                "Sensibile agli iperparametri",
            ],
            "quando_usarlo": "Come primo approccio per identificare anomalie evidenti",
        },
        {
            "nome": "Autoencoder",
            "vantaggi": [
                "Cattura pattern complessi normali",
                "Ottimo per anomalie contestuali",
                "Può apprendere rappresentazioni temporali",
            ],
            "svantaggi": [
                "Richiede più dati per training",
                "Più complesso da implementare",
                "Richiede tuning degli iperparametri",
            ],
            "quando_usarlo": "Per rilevare anomalie sottili basate sul contesto temporale",
        },
        {
            "nome": "Statistical Process Control (SPC)",
            "vantaggi": [
                "Semplice e interpretabile",
                "Basato su soglie statistiche chiare",
                "Ottimo per monitoraggio real-time",
            ],
            "svantaggi": [
                "Assume distribuzione normale",
                "Non cattura dipendenze temporali complesse",
            ],
            "quando_usarlo": "Per allarmi in tempo reale su metriche specifiche",
        },
    ],
}
ml_tasks.append(task2)

# Task 3: Optimization
task3 = {
    "nome": "Ottimizzazione Pressione di Rete",
    "tipo": "Predictive Optimization",
    "obiettivo_business": "Ottimizzare la pressione nella rete per minimizzare le perdite mantenendo il servizio adeguato",
    "variabili_target": ["Pressione ottimale per ogni nodo", "Setpoint delle pompe"],
    "features": [
        "Domanda prevista (dal modello di forecasting)",
        "Topologia della rete",
        "Vincoli di pressione minima/massima",
        "Costi energetici per fascia oraria",
    ],
    "modelli_consigliati": [
        {
            "nome": "Reinforcement Learning (DQN/PPO)",
            "vantaggi": [
                "Apprende strategie ottimali dal feedback",
                "Si adatta a cambiamenti nella rete",
                "Considera obiettivi multipli",
            ],
            "svantaggi": [
                "Richiede simulatore della rete",
                "Lungo tempo di training",
                "Difficile da validare",
            ],
            "quando_usarlo": "Per ottimizzazione avanzata con simulatore disponibile",
        },
        {
            "nome": "Gradient Boosting + Optimization",
            "vantaggi": [
                "Predice outcome di diverse configurazioni",
                "Più semplice del RL",
                "Interpretabile",
            ],
            "svantaggi": [
                "Non garantisce ottimo globale",
                "Richiede feature engineering",
            ],
            "quando_usarlo": "Come approccio pragmatico iniziale",
        },
    ],
}
ml_tasks.append(task3)

# Print recommendations
for i, task in enumerate(ml_tasks, 1):
    print(f"\n{'='*60}")
    print(f"TASK {i}: {task['nome'].upper()}")
    print(f"{'='*60}")
    print(f"\nTipo: {task['tipo']}")
    print("\nObiettivo di Business:")
    print(f"  {task['obiettivo_business']}")

    print("\nVariabili Target:")
    for target in task["variabili_target"]:
        print(f"  • {target}")

    print("\nFeatures Suggerite:")
    for feature in task["features"][:4]:
        print(f"  • {feature}")
    if len(task["features"]) > 4:
        print(f"  • ... e altre {len(task['features'])-4} features")

    print("\nModelli Consigliati:")
    for j, model in enumerate(task["modelli_consigliati"], 1):
        print(f"\n  {j}. {model['nome']}")
        print("     Vantaggi:")
        for v in model["vantaggi"][:2]:
            print(f"       + {v}")
        print(f"     Quando usarlo: {model['quando_usarlo']}")

# Implementation roadmap
print("\n" + "=" * 60)
print("ROADMAP DI IMPLEMENTAZIONE SUGGERITA")
print("=" * 60)

roadmap = [
    {
        "fase": "Fase 1 (Settimane 1-2)",
        "attività": "Implementare Prophet per forecasting portate a 24h",
        "motivazione": "Quick win con modello semplice e interpretabile",
    },
    {
        "fase": "Fase 2 (Settimane 3-4)",
        "attività": "Implementare Isolation Forest per anomaly detection base",
        "motivazione": "Identificare perdite evidenti e anomalie maggiori",
    },
    {
        "fase": "Fase 3 (Settimane 5-8)",
        "attività": "Sviluppare LSTM per forecasting avanzato multi-nodo",
        "motivazione": "Migliorare accuratezza considerando correlazioni tra nodi",
    },
    {
        "fase": "Fase 4 (Settimane 9-12)",
        "attività": "Integrare modelli in sistema di monitoraggio real-time",
        "motivazione": "Passare da analisi a sistema operativo",
    },
]

for step in roadmap:
    print(f"\n{step['fase']}:")
    print(f"  → {step['attività']}")
    print(f"  Motivazione: {step['motivazione']}")

# Save ML recommendations
ml_recommendations = {
    "tasks": ml_tasks,
    "roadmap": roadmap,
    "data_considerations": {
        "stationarity": "Le serie non sono stazionarie - necessaria differenziazione per SARIMA",
        "correlations": "Forte correlazione tra nodi - utile per modelli multi-variati",
        "seasonality": "Pattern orari e probabilmente settimanali evidenti",
        "data_quality": "Pochi valori mancanti, interpolazione lineare adeguata",
    },
}

with open("ml_recommendations.json", "w") as f:
    json.dump(ml_recommendations, f, indent=2, ensure_ascii=False)

print("\n✓ FASE 3 COMPLETATA")
print("\nSalvate raccomandazioni ML in 'ml_recommendations.json'")
