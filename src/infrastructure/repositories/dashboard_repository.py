

import asyncpg
from src.schemas.dashboard import DashboardSummary, KPIs, EnergyConsumption, NodeSummary, EnergyAnalysis

class DashboardRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_summary(self) -> DashboardSummary:
        async with self.pool.acquire() as conn:
            latest_readings = await conn.fetch("""
                SELECT 
                    AVG(sr.flow_rate) as avg_flow,
                    AVG(sr.pressure) as avg_pressure,
                    MAX(sr.flow_rate) as max_flow,
                    MAX(sr.pressure) as max_pressure,
                    MIN(sr.pressure) as min_pressure,
                    COUNT(DISTINCT sr.node_id) as active_nodes
                FROM water_infrastructure.sensor_readings sr
                JOIN water_infrastructure.nodes n ON sr.node_id = n.node_id
                WHERE sr.timestamp > NOW() - INTERVAL '24 hours'
                AND n.is_active = true
            """)
            
            row = latest_readings[0] if latest_readings else None
            
            nodes_data = await conn.fetch("""
                SELECT DISTINCT ON (n.node_id)
                    n.node_id,
                    n.node_name,
                    COALESCE(sr.flow_rate, 0.0) as flow_rate,
                    COALESCE(sr.pressure, 0.0) as pressure,
                    0.0 as reservoir_level,
                    sr.timestamp
                FROM water_infrastructure.nodes n
                LEFT JOIN water_infrastructure.sensor_readings sr 
                    ON sr.node_id = n.node_id
                    AND sr.timestamp > NOW() - INTERVAL '24 hours'
                WHERE n.is_active = true
                ORDER BY n.node_id, sr.timestamp DESC NULLS LAST
            """)
            
            total_power_kw = 0
            energy_nodes = []
            
            for node in nodes_data:
                flow_rate = float(node['flow_rate']) if node['flow_rate'] else 0.0
                pressure = float(node['pressure']) if node['pressure'] else 0.0
                
                if flow_rate > 0 and pressure > 0:
                    power_kw = (flow_rate * pressure * 2.75) / 100
                    total_power_kw += power_kw
                    
                    energy_nodes.append(EnergyAnalysis(
                        node_id=node['node_id'],
                        node_name=node['node_name'],
                        flow_rate=flow_rate,
                        pressure=pressure,
                        power_kw=round(power_kw, 2),
                        energy_cost_per_hour=round(power_kw * 0.20, 2)
                    ))
            
            daily_energy_kwh = total_power_kw * 24
            monthly_energy_kwh = daily_energy_kwh * 30
            daily_cost = daily_energy_kwh * 0.20
            monthly_cost = monthly_energy_kwh * 0.20
            
            if row and row['avg_flow'] and row['avg_pressure']:
                avg_flow = float(row['avg_flow'])
                avg_pressure = float(row['avg_pressure'])
                theoretical_power = (avg_flow * avg_pressure * 2.78) / 100
                pump_efficiency = (theoretical_power / total_power_kw * 100) if total_power_kw > 0 else 0
            else:
                pump_efficiency = 70.0
            
            kpis = KPIs(
                total_flow=float(row["avg_flow"]) if row and row["avg_flow"] else 0,
                average_pressure=float(row["avg_pressure"]) if row and row["avg_pressure"] else 0,
                system_efficiency=92.5,
                active_alerts=3,
                water_quality_index=95.8,
                energy_consumption=EnergyConsumption(
                    current_power_kw=round(total_power_kw, 2),
                    daily_consumption_kwh=round(daily_energy_kwh, 2),
                    monthly_consumption_kwh=round(monthly_energy_kwh, 2),
                    daily_cost_eur=round(daily_cost, 2),
                    monthly_cost_eur=round(monthly_cost, 2),
                    pump_efficiency_percent=round(pump_efficiency, 1),
                    cost_per_cubic_meter=round(daily_cost / (float(row['avg_flow']) * 24) if row and row['avg_flow'] and float(row['avg_flow']) > 0 else 0, 3)
                )
            )

            nodes = [NodeSummary(
                id=node["node_id"],
                name=node["node_name"],
                flow_rate=float(node["flow_rate"]) if node["flow_rate"] else 0,
                pressure=float(node["pressure"]) if node["pressure"] else 0,
                reservoir_level=float(node["reservoir_level"]) if node["reservoir_level"] else 0,
                power_consumption_kw=node.get('power_kw', 0),
                last_update=node["timestamp"].isoformat() if node["timestamp"] else None
            ) for node in nodes_data]

            return DashboardSummary(kpis=kpis, nodes=nodes, energy_analysis=energy_nodes)
