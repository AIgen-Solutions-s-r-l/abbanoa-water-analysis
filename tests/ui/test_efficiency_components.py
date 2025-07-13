"""
Unit tests for efficiency UI components.

This module contains comprehensive tests for the efficiency-related UI components
including DataFetcher, EfficiencyTab, EfficiencyTrend, KpiCard, and EfficiencyFilters.
"""

import pytest
import pandas as pd
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Import the components to test
from src.presentation.streamlit.utils.data_fetcher import DataFetcher
from src.presentation.streamlit.components.efficiency_tab import EfficiencyTab
from src.presentation.streamlit.components.charts.EfficiencyTrend import EfficiencyTrend
from src.presentation.streamlit.components.KpiCard import KpiCard
from src.presentation.streamlit.components.filters.EfficiencyFilters import EfficiencyFilters


class TestDataFetcherEfficiency:
    """Test suite for DataFetcher efficiency methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.data_fetcher = DataFetcher()
        
    def test_get_efficiency_summary_success(self):
        """Test successful efficiency summary retrieval."""
        # Mock response data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'efficiency_percentage': 94.2,
            'total_input_volume': 5200.0,
            'total_output_volume': 4896.4,
            'total_loss_volume': 303.6,
            'active_nodes': 6,
            'total_nodes': 8
        }
        
        with patch.object(self.data_fetcher.session, 'get', return_value=mock_response):
            result = self.data_fetcher.get_efficiency_summary()
            
            assert result is not None
            assert result['efficiency_percentage'] == 94.2
            assert result['loss_percentage'] == 5.8  # 100 - 94.2
            assert result['loss_m3_per_hour'] == 303.6 / 24
            assert result['active_nodes'] == 6
            assert result['total_nodes'] == 8
            assert 'last_updated' in result
    
    def test_get_efficiency_summary_api_failure(self):
        """Test efficiency summary with API failure."""
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(self.data_fetcher.session, 'get', return_value=mock_response):
            result = self.data_fetcher.get_efficiency_summary()
            
            # Should return fallback data
            assert result is not None
            assert result['efficiency_percentage'] == 94.2
            assert result['loss_percentage'] == 5.8
            assert result['loss_m3_per_hour'] == 12.5
            assert result['active_nodes'] == 6
            assert result['total_nodes'] == 8
    
    def test_get_efficiency_summary_with_time_range(self):
        """Test efficiency summary with custom time range."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'efficiency_percentage': 92.5,
            'total_input_volume': 3000.0,
            'total_output_volume': 2775.0,
            'active_nodes': 5
        }
        
        start_time = datetime(2024, 1, 1, 10, 0, 0)
        end_time = datetime(2024, 1, 1, 18, 0, 0)
        
        with patch.object(self.data_fetcher.session, 'get', return_value=mock_response) as mock_get:
            result = self.data_fetcher.get_efficiency_summary(start_time, end_time)
            
            # Verify API was called with correct parameters
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert 'start_time' in call_args[1]['params']
            assert 'end_time' in call_args[1]['params']
            
            assert result['efficiency_percentage'] == 92.5
            assert result['total_input_volume'] == 3000.0
    
    def test_get_efficiency_trends_success(self):
        """Test successful efficiency trends retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'timestamp': '2024-01-01T10:00:00Z',
                'efficiency_percentage': 94.0,
                'loss_percentage': 6.0,
                'pressure_mh2o': 2.8,
                'reservoir_level_percentage': 75.0
            },
            {
                'timestamp': '2024-01-01T11:00:00Z',
                'efficiency_percentage': 94.5,
                'loss_percentage': 5.5,
                'pressure_mh2o': 2.9,
                'reservoir_level_percentage': 76.0
            }
        ]
        
        with patch.object(self.data_fetcher.session, 'get', return_value=mock_response):
            result = self.data_fetcher.get_efficiency_trends(hours_back=2)
            
            assert not result.empty
            assert len(result) == 2
            assert 'timestamp' in result.columns
            assert 'efficiency_percentage' in result.columns
            assert 'loss_percentage' in result.columns
            assert 'pressure_mh2o' in result.columns
            assert 'target_efficiency' in result.columns
            assert result['target_efficiency'].iloc[0] == 95.0
    
    def test_get_efficiency_trends_with_filters(self):
        """Test efficiency trends with district and node filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        
        with patch.object(self.data_fetcher.session, 'get', return_value=mock_response) as mock_get:
            self.data_fetcher.get_efficiency_trends(
                hours_back=24,
                district_filter="DIST_001",
                node_filter="Primary Station"
            )
            
            # Verify filters were passed as parameters
            call_args = mock_get.call_args
            params = call_args[1]['params']
            assert 'district' in params
            assert 'node' in params
            assert params['district'] == "DIST_001"
            assert params['node'] == "Primary Station"
    
    def test_get_efficiency_trends_fallback(self):
        """Test efficiency trends fallback to mock data."""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch.object(self.data_fetcher.session, 'get', return_value=mock_response):
            result = self.data_fetcher.get_efficiency_trends(hours_back=24)
            
            # Should return mock data
            assert not result.empty
            assert len(result) == 25  # 24 hours + 1
            assert 'timestamp' in result.columns
            assert 'efficiency_percentage' in result.columns
            assert 'target_efficiency' in result.columns
            assert result['target_efficiency'].iloc[0] == 95.0


class TestEfficiencyTab:
    """Test suite for EfficiencyTab component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.efficiency_tab = EfficiencyTab()
        
    def test_init(self):
        """Test EfficiencyTab initialization."""
        assert self.efficiency_tab.data_fetcher is not None
        assert self.efficiency_tab.efficiency_trend is not None
        assert self.efficiency_tab.kpi_card is not None
        assert self.efficiency_tab.efficiency_filters is not None
    
    def test_convert_time_range(self):
        """Test time range conversion."""
        start_time, end_time = self.efficiency_tab._convert_time_range("Last 24 Hours")
        
        assert isinstance(start_time, datetime)
        assert isinstance(end_time, datetime)
        assert end_time > start_time
        assert (end_time - start_time).total_seconds() == 24 * 3600
    
    def test_get_hours_from_time_range(self):
        """Test hours extraction from time range."""
        assert self.efficiency_tab._get_hours_from_time_range("Last 6 Hours") == 6
        assert self.efficiency_tab._get_hours_from_time_range("Last 24 Hours") == 24
        assert self.efficiency_tab._get_hours_from_time_range("Last 3 Days") == 72
        assert self.efficiency_tab._get_hours_from_time_range("Last Week") == 168
        assert self.efficiency_tab._get_hours_from_time_range("Unknown") == 24
    
    @patch('streamlit.error')
    @patch('streamlit.spinner')
    def test_get_efficiency_data_with_loading_error(self, mock_spinner, mock_error):
        """Test efficiency data loading with error handling."""
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()
        
        with patch.object(self.efficiency_tab.data_fetcher, 'get_efficiency_summary', 
                         side_effect=Exception("API Error")):
            result = self.efficiency_tab._get_efficiency_data_with_loading("Last 24 Hours")
            
            assert result is None
            mock_error.assert_called_once_with("Error fetching efficiency data: API Error")
    
    def test_get_efficiency_data_with_loading_success(self):
        """Test successful efficiency data loading."""
        mock_efficiency_data = {
            'efficiency_percentage': 95.0,
            'loss_m3_per_hour': 10.0,
            'avg_pressure_mh2o': 2.8,
            'reservoir_level_percentage': 78.0
        }
        
        with patch.object(self.efficiency_tab.data_fetcher, 'get_efficiency_summary', 
                         return_value=mock_efficiency_data):
            result = self.efficiency_tab._get_efficiency_data_with_loading("Last 24 Hours")
            
            assert result == mock_efficiency_data
    
    def test_get_node_efficiency_data(self):
        """Test node efficiency data retrieval."""
        result = self.efficiency_tab._get_node_efficiency_data()
        
        assert isinstance(result, dict)
        assert len(result) == 8
        assert "Primary Station" in result
        assert "Secondary Station" in result
        assert all(isinstance(v, (int, float)) for v in result.values())
    
    def test_get_loss_distribution_data(self):
        """Test loss distribution data retrieval."""
        result = self.efficiency_tab._get_loss_distribution_data()
        
        assert isinstance(result, dict)
        assert len(result) == 5
        assert "Pipe Leakage" in result
        assert "Meter Inaccuracy" in result
        assert all(isinstance(v, (int, float)) for v in result.values())
    
    def test_get_pressure_analysis_data(self):
        """Test pressure analysis data retrieval."""
        result = self.efficiency_tab._get_pressure_analysis_data()
        
        assert isinstance(result, dict)
        assert 'current_pressure' in result
        assert 'optimal_min' in result
        assert 'optimal_max' in result
        assert len(result['current_pressure']) == 8
        assert len(result['optimal_min']) == 8
        assert len(result['optimal_max']) == 8


class TestEfficiencyTrend:
    """Test suite for EfficiencyTrend component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.data_fetcher = Mock()
        self.efficiency_trend = EfficiencyTrend(self.data_fetcher)
        
    def test_init(self):
        """Test EfficiencyTrend initialization."""
        assert self.efficiency_trend.data_fetcher is not None
        
    def test_init_with_no_data_fetcher(self):
        """Test EfficiencyTrend initialization without data fetcher."""
        with patch('src.presentation.streamlit.components.charts.EfficiencyTrend.DataFetcher') as mock_df:
            trend = EfficiencyTrend()
            assert trend.data_fetcher is not None
            mock_df.assert_called_once()
    
    def test_create_efficiency_chart(self):
        """Test efficiency chart creation."""
        # Create sample trend data
        trend_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=24, freq='H'),
            'efficiency_percentage': [94.0 + i * 0.1 for i in range(24)],
            'loss_percentage': [6.0 - i * 0.1 for i in range(24)],
            'pressure_mh2o': [2.8 + i * 0.01 for i in range(24)],
            'reservoir_level_percentage': [75.0 + i * 0.5 for i in range(24)]
        })
        
        fig = self.efficiency_trend._create_efficiency_chart(
            trend_data=trend_data,
            height=400,
            show_target_line=True,
            target_efficiency=95.0,
            chart_type="line",
            title="Test Chart"
        )
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.height == 400
        assert fig.layout.title.text == "Test Chart"
        # Check that we have the expected number of traces (efficiency, input vol, output vol)
        assert len(fig.data) >= 2
    
    def test_create_efficiency_chart_area_type(self):
        """Test efficiency chart creation with area type."""
        trend_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='H'),
            'efficiency_percentage': [94.0, 94.5, 95.0, 94.8, 94.2],
            'loss_percentage': [6.0, 5.5, 5.0, 5.2, 5.8],
            'pressure_mh2o': [2.8, 2.9, 3.0, 2.9, 2.8],
            'reservoir_level_percentage': [75.0, 76.0, 77.0, 76.5, 75.5]
        })
        
        fig = self.efficiency_trend._create_efficiency_chart(
            trend_data=trend_data,
            height=300,
            show_target_line=False,
            target_efficiency=95.0,
            chart_type="area",
            title="Area Chart"
        )
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.height == 300
        # Check that the first trace is an area fill
        assert fig.data[0].fill in ['tozeroy', 'tonexty']
    
    def test_display_chart_summary(self):
        """Test chart summary display."""
        trend_data = pd.DataFrame({
            'efficiency_percentage': [94.0, 95.0, 96.0, 94.5, 93.0]
        })
        
        with patch('streamlit.expander') as mock_expander:
            mock_expander.return_value.__enter__ = Mock()
            mock_expander.return_value.__exit__ = Mock()
            
            with patch('streamlit.columns') as mock_columns:
                mock_columns.return_value = [Mock(), Mock(), Mock(), Mock()]
                
                with patch('streamlit.metric') as mock_metric:
                    self.efficiency_trend._display_chart_summary(trend_data, 95.0)
                    
                    # Should call metric 4 times (one for each column)
                    assert mock_metric.call_count == 4
                    
                    # Check that metrics were called with expected values
                    calls = mock_metric.call_args_list
                    
                    # Current efficiency (last value)
                    assert calls[0][0][0] == "Current Efficiency"
                    assert "93.0%" in calls[0][0][1]
                    
                    # Average efficiency
                    assert calls[1][0][0] == "Average Efficiency"
                    assert "94.5%" in calls[1][0][1]
    
    @patch('streamlit.warning')
    def test_render_empty_data(self, mock_warning):
        """Test rendering with empty data."""
        self.data_fetcher.get_efficiency_trends.return_value = pd.DataFrame()
        
        with patch('streamlit.spinner') as mock_spinner:
            mock_spinner.return_value.__enter__ = Mock()
            mock_spinner.return_value.__exit__ = Mock()
            
            self.efficiency_trend.render(hours_back=24)
            
            mock_warning.assert_called_once_with("No efficiency trend data available for the selected time range")
    
    @patch('streamlit.error')
    def test_render_with_error(self, mock_error):
        """Test rendering with error."""
        self.data_fetcher.get_efficiency_trends.side_effect = Exception("Data fetch error")
        
        with patch('streamlit.spinner') as mock_spinner:
            mock_spinner.return_value.__enter__ = Mock()
            mock_spinner.return_value.__exit__ = Mock()
            
            self.efficiency_trend.render(hours_back=24)
            
            mock_error.assert_called_once()
            assert "Error loading efficiency trend chart" in mock_error.call_args[0][0]


class TestKpiCard:
    """Test suite for KpiCard component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.kpi_card = KpiCard()
        
    def test_init(self):
        """Test KpiCard initialization."""
        assert self.kpi_card.default_thresholds is not None
        assert 'efficiency_percentage' in self.kpi_card.default_thresholds
        assert 'loss_m3_per_hour' in self.kpi_card.default_thresholds
        assert 'avg_pressure_mh2o' in self.kpi_card.default_thresholds
        assert 'reservoir_level_percentage' in self.kpi_card.default_thresholds
    
    def test_get_efficiency_delta_color(self):
        """Test efficiency delta color calculation."""
        assert self.kpi_card._get_efficiency_delta_color(96.0) == "normal"
        assert self.kpi_card._get_efficiency_delta_color(92.0) == "normal"
        assert self.kpi_card._get_efficiency_delta_color(88.0) == "inverse"
    
    def test_get_loss_delta_color(self):
        """Test loss delta color calculation."""
        assert self.kpi_card._get_loss_delta_color(8.0) == "normal"
        assert self.kpi_card._get_loss_delta_color(12.0) == "normal"
        assert self.kpi_card._get_loss_delta_color(18.0) == "inverse"
    
    def test_get_pressure_delta_color(self):
        """Test pressure delta color calculation."""
        assert self.kpi_card._get_pressure_delta_color(3.0) == "normal"  # In good range
        assert self.kpi_card._get_pressure_delta_color(2.2) == "normal"  # In warning range
        assert self.kpi_card._get_pressure_delta_color(1.5) == "inverse"  # Out of range
        assert self.kpi_card._get_pressure_delta_color(5.0) == "inverse"  # Out of range
    
    def test_get_reservoir_delta_color(self):
        """Test reservoir delta color calculation."""
        assert self.kpi_card._get_reservoir_delta_color(80.0) == "normal"
        assert self.kpi_card._get_reservoir_delta_color(60.0) == "normal"
        assert self.kpi_card._get_reservoir_delta_color(40.0) == "inverse"
    
    def test_get_status_info_efficiency(self):
        """Test status info for efficiency metric."""
        status, color = self.kpi_card._get_status_info(96.0, 'efficiency_percentage')
        assert status == "EXCELLENT"
        assert color == "#28a745"
        
        status, color = self.kpi_card._get_status_info(92.0, 'efficiency_percentage')
        assert status == "GOOD"
        assert color == "#ffc107"
        
        status, color = self.kpi_card._get_status_info(88.0, 'efficiency_percentage')
        assert status == "NEEDS ATTENTION"
        assert color == "#dc3545"
    
    def test_get_status_info_loss(self):
        """Test status info for loss metric."""
        status, color = self.kpi_card._get_status_info(8.0, 'loss_m3_per_hour')
        assert status == "EXCELLENT"
        assert color == "#28a745"
        
        status, color = self.kpi_card._get_status_info(12.0, 'loss_m3_per_hour')
        assert status == "ACCEPTABLE"
        assert color == "#ffc107"
        
        status, color = self.kpi_card._get_status_info(18.0, 'loss_m3_per_hour')
        assert status == "HIGH LOSS"
        assert color == "#dc3545"
    
    def test_get_status_info_pressure(self):
        """Test status info for pressure metric."""
        status, color = self.kpi_card._get_status_info(3.0, 'avg_pressure_mh2o')
        assert status == "OPTIMAL"
        assert color == "#28a745"
        
        status, color = self.kpi_card._get_status_info(2.2, 'avg_pressure_mh2o')
        assert status == "ACCEPTABLE"
        assert color == "#ffc107"
        
        status, color = self.kpi_card._get_status_info(1.5, 'avg_pressure_mh2o')
        assert status == "OUT OF RANGE"
        assert color == "#dc3545"
    
    def test_get_status_info_reservoir(self):
        """Test status info for reservoir metric."""
        status, color = self.kpi_card._get_status_info(80.0, 'reservoir_level_percentage')
        assert status == "GOOD LEVEL"
        assert color == "#28a745"
        
        status, color = self.kpi_card._get_status_info(60.0, 'reservoir_level_percentage')
        assert status == "MODERATE"
        assert color == "#ffc107"
        
        status, color = self.kpi_card._get_status_info(40.0, 'reservoir_level_percentage')
        assert status == "LOW LEVEL"
        assert color == "#dc3545"
    
    @patch('streamlit.columns')
    @patch('streamlit.metric')
    def test_render_efficiency_kpis(self, mock_metric, mock_columns):
        """Test rendering efficiency KPIs."""
        mock_columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        
        efficiency_data = {
            'efficiency_percentage': 94.2,
            'loss_m3_per_hour': 12.5,
            'avg_pressure_mh2o': 2.8,
            'reservoir_level_percentage': 78.3,
            'active_nodes': 6,
            'total_nodes': 8
        }
        
        with patch.object(self.kpi_card, '_add_status_indicator') as mock_status:
            self.kpi_card.render_efficiency_kpis(efficiency_data)
            
            # Should call metric 4 times (one for each KPI)
            assert mock_metric.call_count == 4
            
            # Should call status indicator 4 times
            assert mock_status.call_count == 4
            
            # Check metric calls
            calls = mock_metric.call_args_list
            
            # Efficiency card
            assert calls[0][1]['label'] == "🎯 Overall Efficiency"
            assert calls[0][1]['value'] == "94.2%"
            assert "Active nodes: 6/8" in calls[0][1]['delta']
            
            # Loss card
            assert calls[1][1]['label'] == "💧 Water Loss Rate"
            assert calls[1][1]['value'] == "12.5 m³/h"
            
            # Pressure card
            assert calls[2][1]['label'] == "📊 Avg Pressure"
            assert calls[2][1]['value'] == "2.8 mH₂O"
            
            # Reservoir card
            assert calls[3][1]['label'] == "🏗️ Reservoir Level"
            assert calls[3][1]['value'] == "78.3%"
    
    @patch('streamlit.metric')
    def test_render_custom_kpi(self, mock_metric):
        """Test rendering custom KPI."""
        self.kpi_card.render_custom_kpi(
            label="Custom Metric",
            value=42.5,
            unit="units",
            delta_text="Target: 40",
            delta_color="normal",
            icon="🔧"
        )
        
        mock_metric.assert_called_once_with(
            label="🔧 Custom Metric",
            value="42.5 units",
            delta="Target: 40",
            delta_color="normal"
        )
    
    @patch('streamlit.columns')
    def test_render_kpi_grid(self, mock_columns):
        """Test rendering KPI grid."""
        mock_columns.return_value = [Mock(), Mock(), Mock(), Mock()]
        
        kpi_data = {
            'metric1': {
                'label': 'Metric 1',
                'value': 100,
                'unit': '%',
                'delta_text': 'Good',
                'icon': '📈'
            },
            'metric2': {
                'label': 'Metric 2',
                'value': 50,
                'unit': 'units',
                'delta_text': 'Average',
                'icon': '📊'
            }
        }
        
        with patch.object(self.kpi_card, 'render_custom_kpi') as mock_custom:
            self.kpi_card.render_kpi_grid(kpi_data, columns=4)
            
            # Should call render_custom_kpi for each metric
            assert mock_custom.call_count == 2


class TestEfficiencyFilters:
    """Test suite for EfficiencyFilters component."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.efficiency_filters = EfficiencyFilters()
        
    def test_init(self):
        """Test EfficiencyFilters initialization."""
        assert self.efficiency_filters.districts is not None
        assert self.efficiency_filters.nodes_by_district is not None
        assert len(self.efficiency_filters.districts) == 5
        assert "DIST_001" in self.efficiency_filters.districts
        assert "DIST_001" in self.efficiency_filters.nodes_by_district
        assert len(self.efficiency_filters.nodes_by_district["DIST_001"]) == 3
    
    def test_init_session_state(self):
        """Test session state initialization."""
        with patch('streamlit.session_state', new_callable=dict) as mock_session:
            filters = EfficiencyFilters()
            
            # Check that session state keys are set
            assert "efficiency_selected_districts" in mock_session
            assert "efficiency_selected_nodes" in mock_session
            assert "efficiency_filter_mode" in mock_session
            assert mock_session["efficiency_selected_districts"] == []
            assert mock_session["efficiency_selected_nodes"] == []
            assert mock_session["efficiency_filter_mode"] == "district"
    
    def test_reset_filters(self):
        """Test filter reset functionality."""
        with patch('streamlit.session_state', new_callable=dict) as mock_session:
            mock_session["efficiency_selected_districts"] = ["DIST_001"]
            mock_session["efficiency_selected_nodes"] = ["Primary Station"]
            mock_session["efficiency_filter_mode"] = "both"
            
            filters = EfficiencyFilters()
            filters._reset_filters()
            
            assert mock_session["efficiency_selected_districts"] == []
            assert mock_session["efficiency_selected_nodes"] == []
            assert mock_session["efficiency_filter_mode"] == "district"
    
    def test_show_all_data(self):
        """Test show all data functionality."""
        with patch('streamlit.session_state', new_callable=dict) as mock_session:
            filters = EfficiencyFilters()
            filters._show_all_data()
            
            assert len(mock_session["efficiency_selected_districts"]) == 5
            assert len(mock_session["efficiency_selected_nodes"]) == 12  # Total nodes
            assert "Primary Station" in mock_session["efficiency_selected_nodes"]
    
    def test_get_filtered_data_params(self):
        """Test filtered data parameters generation."""
        with patch('streamlit.session_state', new_callable=dict) as mock_session:
            mock_session["efficiency_selected_districts"] = ["DIST_001", "DIST_002"]
            mock_session["efficiency_selected_nodes"] = ["Primary Station", "Secondary Station"]
            
            filters = EfficiencyFilters()
            params = filters.get_filtered_data_params()
            
            assert "districts" in params
            assert "nodes" in params
            assert params["districts"] == "DIST_001,DIST_002"
            assert params["nodes"] == "Primary Station,Secondary Station"
    
    def test_get_filtered_data_params_empty(self):
        """Test filtered data parameters with no selections."""
        with patch('streamlit.session_state', new_callable=dict) as mock_session:
            mock_session["efficiency_selected_districts"] = []
            mock_session["efficiency_selected_nodes"] = []
            
            filters = EfficiencyFilters()
            params = filters.get_filtered_data_params()
            
            assert params == {}
    
    def test_apply_filters_to_data(self):
        """Test applying filters to data."""
        # Create sample data
        data = Mock()
        data.loc = Mock()
        
        with patch('streamlit.session_state', new_callable=dict) as mock_session:
            mock_session["efficiency_selected_districts"] = ["DIST_001"]
            mock_session["efficiency_selected_nodes"] = ["Primary Station"]
            
            filters = EfficiencyFilters()
            
            # Mock the data filtering
            filtered_data = Mock()
            data.__getitem__.return_value.__getitem__.return_value.isin.return_value = Mock()
            data.__getitem__.return_value.__getitem__.return_value.isin.return_value = filtered_data
            
            result = filters.apply_filters_to_data(data)
            
            # Should attempt to filter the data
            assert result is not None
    
    @patch('streamlit.multiselect')
    @patch('streamlit.columns')
    def test_render_compact(self, mock_columns, mock_multiselect):
        """Test compact rendering."""
        mock_columns.return_value = [Mock(), Mock()]
        mock_multiselect.side_effect = [["DIST_001"], ["Primary Station"]]
        
        result = self.efficiency_filters.render_compact()
        
        # Should return selected districts and nodes
        assert result == (["DIST_001"], ["Primary Station"])
        assert mock_multiselect.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__]) 