"""
KpiCard component for displaying network efficiency metrics.

This component provides a reusable way to display KPI cards with consistent
styling, delta indicators, and proper units for efficiency metrics.
"""

from typing import Dict, Any, Optional, Union
import streamlit as st
from datetime import datetime


class KpiCard:
    """
    Reusable KPI card component for efficiency metrics.
    
    Features:
    - Consistent styling across all KPI cards
    - Delta indicators with color coding
    - Proper units for different metric types
    - Threshold-based status indicators
    - Configurable colors and styling
    """
    
    def __init__(self):
        """Initialize the KpiCard component."""
        self.default_thresholds = {
            'efficiency_percentage': {'good': 95.0, 'warning': 90.0},
            'loss_m3_per_hour': {'good': 10.0, 'warning': 15.0},
            'avg_pressure_mh2o': {'good_min': 2.5, 'good_max': 3.5, 'warning_min': 2.0, 'warning_max': 4.0},
            'reservoir_level_percentage': {'good': 70.0, 'warning': 50.0}
        }
    
    def render_efficiency_kpis(self, efficiency_data: Dict[str, Any]) -> None:
        """
        Render the standard efficiency KPI cards.
        
        Args:
            efficiency_data: Dictionary containing efficiency metrics
        """
        
        # Create four columns for the KPI cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self._render_efficiency_card(efficiency_data)
        
        with col2:
            self._render_loss_card(efficiency_data)
        
        with col3:
            self._render_pressure_card(efficiency_data)
        
        with col4:
            self._render_reservoir_card(efficiency_data)
    
    def _render_efficiency_card(self, data: Dict[str, Any]) -> None:
        """Render the efficiency percentage KPI card."""
        efficiency_pct = data.get('efficiency_percentage', 0)
        active_nodes = data.get('active_nodes', 0)
        total_nodes = data.get('total_nodes', 8)
        
        # Determine status color
        delta_color = self._get_efficiency_delta_color(efficiency_pct)
        
        # Format delta text
        delta_text = f"Active nodes: {active_nodes}/{total_nodes}"
        
        st.metric(
            label="🎯 Overall Efficiency",
            value=f"{efficiency_pct:.1f}%",
            delta=delta_text,
            delta_color=delta_color
        )
        
        # Add status indicator
        self._add_status_indicator(efficiency_pct, 'efficiency_percentage')
    
    def _render_loss_card(self, data: Dict[str, Any]) -> None:
        """Render the water loss KPI card."""
        loss_m3h = data.get('loss_m3_per_hour', 0)
        loss_pct = data.get('loss_percentage', 0)
        
        # Determine status color
        delta_color = self._get_loss_delta_color(loss_m3h)
        
        # Format delta text
        delta_text = f"Loss: {loss_pct:.1f}%"
        
        st.metric(
            label="💧 Water Loss Rate",
            value=f"{loss_m3h:.1f} m³/h",
            delta=delta_text,
            delta_color=delta_color
        )
        
        # Add status indicator
        self._add_status_indicator(loss_m3h, 'loss_m3_per_hour')
    
    def _render_pressure_card(self, data: Dict[str, Any]) -> None:
        """Render the pressure KPI card."""
        avg_pressure = data.get('avg_pressure_mh2o', 0)
        
        # Determine status color
        delta_color = self._get_pressure_delta_color(avg_pressure)
        
        # Format delta text
        delta_text = "Optimal: 2.5-3.5 mH₂O"
        
        st.metric(
            label="📊 Avg Pressure",
            value=f"{avg_pressure:.1f} mH₂O",
            delta=delta_text,
            delta_color=delta_color
        )
        
        # Add status indicator
        self._add_status_indicator(avg_pressure, 'avg_pressure_mh2o')
    
    def _render_reservoir_card(self, data: Dict[str, Any]) -> None:
        """Render the reservoir level KPI card."""
        reservoir_level = data.get('reservoir_level_percentage', 0)
        last_updated = data.get('last_updated', datetime.now().isoformat())
        
        # Determine status color
        delta_color = self._get_reservoir_delta_color(reservoir_level)
        
        # Format delta text
        delta_text = "Target: >70%"
        
        st.metric(
            label="🏗️ Reservoir Level",
            value=f"{reservoir_level:.1f}%",
            delta=delta_text,
            delta_color=delta_color
        )
        
        # Add status indicator
        self._add_status_indicator(reservoir_level, 'reservoir_level_percentage')
    
    def _get_efficiency_delta_color(self, efficiency: float) -> str:
        """Get delta color for efficiency metric."""
        thresholds = self.default_thresholds['efficiency_percentage']
        if efficiency >= thresholds['good']:
            return "normal"
        elif efficiency >= thresholds['warning']:
            return "normal"
        else:
            return "inverse"
    
    def _get_loss_delta_color(self, loss: float) -> str:
        """Get delta color for loss metric."""
        thresholds = self.default_thresholds['loss_m3_per_hour']
        if loss <= thresholds['good']:
            return "normal"
        elif loss <= thresholds['warning']:
            return "normal"
        else:
            return "inverse"
    
    def _get_pressure_delta_color(self, pressure: float) -> str:
        """Get delta color for pressure metric."""
        thresholds = self.default_thresholds['avg_pressure_mh2o']
        if thresholds['good_min'] <= pressure <= thresholds['good_max']:
            return "normal"
        elif thresholds['warning_min'] <= pressure <= thresholds['warning_max']:
            return "normal"
        else:
            return "inverse"
    
    def _get_reservoir_delta_color(self, reservoir: float) -> str:
        """Get delta color for reservoir metric."""
        thresholds = self.default_thresholds['reservoir_level_percentage']
        if reservoir >= thresholds['good']:
            return "normal"
        elif reservoir >= thresholds['warning']:
            return "normal"
        else:
            return "inverse"
    
    def _add_status_indicator(self, value: float, metric_type: str) -> None:
        """Add a status indicator below the KPI card."""
        status, color = self._get_status_info(value, metric_type)
        
        # Create a small status indicator
        st.markdown(
            f"""
            <div style="
                text-align: center;
                padding: 2px 8px;
                margin-top: 5px;
                border-radius: 12px;
                background-color: {color};
                color: white;
                font-size: 12px;
                font-weight: bold;
            ">
                {status}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def _get_status_info(self, value: float, metric_type: str) -> tuple[str, str]:
        """Get status text and color for a metric."""
        thresholds = self.default_thresholds.get(metric_type, {})
        
        if metric_type == 'efficiency_percentage':
            if value >= thresholds.get('good', 95.0):
                return "EXCELLENT", "#28a745"
            elif value >= thresholds.get('warning', 90.0):
                return "GOOD", "#ffc107"
            else:
                return "NEEDS ATTENTION", "#dc3545"
        
        elif metric_type == 'loss_m3_per_hour':
            if value <= thresholds.get('good', 10.0):
                return "EXCELLENT", "#28a745"
            elif value <= thresholds.get('warning', 15.0):
                return "ACCEPTABLE", "#ffc107"
            else:
                return "HIGH LOSS", "#dc3545"
        
        elif metric_type == 'avg_pressure_mh2o':
            good_min = thresholds.get('good_min', 2.5)
            good_max = thresholds.get('good_max', 3.5)
            warning_min = thresholds.get('warning_min', 2.0)
            warning_max = thresholds.get('warning_max', 4.0)
            
            if good_min <= value <= good_max:
                return "OPTIMAL", "#28a745"
            elif warning_min <= value <= warning_max:
                return "ACCEPTABLE", "#ffc107"
            else:
                return "OUT OF RANGE", "#dc3545"
        
        elif metric_type == 'reservoir_level_percentage':
            if value >= thresholds.get('good', 70.0):
                return "GOOD LEVEL", "#28a745"
            elif value >= thresholds.get('warning', 50.0):
                return "MODERATE", "#ffc107"
            else:
                return "LOW LEVEL", "#dc3545"
        
        return "UNKNOWN", "#6c757d"
    
    def render_custom_kpi(
        self,
        label: str,
        value: Union[float, int, str],
        unit: str = "",
        delta_text: Optional[str] = None,
        delta_color: str = "normal",
        icon: str = "📊",
        status_color: Optional[str] = None
    ) -> None:
        """
        Render a custom KPI card.
        
        Args:
            label: KPI label
            value: KPI value
            unit: Value unit
            delta_text: Delta text to display
            delta_color: Delta color ("normal", "inverse", "off")
            icon: Icon to display with label
            status_color: Optional status indicator color
        """
        
        # Format value with unit
        if isinstance(value, (int, float)):
            if unit:
                display_value = f"{value:.1f} {unit}"
            else:
                display_value = f"{value:.1f}"
        else:
            display_value = str(value)
        
        # Display metric
        st.metric(
            label=f"{icon} {label}",
            value=display_value,
            delta=delta_text,
            delta_color=delta_color
        )
        
        # Add custom status indicator if provided
        if status_color:
            st.markdown(
                f"""
                <div style="
                    text-align: center;
                    padding: 2px 8px;
                    margin-top: 5px;
                    border-radius: 12px;
                    background-color: {status_color};
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                ">
                    CUSTOM STATUS
                </div>
                """,
                unsafe_allow_html=True
            )
    
    def render_kpi_grid(self, kpi_data: Dict[str, Dict[str, Any]], columns: int = 4) -> None:
        """
        Render a grid of KPI cards.
        
        Args:
            kpi_data: Dictionary of KPI data {kpi_name: {value, unit, delta_text, etc.}}
            columns: Number of columns in the grid
        """
        
        # Create columns
        cols = st.columns(columns)
        
        for i, (kpi_name, kpi_config) in enumerate(kpi_data.items()):
            with cols[i % columns]:
                self.render_custom_kpi(
                    label=kpi_config.get('label', kpi_name),
                    value=kpi_config.get('value', 0),
                    unit=kpi_config.get('unit', ''),
                    delta_text=kpi_config.get('delta_text'),
                    delta_color=kpi_config.get('delta_color', 'normal'),
                    icon=kpi_config.get('icon', '📊'),
                    status_color=kpi_config.get('status_color')
                ) 