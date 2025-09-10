"""Integration tests for KPI service real calculations."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np

from src.api.services.kpis.system_performance_service import SystemPerformanceService
from src.api.services.kpis.network_efficiency_service import NetworkEfficiencyService


@pytest.mark.asyncio
class TestSystemPerformanceRealCalculations:
    """Test system performance KPI calculations with real data."""
    
    async def test_calculate_uptime_percentage_from_real_data(self):
        """Test uptime calculation uses real sensor readings."""
        # Arrange
        service = SystemPerformanceService()
        mock_data = {
            'sensor_readings': [
                {'timestamp': datetime.now(timezone.utc) - timedelta(hours=i), 'status': 'active'}
                for i in range(24)
            ]
        }
        mock_data['sensor_readings'][5]['status'] = 'inactive'  # 1 hour downtime
        
        # Act
        result = service._calculate_uptime_percentage(mock_data)
        
        # Assert
        assert result == pytest.approx(95.83, rel=0.01)  # 23/24 hours = 95.83%
        assert result != 99.5  # Not the hardcoded value
    
    async def test_calculate_response_time_from_sensor_data(self):
        """Test response time calculation from actual sensor latencies."""
        # Arrange
        service = SystemPerformanceService()
        mock_data = {
            'response_times': [120, 145, 165, 130, 155, 140, 170, 125, 135, 150]
        }
        
        # Act
        result = service._calculate_average_response_time(mock_data)
        
        # Assert
        expected_avg = np.mean(mock_data['response_times'])
        assert result == pytest.approx(expected_avg, rel=0.01)
        assert result != 150.0  # Not the hardcoded value
    
    async def test_calculate_throughput_from_flow_rates(self):
        """Test throughput calculation from actual flow sensor data."""
        # Arrange
        service = SystemPerformanceService()
        mock_data = {
            'flow_rates': [45.2, 48.6, 52.1, 44.8, 50.3, 47.9, 51.5, 46.2],
            'time_interval': 3600  # 1 hour in seconds
        }
        
        # Act
        result = service._calculate_system_throughput(mock_data)
        
        # Assert
        total_flow = sum(mock_data['flow_rates'])
        expected_throughput = total_flow / (mock_data['time_interval'] / 3600)
        assert result == pytest.approx(expected_throughput, rel=0.01)
        assert result != 1000.0  # Not the hardcoded value
    
    async def test_calculate_error_rate_from_anomalies(self):
        """Test error rate calculation from anomaly detection data."""
        # Arrange
        service = SystemPerformanceService()
        mock_data = {
            'total_operations': 10000,
            'anomalies': [
                {'type': 'error', 'severity': 'high'},
                {'type': 'error', 'severity': 'medium'},
                {'type': 'warning', 'severity': 'low'},
                {'type': 'error', 'severity': 'critical'},
            ]
        }
        
        # Act
        result = service._calculate_error_rate(mock_data)
        
        # Assert
        error_count = len([a for a in mock_data['anomalies'] if a['type'] == 'error'])
        expected_rate = (error_count / mock_data['total_operations']) * 100
        assert result == pytest.approx(expected_rate, rel=0.01)
        assert result != 0.1  # Not the hardcoded value
    
    async def test_returns_null_when_insufficient_data(self):
        """Test returns null/error state when insufficient data available."""
        # Arrange
        service = SystemPerformanceService()
        mock_data = {'sensor_readings': []}  # Empty data
        
        # Act
        result = service._calculate_uptime_percentage(mock_data)
        
        # Assert
        assert result is None  # Should return None for insufficient data


@pytest.mark.asyncio
class TestNetworkEfficiencyRealCalculations:
    """Test network efficiency KPI calculations with real data."""
    
    async def test_calculate_water_loss_from_flow_differential(self):
        """Test water loss calculation from input/output flow sensors."""
        # Arrange
        service = NetworkEfficiencyService()
        mock_data = {
            'input_flow': 1000.0,  # m³/hour input
            'output_flow': 850.0,   # m³/hour output
            'known_consumption': 100.0  # m³/hour known usage
        }
        
        # Act
        result = service._calculate_water_loss_percentage(mock_data)
        
        # Assert
        loss = mock_data['input_flow'] - mock_data['output_flow'] - mock_data['known_consumption']
        expected_percentage = (loss / mock_data['input_flow']) * 100
        assert result == pytest.approx(expected_percentage, rel=0.01)
        assert result != 15.0  # Not the hardcoded value
    
    async def test_calculate_pressure_efficiency_from_sensors(self):
        """Test pressure efficiency from pressure sensor readings."""
        # Arrange
        service = NetworkEfficiencyService()
        mock_data = {
            'pressure_readings': [
                {'node': 'A', 'pressure': 4.5, 'target': 5.0},
                {'node': 'B', 'pressure': 4.8, 'target': 5.0},
                {'node': 'C', 'pressure': 3.9, 'target': 4.0},
                {'node': 'D', 'pressure': 5.2, 'target': 5.0},
            ]
        }
        
        # Act
        result = service._calculate_pressure_efficiency(mock_data)
        
        # Assert
        efficiencies = []
        for reading in mock_data['pressure_readings']:
            efficiency = min(reading['pressure'] / reading['target'], 1.0) * 100
            efficiencies.append(efficiency)
        expected = np.mean(efficiencies)
        assert result == pytest.approx(expected, rel=0.01)
        assert result != 85.0  # Not the hardcoded value
    
    async def test_calculate_flow_efficiency_from_capacity(self):
        """Test flow efficiency based on pipe capacity utilization."""
        # Arrange
        service = NetworkEfficiencyService()
        mock_data = {
            'pipes': [
                {'flow': 30, 'capacity': 50},
                {'flow': 45, 'capacity': 50},
                {'flow': 35, 'capacity': 40},
                {'flow': 20, 'capacity': 30},
            ]
        }
        
        # Act
        result = service._calculate_flow_efficiency(mock_data)
        
        # Assert
        efficiencies = []
        for pipe in mock_data['pipes']:
            # Efficiency is optimal at 70-80% capacity
            utilization = pipe['flow'] / pipe['capacity']
            if 0.7 <= utilization <= 0.8:
                efficiency = 100.0
            elif utilization < 0.7:
                efficiency = (utilization / 0.7) * 100
            else:
                efficiency = max(0, 100 - ((utilization - 0.8) / 0.2) * 50)
            efficiencies.append(efficiency)
        expected = np.mean(efficiencies)
        assert result == pytest.approx(expected, rel=0.01)
        assert result != 90.0  # Not the hardcoded value
    
    async def test_calculate_energy_efficiency_from_consumption(self):
        """Test energy efficiency from pump energy consumption data."""
        # Arrange
        service = NetworkEfficiencyService()
        mock_data = {
            'pumps': [
                {'flow_rate': 100, 'energy_consumed': 80},  # kWh per m³
                {'flow_rate': 150, 'energy_consumed': 110},
                {'flow_rate': 120, 'energy_consumed': 95},
            ],
            'baseline_efficiency': 0.7  # kWh/m³ baseline
        }
        
        # Act
        result = service._calculate_energy_efficiency(mock_data)
        
        # Assert
        efficiencies = []
        for pump in mock_data['pumps']:
            actual_efficiency = pump['energy_consumed'] / pump['flow_rate']
            efficiency = (mock_data['baseline_efficiency'] / actual_efficiency) * 100
            efficiencies.append(min(efficiency, 100))
        expected = np.mean(efficiencies)
        assert result == pytest.approx(expected, rel=0.01)
        assert result != 80.0  # Not the hardcoded value
    
    async def test_handles_database_connection_failure(self):
        """Test proper error handling when database is unavailable."""
        # Arrange
        service = NetworkEfficiencyService()
        mock_data = None  # Simulating no data from database
        
        # Act
        result = service._calculate_water_loss_percentage(mock_data)
        
        # Assert
        assert result is None  # Should return None when no data available


@pytest.mark.asyncio
async def test_no_hardcoded_values_in_system_performance():
    """Verify all hardcoded values have been removed from system performance."""
    # Read the service file
    with open('src/api/services/kpis/system_performance_service.py', 'r') as f:
        content = f.read()
    
    # Check that mock return statements are removed
    assert 'return 99.5' not in content
    assert 'return 150.0' not in content
    assert 'return 1000.0' not in content
    assert 'return 0.1' not in content
    assert 'return 65.0' not in content
    assert 'return 70.0' not in content
    assert 'return 99.9' not in content


@pytest.mark.asyncio
async def test_no_hardcoded_values_in_network_efficiency():
    """Verify all hardcoded values have been removed from network efficiency."""
    # Read the service file
    with open('src/api/services/kpis/network_efficiency_service.py', 'r') as f:
        content = f.read()
    
    # Check that mock return statements are removed
    assert 'return 15.0' not in content
    assert 'return 85.0' not in content
    assert 'return 90.0' not in content
    assert 'return 80.0' not in content
    assert 'return 95.0' not in content
    assert 'return 88.0' not in content