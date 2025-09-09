"""Unit tests for industry-standard water sector calculations."""

import pytest
from src.core.analytics.industry_calculations import (
    WaterIndustryCalculator,
    ItalianWaterSectorBenchmarks
)


class TestWaterIndustryCalculator:
    """Test industry-standard water sector calculations."""
    
    def test_energy_cost_calculation_follows_italian_standards(self):
        """Should calculate energy costs based on Italian water sector benchmarks."""
        # Arrange
        calculator = WaterIndustryCalculator()
        zones_count = 4
        system_efficiency = 85.0  # 85% efficient
        
        # Act
        result = calculator.calculate_energy_costs(zones_count, system_efficiency)
        
        # Assert
        assert result["annual_cost_eur"] > 0
        assert result["cost_per_zone_eur"] > 0
        assert result["kwh_per_m3"] == ItalianWaterSectorBenchmarks.SPECIFIC_ENERGY_CONSUMPTION
        assert result["tariff_eur_per_kwh"] == ItalianWaterSectorBenchmarks.INDUSTRIAL_ENERGY_TARIFF
        assert "methodology" in result
        
    def test_energy_cost_decreases_with_higher_efficiency(self):
        """Energy costs should decrease as system efficiency increases."""
        # Arrange
        calculator = WaterIndustryCalculator()
        zones_count = 4
        
        # Act
        low_efficiency_cost = calculator.calculate_energy_costs(zones_count, 60.0)
        high_efficiency_cost = calculator.calculate_energy_costs(zones_count, 90.0)
        
        # Assert
        assert low_efficiency_cost["annual_cost_eur"] > high_efficiency_cost["annual_cost_eur"]
        
    def test_water_loss_rate_calculation_uses_pressure_correlation(self):
        """Should calculate water loss rate based on pressure zones data."""
        # Arrange
        calculator = WaterIndustryCalculator()
        avg_pressure = 2.5  # bar
        zones_data = [
            {"avgPressure": 3.0, "status": "optimal"},
            {"avgPressure": 2.0, "status": "warning"}
        ]
        
        # Act
        result = calculator.calculate_water_loss_rate(zones_data, avg_pressure)
        
        # Assert
        assert 3.0 <= result["loss_percentage"] <= 25.0  # Realistic range
        assert result["baseline_losses"] == ItalianWaterSectorBenchmarks.BASELINE_WATER_LOSSES
        assert result["pressure_factor"] > 0
        assert "calculation_method" in result
        
    def test_system_efficiency_based_on_optimal_zones_ratio(self):
        """System efficiency should be calculated from optimal zones ratio."""
        # Arrange
        calculator = WaterIndustryCalculator()
        zones_data = [
            {"status": "optimal"},
            {"status": "optimal"},
            {"status": "warning"},
            {"status": "critical"}
        ]
        
        # Act
        result = calculator.calculate_system_efficiency(zones_data)
        
        # Assert
        assert result["efficiency_percentage"] == 50.0  # 2/4 optimal zones
        assert result["optimal_zones"] == 2
        assert result["total_zones"] == 4
        assert result["efficiency_class"] in ["A", "B", "C", "D", "E"]
        
    def test_italian_benchmarks_constants_are_realistic(self):
        """Italian water sector benchmarks should reflect realistic values."""
        # Act & Assert
        benchmarks = ItalianWaterSectorBenchmarks
        
        # Energy consumption: 0.5-1.2 kWh/m³ typical for Italian networks
        assert 0.5 <= benchmarks.SPECIFIC_ENERGY_CONSUMPTION <= 1.2
        
        # Industrial energy tariff: €0.20-€0.35/kWh typical in Italy
        assert 0.20 <= benchmarks.INDUSTRIAL_ENERGY_TARIFF <= 0.35
        
        # Water losses: 8-12% baseline for efficient Italian networks
        assert 8.0 <= benchmarks.BASELINE_WATER_LOSSES <= 12.0
        
        # Daily volume per zone: 1000-8000 m³/day realistic for municipal networks
        assert 1000 <= benchmarks.ESTIMATED_DAILY_VOLUME_PER_ZONE <= 8000


class TestItalianWaterSectorBenchmarks:
    """Test benchmark constants are properly defined."""
    
    def test_all_benchmarks_defined(self):
        """All required benchmarks should be defined."""
        benchmarks = ItalianWaterSectorBenchmarks
        
        assert hasattr(benchmarks, 'SPECIFIC_ENERGY_CONSUMPTION')
        assert hasattr(benchmarks, 'INDUSTRIAL_ENERGY_TARIFF')
        assert hasattr(benchmarks, 'BASELINE_WATER_LOSSES')
        assert hasattr(benchmarks, 'ESTIMATED_DAILY_VOLUME_PER_ZONE')
        assert hasattr(benchmarks, 'PRESSURE_LOSS_CORRELATION_FACTOR')
        
    def test_benchmark_sources_documented(self):
        """Benchmark values should have documented sources."""
        benchmarks = ItalianWaterSectorBenchmarks
        
        assert hasattr(benchmarks, 'SOURCES')
        assert len(benchmarks.SOURCES) > 0
        assert any('ARERA' in source or 'Utilitalia' in source or 'ISTAT' in source 
                  for source in benchmarks.SOURCES)