# Strategia di Ottimizzazione dell'Inerzia nella Rete Idrica

## Executive Summary

L'inerzia meccanica della rete idrica rappresenta un'opportunità significativa per il risparmio energetico. Questo documento delinea strategie pratiche per sfruttare il momentum dell'acqua in movimento per ridurre il consumo delle pompe del 15-30%.

## 1. Principi Fisici

### 1.1 Inerzia Idraulica
L'acqua in movimento in una condotta possiede energia cinetica:
```
E_k = ½ * m * v²
dove:
- m = massa d'acqua nel segmento di tubo (kg)
- v = velocità del flusso (m/s)
```

### 1.2 Tempo di Decadimento
Dopo lo spegnimento della pompa, il flusso continua per:
```
t_coast = (ρ * L * v₀) / (f * P)
dove:
- ρ = densità dell'acqua (1000 kg/m³)
- L = lunghezza della condotta (m)
- v₀ = velocità iniziale (m/s)
- f = fattore di attrito
- P = perimetro bagnato (m)
```

## 2. Strategie di Ottimizzazione

### 2.1 Pump Cycling Optimization
**Obiettivo**: Minimizzare cicli start/stop sfruttando l'inerzia.

```python
def optimize_pump_cycles(current_flow, target_pressure, network_state):
    # Calcola il tempo di coasting disponibile
    coast_time = calculate_coast_time(current_flow, pipe_properties)
    
    # Se possiamo mantenere la pressione minima per X minuti
    if coast_time > 5 and current_pressure > target_pressure * 1.1:
        return PumpAction.STOP
    elif current_pressure < target_pressure * 0.9:
        return PumpAction.START
    else:
        return PumpAction.MAINTAIN
```

### 2.2 Variable Speed Drive (VSD) Integration
**Risparmio**: 20-30% rispetto a controllo ON/OFF.

```javascript
// Controllo adattivo della velocità
const adaptivePumpControl = (inertiaMetrics) => {
  const { momentum, pressureGradient, demandForecast } = inertiaMetrics;
  
  // Modulazione continua invece di ON/OFF
  let speedFactor = 1.0;
  
  if (momentum > HIGH_MOMENTUM_THRESHOLD) {
    // Ridurre velocità sfruttando l'inerzia esistente
    speedFactor = 0.6 + (0.4 * pressureGradient);
  }
  
  return {
    pumpSpeed: baseSpeed * speedFactor,
    estimatedSavings: (1 - speedFactor) * currentPowerKw
  };
};
```

### 2.3 Hydraulic Energy Recovery
**Pump-as-Turbine (PAT)** per zone con dislivello:

```sql
-- Identificazione opportunità PAT
WITH elevation_analysis AS (
  SELECT 
    source_node,
    dest_node,
    elevation_diff,
    avg_flow_rate,
    (elevation_diff * 9.81 * avg_flow_rate * 0.7 / 1000) as recovery_potential_kw
  FROM network_segments
  WHERE elevation_diff < -10  -- Flusso discendente
)
SELECT * FROM elevation_analysis 
WHERE recovery_potential_kw > 3
ORDER BY recovery_potential_kw DESC;
```

### 2.4 Smart Storage Management
Utilizzare serbatoi come "volani idraulici":

```python
class HydraulicBattery:
    def __init__(self, tank_capacity, elevation):
        self.capacity = tank_capacity
        self.elevation = elevation
        self.current_level = 0
        
    def charge(self, flow_rate, duration):
        """Riempire durante ore off-peak"""
        volume_added = flow_rate * duration
        self.current_level = min(self.current_level + volume_added, self.capacity)
        return self.calculate_stored_energy()
    
    def discharge(self, required_flow):
        """Usare gravità durante picchi"""
        available_head = self.elevation * self.current_level / self.capacity
        gravity_flow = sqrt(2 * 9.81 * available_head) * pipe_area
        return min(gravity_flow, required_flow)
```

## 3. Implementazione nel Sistema Abbanoa

### 3.1 Nuovi Sensori Richiesti
- Accelerometri per misurare vibrazioni/transitori
- Misuratori di coppia sui motori
- Sensori di velocità del flusso ad alta frequenza

### 3.2 Algoritmi ML per Predizione
```python
# Rete neurale per predire il decadimento del flusso
class InertiaPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=5, hidden_size=64, num_layers=2)
        self.fc = nn.Linear(64, 1)
        
    def forward(self, x):
        # x: [flow_rate, pressure, pipe_diameter, temperature, time_of_day]
        lstm_out, _ = self.lstm(x)
        coast_time = self.fc(lstm_out[-1])
        return coast_time
```

### 3.3 Dashboard Metrics
```typescript
interface InertiaOptimizationMetrics {
  currentInertia: number;           // kg⋅m/s
  availableCoastTime: number;       // secondi
  pumpEfficiency: number;           // %
  energySavedToday: number;         // kWh
  co2Reduced: number;               // kg CO₂
  costSavings: number;              // €
}
```

## 4. Calcolo del ROI

### 4.1 Risparmi Attesi
- **Pump Cycling Optimization**: 10-15% riduzione consumo
- **VSD Implementation**: 20-30% riduzione consumo
- **PAT Recovery**: 5-10% recupero energia
- **Smart Storage**: 15-20% shift del carico

### 4.2 Esempio Calcolo
```
Consumo attuale: 1,000,000 kWh/anno
Costo energia: €0.15/kWh
Risparmio totale: 25% = 250,000 kWh/anno
Risparmio economico: €37,500/anno
Investimento: €150,000
ROI: 4 anni
```

## 5. Fasi di Implementazione

### Fase 1: Analisi e Modellazione (2 settimane)
- Audit energetico dettagliato
- Modellazione idraulica della rete
- Identificazione zone con maggior potenziale

### Fase 2: Pilot Project (4 settimane)
- Implementare in 1-2 distretti
- Installare sensori aggiuntivi
- Sviluppare algoritmi di controllo

### Fase 3: ML Training (2 settimane)
- Raccolta dati dal pilot
- Training modelli predittivi
- Ottimizzazione parametri

### Fase 4: Full Deployment (8 settimane)
- Rollout su tutta la rete
- Integrazione SCADA
- Training operatori

## 6. KPI di Monitoraggio

```sql
-- Query per dashboard KPI
SELECT 
    DATE(timestamp) as date,
    SUM(energy_consumed_kwh) as total_energy,
    SUM(energy_saved_kwh) as energy_saved,
    AVG(pump_efficiency) as avg_efficiency,
    SUM(coast_time_minutes) as total_coasting,
    (SUM(energy_saved_kwh) * 0.15) as cost_savings_eur
FROM pump_operations
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## 7. Best Practices

1. **Evitare Water Hammer**: Transizioni graduali
2. **Mantenere Pressione Minima**: Mai sotto 1.5 bar
3. **Coordinazione Multi-Pompa**: Sincronizzare per massimizzare inerzia
4. **Manutenzione Predittiva**: L'efficienza degrada con l'usura

## 8. Conclusioni

L'ottimizzazione dell'inerzia può ridurre significativamente i costi operativi mantenendo o migliorando il servizio. La chiave è un approccio graduale con monitoraggio continuo dei risultati. 