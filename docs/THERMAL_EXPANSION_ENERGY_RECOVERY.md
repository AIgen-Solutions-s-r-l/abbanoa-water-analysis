# Sfruttamento dell'Espansione Termica delle Tubature per Risparmio Energetico

## Executive Summary

L'espansione e contrazione termica delle tubature rappresenta un fenomeno fisico sottoutilizzato che può essere sfruttato per monitoraggio passivo, generazione di energia e ottimizzazione della rete idrica.

## 1. Principi Fisici

### 1.1 Formula di Dilatazione Lineare
```
ΔL = L₀ × α × ΔT
dove:
- ΔL = variazione di lunghezza (m)
- L₀ = lunghezza iniziale (m)
- α = coefficiente di dilatazione termica (1/°C)
- ΔT = variazione di temperatura (°C)
```

### 1.2 Forza Generata
Se il tubo è vincolato:
```
F = E × A × α × ΔT
dove:
- F = forza assiale (N)
- E = modulo di Young (Pa)
- A = area sezione trasversale (m²)
```

## 2. Applicazioni Innovative

### 2.1 Energy Harvesting Piezoelettrico

**Concetto**: Convertire le micro-deformazioni in energia elettrica.

```python
class PiezoHarvester:
    def __init__(self, pipe_material, pipe_length, piezo_efficiency=0.15):
        self.material = pipe_material
        self.length = pipe_length
        self.efficiency = piezo_efficiency
        
    def calculate_energy_potential(self, temp_variation, cycles_per_day):
        # Energia meccanica per ciclo
        strain = self.material.thermal_coefficient * temp_variation
        stress = self.material.youngs_modulus * strain
        volume = self.length * self.material.cross_section
        
        mechanical_energy = 0.5 * stress * strain * volume
        electrical_energy = mechanical_energy * self.efficiency
        
        # Energia giornaliera
        daily_energy_wh = electrical_energy * cycles_per_day / 3600
        return daily_energy_wh
```

**Implementazione Pratica**:
- Installare trasduttori piezoelettrici nei giunti di dilatazione
- Energia stimata: 0.1-1 W per giunto
- Sufficiente per alimentare sensori IoT locali

### 2.2 Monitoraggio Passivo della Temperatura

**Sensore a Fibra di Bragg (FBG)**:
```javascript
// Algoritmo per temperatura da deformazione
const calculateTemperatureFromStrain = (measuredStrain, pipeProperties) => {
  const { thermalCoeff, mechanicalStrain, calibrationTemp } = pipeProperties;
  
  // Separare componente termica da meccanica
  const thermalStrain = measuredStrain - mechanicalStrain;
  const deltaTemp = thermalStrain / thermalCoeff;
  
  return calibrationTemp + deltaTemp;
};
```

### 2.3 Sistema di Compensazione Automatica della Pressione

**Principio**: Usare l'espansione per autoregolare la pressione.

```sql
-- Identificare pattern di espansione/pressione
WITH thermal_pressure_correlation AS (
  SELECT 
    node_id,
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(temperature) as avg_temp,
    AVG(pressure) as avg_pressure,
    STDDEV(pressure) as pressure_variation,
    LAG(AVG(temperature), 1) OVER (PARTITION BY node_id ORDER BY hour) as prev_temp
  FROM sensor_readings
  GROUP BY node_id, hour
)
SELECT 
  node_id,
  AVG((avg_temp - prev_temp) * 1000) as temp_change_rate,
  AVG(pressure_variation) as avg_pressure_var,
  CORR(avg_temp - prev_temp, pressure_variation) as correlation
FROM thermal_pressure_correlation
WHERE prev_temp IS NOT NULL
GROUP BY node_id
HAVING ABS(correlation) > 0.7;
```

### 2.4 Rilevamento Anomalie Strutturali

**ML per Pattern Recognition**:
```python
class ThermalAnomalyDetector:
    def __init__(self):
        self.expected_expansion = {}
        self.tolerance = 0.1  # 10%
        
    def train(self, historical_data):
        """Impara i pattern normali di espansione"""
        for pipe_segment in historical_data:
            temp_range = pipe_segment['temp_max'] - pipe_segment['temp_min']
            observed_movement = pipe_segment['displacement']
            material = pipe_segment['material']
            
            expected = self.calculate_theoretical_expansion(
                temp_range, 
                pipe_segment['length'],
                material
            )
            
            self.expected_expansion[pipe_segment['id']] = {
                'theoretical': expected,
                'observed': observed_movement,
                'ratio': observed_movement / expected
            }
    
    def detect_anomaly(self, pipe_id, current_temp_delta, current_displacement):
        """Rileva comportamenti anomali"""
        expected = self.expected_expansion[pipe_id]['theoretical'] * current_temp_delta
        
        if abs(current_displacement - expected) / expected > self.tolerance:
            return {
                'anomaly': True,
                'type': 'STRUCTURAL_ISSUE' if current_displacement < expected else 'BLOCKAGE',
                'severity': abs(current_displacement - expected) / expected
            }
        return {'anomaly': False}
```

## 3. Implementazione nel Sistema Roccavina

### 3.1 Dashboard "Thermal Dynamics"

```typescript
interface ThermalMetrics {
  currentExpansion: Map<string, number>;  // mm per segmento
  energyHarvested: number;               // Wh oggi
  temperatureMap: HeatmapData;           // Mappa termica rete
  anomalies: ThermalAnomaly[];           // Comportamenti anomali
  predictedMovement: number[];           // Previsione prossime 24h
}

// Componente React
const ThermalDynamicsPanel: React.FC = () => {
  const [metrics, setMetrics] = useState<ThermalMetrics>();
  
  return (
    <div className="grid grid-cols-3 gap-4">
      <Card>
        <h3>Energia Recuperata</h3>
        <div className="text-2xl font-bold">
          {metrics?.energyHarvested.toFixed(2)} Wh
        </div>
        <p className="text-sm text-gray-600">
          Equivalente a {(metrics?.energyHarvested * 365 / 1000).toFixed(1)} kWh/anno
        </p>
      </Card>
      
      <Card>
        <h3>Risparmio Manutenzione</h3>
        <ExpansionJointHealth data={metrics?.currentExpansion} />
      </Card>
      
      <Card>
        <h3>Anomalie Rilevate</h3>
        <AnomalyList items={metrics?.anomalies} />
      </Card>
    </div>
  );
};
```

### 3.2 Algoritmo di Ottimizzazione Operativa

```python
def optimize_operations_thermal(network_state, weather_forecast):
    """
    Ottimizza le operazioni basandosi sulle previsioni termiche
    """
    predicted_expansions = []
    
    for segment in network_state.segments:
        # Prevedi espansione per le prossime 24h
        temp_profile = weather_forecast.get_temperature_profile(segment.location)
        expansion = predict_thermal_expansion(segment, temp_profile)
        predicted_expansions.append(expansion)
        
        # Aggiusta pressione preventivamente
        if expansion.max_stress > segment.safe_stress * 0.8:
            return {
                'action': 'REDUCE_PRESSURE',
                'segment': segment.id,
                'reason': 'Prevenzione stress termico',
                'pressure_reduction': 0.2  # bar
            }
    
    return predicted_expansions
```

## 4. Calcolo del Valore Economico

### 4.1 Risparmio Diretto

1. **Energy Harvesting**:
   - 1000 giunti × 0.5W × 12h = 6 kWh/giorno
   - Valore: €330/anno (piccolo ma utile per IoT)

2. **Riduzione Rotture**:
   - Prevenzione 5 rotture/anno = €50,000 risparmio
   - Riduzione perdite acqua: 10,000 m³/anno = €15,000

3. **Manutenzione Predittiva**:
   - Estensione vita utile tubi: +20%
   - Risparmio: €200,000/anno su rete media

### 4.2 ROI Stimato
```
Investimento iniziale:
- Sensori FBG: €50,000
- Sistema piezoelettrico: €30,000
- Software & Integrazione: €40,000
Totale: €120,000

Risparmio annuale: €265,330
ROI: < 6 mesi
```

## 5. Implementazione Pratica

### Fase 1: Pilot Study (4 settimane)
```bash
# Selezione tratti test
- 2 km tubature acciaio DN500
- 1 km PVC DN300
- Installazione 20 sensori FBG
- 10 harvester piezoelettrici
```

### Fase 2: Data Collection (8 settimane)
```python
# Script raccolta dati
async def collect_thermal_data():
    while True:
        for sensor in thermal_sensors:
            data = await sensor.read()
            await db.insert({
                'timestamp': datetime.now(),
                'sensor_id': sensor.id,
                'temperature': data.temperature,
                'strain': data.strain,
                'displacement': data.displacement
            })
        await asyncio.sleep(300)  # 5 minuti
```

### Fase 3: ML Training (4 settimane)
- Dataset: 100,000+ misurazioni
- Modelli: LSTM per previsione, Isolation Forest per anomalie
- Accuracy target: >95% per previsioni a 24h

## 6. Sfide e Soluzioni

### 6.1 Sfide Tecniche
1. **Rumore nelle misurazioni**: Filtri Kalman
2. **Accoppiamento termo-meccanico**: Modelli FEM
3. **Variabilità materiali**: Calibrazione per tratto

### 6.2 Soluzioni Proposte
```python
# Filtro per separare segnali
class ThermalMechanicalFilter:
    def __init__(self):
        self.kalman = KalmanFilter(dim_x=4, dim_z=2)
        
    def process(self, measurement):
        # Separa componente termica da vibrazionale
        thermal_component = self.kalman.filter(measurement)
        mechanical_component = measurement - thermal_component
        return thermal_component, mechanical_component
```

## 7. Innovazioni Future

1. **Materiali Shape Memory**:
   - Tubi che si auto-riparano con il calore
   - Valvole termiche passive

2. **Digital Twin Termico**:
   - Simulazione real-time espansioni
   - Ottimizzazione preventiva

3. **Energy Storage Termico**:
   - Usare massa termica tubi come accumulo
   - Preriscaldamento acqua con calore ambientale

## Conclusioni

Lo sfruttamento dell'espansione termica delle tubature offre opportunità uniche per:
- Monitoraggio passivo a costo zero
- Generazione energia per IoT
- Prevenzione guasti strutturali
- Ottimizzazione operativa

L'implementazione richiede investimenti modesti con ROI rapidissimo e benefici a lungo termine significativi. 