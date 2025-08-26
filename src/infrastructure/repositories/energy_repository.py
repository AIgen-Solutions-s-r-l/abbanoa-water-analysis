
import asyncpg
from typing import Optional
from src.schemas.energy import EnergyOptimization, HourlyEnergy, DailyStatistics, OptimizationOpportunity
from datetime import datetime

class EnergyRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_energy_optimization(self) -> Optional[EnergyOptimization]:
        try:
            async with self.pool.acquire() as conn:
                # Check if sensor_readings table exists
                table_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'water_infrastructure' 
                        AND table_name = 'sensor_readings'
                    )
                """)
                
                if not table_exists:
                    return None
                
                hourly_data = await conn.fetch("""
                    SELECT 
                        DATE_PART('hour', timestamp) as hour,
                        AVG(flow_rate) as avg_flow,
                        AVG(pressure) as avg_pressure,
                        COUNT(*) as reading_count
                    FROM water_infrastructure.sensor_readings
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                    GROUP BY DATE_PART('hour', timestamp)
                    ORDER BY hour
                """)
                
                # If no data, return None
                if not hourly_data:
                    return None
                
                hourly_energy = []
                peak_hours = []
                off_peak_savings = 0
            
            for hour_data in hourly_data:
                hour = int(hour_data['hour'])
                flow = float(hour_data['avg_flow']) if hour_data['avg_flow'] else 0
                pressure = float(hour_data['avg_pressure']) if hour_data['avg_pressure'] else 0
                
                power_kw = (flow * pressure * 2.75) / 100
                
                if 8 <= hour <= 20:
                    rate = 0.25
                    is_peak = True
                else:
                    rate = 0.15
                    is_peak = False
                
                cost = power_kw * rate
                
                hourly_energy.append(HourlyEnergy(
                    hour=hour,
                    flow_rate=round(flow, 2),
                    pressure=round(pressure, 2),
                    power_kw=round(power_kw, 2),
                    energy_cost=round(cost, 2),
                    is_peak=is_peak,
                    rate_eur_kwh=rate
                ))
                
                if is_peak and pressure > 4:
                    potential_savings = (flow * 1 * 2.75 / 100) * rate
                    off_peak_savings += potential_savings
            
            # If no hourly energy data was generated, return None
            if not hourly_energy:
                return None
            
            opportunities = []
            
            # Calculate average night pressure safely
            night_readings = [h for h in hourly_energy if h.hour < 6 or h.hour > 22]
            if night_readings:
                avg_night_pressure = sum(h.pressure for h in night_readings) / len(night_readings)
                if avg_night_pressure > 4:
                    opportunities.append(OptimizationOpportunity(
                        type='pressure_reduction',
                        title='Night-time Pressure Reduction',
                        description=f'Reduce pressure from {avg_night_pressure:.1f} to 3.5 bar during 23:00-06:00',
                        annual_savings_eur=round((avg_night_pressure - 3.5) * 7 * 365 * 2.75 * 0.15, 0),
                        implementation='Install PRV with time control',
                        investment_eur=15000,
                        roi_months=18
                    ))
            
            # Calculate peak and average power safely
            if hourly_energy:
                peak_power = max(h.power_kw for h in hourly_energy)
                avg_power = sum(h.power_kw for h in hourly_energy) / len(hourly_energy)
                if peak_power > avg_power * 1.5:
                    opportunities.append(OptimizationOpportunity(
                        type='peak_shaving',
                        title='Peak Demand Reduction',
                        description='Use storage tanks to reduce peak pumping by 30%',
                        annual_savings_eur=round((peak_power - avg_power) * 0.3 * 12 * 30 * 0.25, 0),
                        implementation='Optimize tank filling during off-peak',
                        investment_eur=5000,
                        roi_months=6
                    ))
            
                # Add VFD opportunity if we have data
                if avg_power > 0:
                    opportunities.append(OptimizationOpportunity(
                        type='vfd_upgrade',
                        title='Variable Frequency Drive Installation',
                        description='Install VFDs on main pumps for 20% energy reduction',
                        annual_savings_eur=round(avg_power * 24 * 365 * 0.2 * 0.20, 0),
                        implementation='Retrofit existing pump motors',
                        investment_eur=50000,
                        roi_months=24
                    ))
            
                daily_statistics = DailyStatistics(
                    total_energy_kwh=round(sum(h.power_kw for h in hourly_energy), 2),
                    total_cost_eur=round(sum(h.energy_cost for h in hourly_energy), 2),
                    peak_demand_kw=round(peak_power, 2),
                    average_power_kw=round(avg_power, 2),
                    peak_hours_cost=round(sum(h.energy_cost for h in hourly_energy if h.is_peak), 2),
                    off_peak_cost=round(sum(h.energy_cost for h in hourly_energy if not h.is_peak), 2)
                )

                return EnergyOptimization(
                    current_energy_profile=hourly_energy,
                    daily_statistics=daily_statistics,
                    optimization_opportunities=opportunities,
                    projected_annual_savings=round(sum(o.annual_savings_eur for o in opportunities), 0)
                )
            else:
                # Return None if we don't have enough data
                return None
        except Exception as e:
            print(f"Error fetching energy optimization data: {e}")
            return None
