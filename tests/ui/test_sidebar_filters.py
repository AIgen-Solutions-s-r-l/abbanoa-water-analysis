"""
Unit tests for the SidebarFilters component.

Tests sidebar rendering, filter interactions, and state management.
"""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from src.presentation.streamlit.components.sidebar_filters import SidebarFilters


class TestSidebarFilters:
    """Test suite for SidebarFilters component."""

    @pytest.fixture
    def sidebar_filters(self):
        """Create a SidebarFilters instance."""
        return SidebarFilters()

    def test_initialization(self, sidebar_filters):
        """Test SidebarFilters initialization."""
        assert sidebar_filters.districts == ["DIST_001", "DIST_002", "DIST_003"]
        assert len(sidebar_filters.metrics) == 3
        assert "flow_rate" in sidebar_filters.metrics
        assert "pressure" in sidebar_filters.metrics
        assert "reservoir_level" in sidebar_filters.metrics

    @patch("streamlit.sidebar")
    @patch("streamlit.markdown")
    def test_render_calls_all_components(
        self, mock_markdown, mock_sidebar, sidebar_filters
    ):
        """Test that render method calls all component methods."""
        # Create a mock context manager for sidebar
        mock_sidebar_context = MagicMock()
        mock_sidebar.__enter__ = Mock(return_value=mock_sidebar_context)
        mock_sidebar.__exit__ = Mock(return_value=None)

        # Mock all render methods
        sidebar_filters._render_district_selector = Mock()
        sidebar_filters._render_metric_selector = Mock()
        sidebar_filters._render_horizon_selector = Mock()
        sidebar_filters._render_additional_options = Mock()
        sidebar_filters._render_info_section = Mock()

        sidebar_filters.render()

        # Verify all components are rendered
        assert sidebar_filters._render_district_selector.called
        assert sidebar_filters._render_metric_selector.called
        assert sidebar_filters._render_horizon_selector.called
        assert sidebar_filters._render_additional_options.called
        assert sidebar_filters._render_info_section.called

    @patch("streamlit.selectbox")
    @patch("streamlit.session_state")
    def test_render_district_selector(
        self, mock_session_state, mock_selectbox, sidebar_filters
    ):
        """Test district selector rendering."""
        mock_session_state.district_id = "DIST_001"

        sidebar_filters._render_district_selector()

        # Verify selectbox is created
        mock_selectbox.assert_called_once()
        call_kwargs = mock_selectbox.call_args[1]

        assert call_kwargs["label"] == "Select District"
        assert call_kwargs["options"] == ["DIST_001", "DIST_002", "DIST_003"]
        assert call_kwargs["index"] == 0  # DIST_001 is at index 0
        assert call_kwargs["key"] == "district_selector"
        assert callable(call_kwargs["on_change"])

    @patch("streamlit.selectbox")
    @patch("streamlit.session_state")
    def test_render_metric_selector(
        self, mock_session_state, mock_selectbox, sidebar_filters
    ):
        """Test metric selector rendering."""
        mock_session_state.metric = "flow_rate"

        sidebar_filters._render_metric_selector()

        # Verify selectbox is created with formatted labels
        mock_selectbox.assert_called_once()
        call_kwargs = mock_selectbox.call_args[1]

        assert call_kwargs["label"] == "Select Metric"
        assert "Flow Rate (L/s)" in call_kwargs["options"]
        assert call_kwargs["key"] == "metric_selector"
        assert callable(call_kwargs["on_change"])

    @patch("streamlit.slider")
    @patch("streamlit.caption")
    @patch("streamlit.session_state")
    def test_render_horizon_selector(
        self, mock_session_state, mock_caption, mock_slider, sidebar_filters
    ):
        """Test horizon slider rendering."""
        mock_session_state.horizon = 7
        mock_slider.return_value = 7

        sidebar_filters._render_horizon_selector()

        # Verify slider is created
        mock_slider.assert_called_once()
        call_kwargs = mock_slider.call_args[1]

        assert call_kwargs["label"] == "Forecast Horizon (days)"
        assert call_kwargs["min_value"] == 1
        assert call_kwargs["max_value"] == 7
        assert call_kwargs["value"] == 7
        assert call_kwargs["step"] == 1
        assert call_kwargs["key"] == "horizon_slider"

        # Verify caption is displayed
        mock_caption.assert_called_once_with("Forecasting 7 days ahead")

    @patch("streamlit.checkbox")
    @patch("streamlit.info")
    def test_render_additional_options(self, mock_info, mock_checkbox, sidebar_filters):
        """Test additional options rendering."""
        # Set return values for checkboxes
        mock_checkbox.side_effect = [True, True, True]  # All options enabled

        sidebar_filters._render_additional_options()

        # Verify checkboxes are created
        assert mock_checkbox.call_count == 3

        # Check confidence interval checkbox
        ci_call = mock_checkbox.call_args_list[0]
        assert ci_call[0][0] == "Show Confidence Interval"
        assert ci_call[1]["key"] == "show_confidence_interval"

        # Check historical data checkbox
        hist_call = mock_checkbox.call_args_list[1]
        assert hist_call[0][0] == "Show Historical Data"
        assert hist_call[1]["key"] == "show_historical"

        # Check auto-refresh checkbox
        refresh_call = mock_checkbox.call_args_list[2]
        assert refresh_call[0][0] == "Auto-refresh (5 min)"
        assert refresh_call[1]["key"] == "auto_refresh"

        # Verify info is shown when auto-refresh is enabled
        mock_info.assert_called_once_with("Auto-refresh enabled")

    @patch("streamlit.expander")
    @patch("streamlit.markdown")
    @patch("streamlit.metric")
    @patch("streamlit.columns")
    def test_render_info_section(
        self, mock_columns, mock_metric, mock_markdown, mock_expander, sidebar_filters
    ):
        """Test info section rendering."""
        # Mock expander context manager
        mock_expander_context = MagicMock()
        mock_expander.return_value.__enter__ = Mock(return_value=mock_expander_context)
        mock_expander.return_value.__exit__ = Mock(return_value=None)

        # Mock columns
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_columns.return_value = [mock_col1, mock_col2]

        sidebar_filters._render_info_section()

        # Verify expanders are created
        assert mock_expander.call_count == 3

        # Check expander titles
        expander_calls = [call[0][0] for call in mock_expander.call_args_list]
        assert "Model Information" in expander_calls
        assert "How to Use" in expander_calls
        assert "System Performance" in expander_calls

    @patch("streamlit.session_state")
    def test_on_district_change(self, mock_session_state, sidebar_filters):
        """Test district change callback."""
        # Setup initial state
        mock_session_state.district_selector = "DIST_002"
        mock_session_state.district_id = "DIST_001"
        mock_session_state.forecast_data = "some_data"
        mock_session_state.historical_data = "some_data"

        sidebar_filters._on_district_change()

        # Verify state is updated
        assert mock_session_state.district_id == "DIST_002"
        assert mock_session_state.forecast_data is None
        assert mock_session_state.historical_data is None

    @patch("streamlit.session_state")
    def test_on_metric_change(self, mock_session_state, sidebar_filters):
        """Test metric change callback."""
        # Setup initial state
        mock_session_state.metric_selector = "Pressure (bar)"
        mock_session_state.metric = "flow_rate"
        mock_session_state.forecast_data = "some_data"
        mock_session_state.historical_data = "some_data"

        sidebar_filters._on_metric_change()

        # Verify state is updated
        assert mock_session_state.metric == "pressure"
        assert mock_session_state.forecast_data is None
        assert mock_session_state.historical_data is None

    @patch("streamlit.session_state")
    def test_on_horizon_change(self, mock_session_state, sidebar_filters):
        """Test horizon change callback."""
        # Setup initial state
        mock_session_state.horizon_slider = 5
        mock_session_state.horizon = 7
        mock_session_state.forecast_data = "some_data"

        sidebar_filters._on_horizon_change()

        # Verify state is updated
        assert mock_session_state.horizon == 5
        assert mock_session_state.forecast_data is None

    @patch("streamlit.session_state")
    def test_state_persistence(self, mock_session_state, sidebar_filters):
        """Test that filter state persists without causing reloads."""
        # Setup state
        mock_session_state.district_id = "DIST_001"
        mock_session_state.metric = "flow_rate"
        mock_session_state.horizon = 7
        mock_session_state.forecast_data = pd.DataFrame({"data": [1, 2, 3]})

        # Same values selected - should not clear data
        mock_session_state.district_selector = "DIST_001"
        sidebar_filters._on_district_change()

        # Data should not be cleared if value didn't change
        assert mock_session_state.forecast_data is not None
