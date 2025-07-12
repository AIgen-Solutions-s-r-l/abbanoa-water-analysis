"""
Unit tests for the ForecastTab component.

Tests component rendering, data handling, and user interactions.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

from src.presentation.streamlit.components.forecast_tab import ForecastTab
from src.presentation.streamlit.utils.data_fetcher import DataFetcher


class TestForecastTab:
    """Test suite for ForecastTab component."""

    @pytest.fixture
    def mock_data_fetcher(self):
        """Create a mock data fetcher."""
        fetcher = Mock(spec=DataFetcher)

        # Mock forecast data
        forecast_data = pd.DataFrame(
            {
                "timestamp": pd.date_range(start=datetime.now(), periods=7, freq="D"),
                "district_id": "DIST_001",
                "metric": "flow_rate",
                "forecast_value": np.random.uniform(90, 110, 7),
                "lower_bound": np.random.uniform(80, 90, 7),
                "upper_bound": np.random.uniform(110, 120, 7),
                "confidence_level": [0.95] * 7,
            }
        )

        # Mock historical data
        historical_data = pd.DataFrame(
            {
                "timestamp": pd.date_range(end=datetime.now(), periods=720, freq="H"),
                "district_id": "DIST_001",
                "metric": "flow_rate",
                "value": np.random.uniform(85, 115, 720),
            }
        )

        fetcher.get_forecast.return_value = forecast_data
        fetcher.get_historical_data.return_value = historical_data

        return fetcher

    @pytest.fixture
    def forecast_tab(self, mock_data_fetcher):
        """Create a ForecastTab instance with mocked dependencies."""
        return ForecastTab(mock_data_fetcher)

    def test_initialization(self, forecast_tab):
        """Test ForecastTab initialization."""
        assert forecast_tab.data_fetcher is not None
        assert forecast_tab.plot_builder is not None

    @patch("streamlit.session_state")
    def test_init_session_state(self, mock_session_state, forecast_tab):
        """Test session state initialization."""
        mock_session_state.__contains__ = Mock(return_value=False)
        mock_session_state.__setitem__ = Mock()

        forecast_tab._init_session_state()

        # Verify session state variables are set
        assert mock_session_state.__setitem__.call_count >= 3

    @patch("streamlit.markdown")
    @patch("streamlit.session_state")
    def test_render_header(self, mock_session_state, mock_markdown, forecast_tab):
        """Test header rendering."""
        mock_session_state.district_id = "DIST_001"
        mock_session_state.metric = "flow_rate"
        mock_session_state.horizon = 7

        forecast_tab._render_header()

        # Verify header is rendered
        assert mock_markdown.call_count >= 1

        # Check that current selection is displayed
        call_args = str(mock_markdown.call_args_list)
        assert "DIST_001" in call_args
        assert "Flow Rate" in call_args

    @patch("streamlit.plotly_chart")
    @patch("streamlit.spinner")
    @patch("streamlit.container")
    def test_render_forecast_chart_with_data(
        self, mock_container, mock_spinner, mock_plotly_chart, forecast_tab
    ):
        """Test forecast chart rendering with data."""
        # Setup mock session state
        with patch("streamlit.session_state") as mock_state:
            mock_state.forecast_data = pd.DataFrame(
                {
                    "timestamp": pd.date_range(
                        start=datetime.now(), periods=7, freq="D"
                    ),
                    "forecast_value": [100] * 7,
                    "lower_bound": [90] * 7,
                    "upper_bound": [110] * 7,
                }
            )
            mock_state.historical_data = pd.DataFrame(
                {
                    "timestamp": pd.date_range(
                        end=datetime.now(), periods=24, freq="H"
                    ),
                    "value": [95] * 24,
                }
            )
            mock_state.district_id = "DIST_001"
            mock_state.metric = "flow_rate"

            # Mock container context manager
            mock_container.return_value.__enter__ = Mock()
            mock_container.return_value.__exit__ = Mock()

            forecast_tab._render_forecast_chart()

            # Verify chart is rendered
            assert mock_plotly_chart.called

    def test_should_fetch_data(self, forecast_tab):
        """Test data fetching logic."""
        with patch("streamlit.session_state") as mock_state:
            # Test when no data exists
            mock_state.forecast_data = None
            assert forecast_tab._should_fetch_data() is True

            # Test when data exists
            mock_state.forecast_data = pd.DataFrame({"data": [1, 2, 3]})
            assert forecast_tab._should_fetch_data() is False

    def test_fetch_forecast_data_caching(self, forecast_tab, mock_data_fetcher):
        """Test that forecast data fetching is cached."""
        # First call
        result1 = forecast_tab._fetch_forecast_data("DIST_001", "flow_rate", 7)

        # Second call with same parameters
        result2 = forecast_tab._fetch_forecast_data("DIST_001", "flow_rate", 7)

        # Should return same object due to caching
        assert result1 is result2

        # Data fetcher should only be called once due to cache
        assert mock_data_fetcher.get_forecast.call_count == 1

    def test_build_forecast_plot(self, forecast_tab):
        """Test forecast plot building."""
        # Create test data
        historical_df = pd.DataFrame(
            {
                "timestamp": pd.date_range(end=datetime.now(), periods=24, freq="H"),
                "value": np.random.uniform(90, 110, 24),
            }
        )

        forecast_df = pd.DataFrame(
            {
                "timestamp": pd.date_range(start=datetime.now(), periods=7, freq="D"),
                "forecast_value": np.random.uniform(95, 105, 7),
                "lower_bound": np.random.uniform(85, 95, 7),
                "upper_bound": np.random.uniform(105, 115, 7),
            }
        )

        with patch("streamlit.session_state") as mock_state:
            mock_state.metric = "flow_rate"
            mock_state.district_id = "DIST_001"

            # Build plot
            fig = forecast_tab._build_forecast_plot(historical_df, forecast_df)

            # Verify plot structure
            assert fig is not None
            assert len(fig.data) >= 2  # At least historical and forecast traces
            assert fig.layout.title.text is not None
            assert "DIST_001" in fig.layout.title.text

    @patch("streamlit.metric")
    @patch("streamlit.info")
    @patch("streamlit.columns")
    def test_render_metrics_cards(
        self, mock_columns, mock_info, mock_metric, forecast_tab
    ):
        """Test metrics cards rendering."""
        # Mock columns
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_columns.return_value = [mock_col1, mock_col2]

        # Setup forecast data
        with patch("streamlit.session_state") as mock_state:
            mock_state.forecast_data = pd.DataFrame(
                {
                    "forecast_value": [100, 102, 104, 106, 108, 110, 112],
                    "lower_bound": [95, 97, 99, 101, 103, 105, 107],
                    "upper_bound": [105, 107, 109, 111, 113, 115, 117],
                }
            )
            mock_state.last_update = datetime.now()

            forecast_tab._render_metrics_cards()

            # Verify metrics are displayed
            assert mock_metric.call_count >= 2
            assert mock_info.call_count >= 1

    @patch("streamlit.download_button")
    def test_render_export_options(self, mock_download_button, forecast_tab):
        """Test export options rendering."""
        with patch("streamlit.session_state") as mock_state:
            mock_state.forecast_data = pd.DataFrame(
                {
                    "timestamp": pd.date_range(
                        start=datetime.now(), periods=7, freq="D"
                    ),
                    "forecast_value": [100] * 7,
                }
            )
            mock_state.district_id = "DIST_001"
            mock_state.metric = "flow_rate"

            forecast_tab._render_export_options()

            # Verify download buttons are created
            assert mock_download_button.call_count >= 2  # CSV and JSON

            # Check CSV export
            csv_call = mock_download_button.call_args_list[0]
            assert "CSV" in csv_call[1]["label"]
            assert csv_call[1]["mime"] == "text/csv"

            # Check JSON export
            json_call = mock_download_button.call_args_list[1]
            assert "JSON" in json_call[1]["label"]
            assert json_call[1]["mime"] == "application/json"

    def test_error_handling(self, forecast_tab):
        """Test error handling in data fetching."""
        with patch("streamlit.error") as mock_error:
            with patch("streamlit.session_state") as mock_state:
                # Simulate error in data fetching
                forecast_tab.data_fetcher.get_forecast.side_effect = Exception(
                    "API Error"
                )

                forecast_tab._fetch_and_cache_data()

                # Verify error is displayed
                mock_error.assert_called_once()
                assert "API Error" in str(mock_error.call_args)

                # Verify empty dataframes are set
                assert isinstance(mock_state.forecast_data, pd.DataFrame)
                assert isinstance(mock_state.historical_data, pd.DataFrame)
