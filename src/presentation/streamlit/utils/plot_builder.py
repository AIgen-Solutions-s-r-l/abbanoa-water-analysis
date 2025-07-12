"""
Plot builder utility for creating consistent Plotly visualizations.

This module provides reusable functions for building various types
of plots used throughout the dashboard.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PlotBuilder:
    """Utility class for building Plotly visualizations."""

    def __init__(self):
        """Initialize the plot builder with default settings."""
        self.default_colors = {
            "primary": "#1f77b4",
            "secondary": "#ff7f0e",
            "success": "#2ca02c",
            "warning": "#ff7f0e",
            "danger": "#d62728",
            "historical": "#1f77b4",
            "forecast": "#ff7f0e",
            "confidence": "rgba(255, 127, 14, 0.2)",
        }

        self.default_layout = {
            "template": "plotly_white",
            "font": {"family": "Inter, sans-serif"},
            "margin": {"l": 50, "r": 50, "t": 80, "b": 50},
            "hovermode": "x unified",
            "plot_bgcolor": "white",
            "paper_bgcolor": "white",
        }

    def build_forecast_plot(
        self,
        historical_df: Optional[pd.DataFrame],
        forecast_df: pd.DataFrame,
        metric: str,
        district_id: str,
        show_confidence: bool = True,
        confidence_level: float = 0.80,
    ) -> go.Figure:
        """
        Build a forecast plot with historical context and confidence intervals.

        Args:
            historical_df: Historical data DataFrame
            forecast_df: Forecast data DataFrame
            metric: Metric type for labeling
            district_id: District identifier
            show_confidence: Whether to show confidence intervals
            confidence_level: Confidence level (0.80 for 80%)

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        # Add historical data if available
        if historical_df is not None and not historical_df.empty:
            fig.add_trace(self._create_historical_trace(historical_df))

        # Add forecast trace
        fig.add_trace(self._create_forecast_trace(forecast_df))

        # Add confidence interval if requested
        if show_confidence and "lower_bound" in forecast_df.columns:
            upper_trace, lower_trace = self._create_confidence_traces(
                forecast_df, confidence_level
            )
            fig.add_trace(upper_trace)
            fig.add_trace(lower_trace)

        # Add vertical line for current time
        fig.add_vline(
            x=datetime.now(),
            line_dash="dot",
            line_color="gray",
            annotation_text="Now",
            annotation_position="top",
        )

        # Update layout
        layout = self._create_forecast_layout(metric, district_id)
        fig.update_layout(layout)

        return fig

    def build_comparison_plot(
        self, data_dict: Dict[str, pd.DataFrame], metric: str, plot_type: str = "line"
    ) -> go.Figure:
        """
        Build a comparison plot for multiple districts or metrics.

        Args:
            data_dict: Dictionary mapping labels to DataFrames
            metric: Metric type for labeling
            plot_type: Type of plot ('line', 'bar', 'scatter')

        Returns:
            Plotly figure object
        """
        fig = go.Figure()

        colors = px.colors.qualitative.Set2

        for idx, (label, df) in enumerate(data_dict.items()):
            color = colors[idx % len(colors)]

            if plot_type == "line":
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df["value"],
                        mode="lines",
                        name=label,
                        line=dict(color=color, width=2),
                    )
                )
            elif plot_type == "bar":
                fig.add_trace(
                    go.Bar(
                        x=df["timestamp"], y=df["value"], name=label, marker_color=color
                    )
                )
            elif plot_type == "scatter":
                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=df["value"],
                        mode="markers",
                        name=label,
                        marker=dict(color=color, size=8),
                    )
                )

        # Update layout
        fig.update_layout(
            **self.default_layout,
            title=f"{metric} Comparison",
            xaxis_title="Date",
            yaxis_title=self._get_metric_label(metric),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        return fig

    def build_metric_cards_plot(
        self,
        metrics: Dict[str, float],
        previous_metrics: Optional[Dict[str, float]] = None,
    ) -> go.Figure:
        """
        Build a plot for metric cards visualization.

        Args:
            metrics: Current metric values
            previous_metrics: Previous metric values for comparison

        Returns:
            Plotly figure object
        """
        # Create subplots for metric cards
        fig = make_subplots(
            rows=1,
            cols=len(metrics),
            subplot_titles=list(metrics.keys()),
            specs=[[{"type": "indicator"} for _ in metrics]],
        )

        for idx, (metric_name, value) in enumerate(metrics.items()):
            delta = None
            if previous_metrics and metric_name in previous_metrics:
                delta = {"reference": previous_metrics[metric_name], "relative": True}

            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=value,
                    delta=delta,
                    domain={
                        "x": [idx / len(metrics), (idx + 1) / len(metrics)],
                        "y": [0, 1],
                    },
                ),
                row=1,
                col=idx + 1,
            )

        fig.update_layout(height=200, margin=dict(l=20, r=20, t=50, b=20))

        return fig

    def _create_historical_trace(self, df: pd.DataFrame) -> go.Scatter:
        """Create a trace for historical data."""
        return go.Scatter(
            x=df["timestamp"],
            y=df["value"],
            mode="lines",
            name="Historical",
            line=dict(color=self.default_colors["historical"], width=2),
            hovertemplate="<b>Historical</b><br>"
            + "Date: %{x|%Y-%m-%d %H:%M}<br>"
            + "Value: %{y:.2f}<br>"
            + "<extra></extra>",
        )

    def _create_forecast_trace(self, df: pd.DataFrame) -> go.Scatter:
        """Create a trace for forecast data."""
        return go.Scatter(
            x=df["timestamp"],
            y=df["forecast_value"],
            mode="lines+markers",
            name="Forecast",
            line=dict(color=self.default_colors["forecast"], width=2, dash="dash"),
            marker=dict(size=6),
            hovertemplate="<b>Forecast</b><br>"
            + "Date: %{x|%Y-%m-%d}<br>"
            + "Value: %{y:.2f}<br>"
            + "<extra></extra>",
        )

    def _create_confidence_traces(
        self, df: pd.DataFrame, confidence_level: float
    ) -> Tuple[go.Scatter, go.Scatter]:
        """Create traces for confidence interval bands."""
        # Convert confidence level if needed
        if confidence_level == 0.80 and df["confidence_level"].iloc[0] == 0.95:
            # Convert 95% CI to 80% CI
            forecast_mean = df["forecast_value"]
            ci_95_width = (df["upper_bound"] - df["lower_bound"]) / 2
            ci_80_width = ci_95_width * 0.84  # 80% CI is ~84% of 95% CI width

            lower_bound = forecast_mean - ci_80_width
            upper_bound = forecast_mean + ci_80_width
        else:
            lower_bound = df["lower_bound"]
            upper_bound = df["upper_bound"]

        # Upper bound (invisible)
        upper_trace = go.Scatter(
            x=df["timestamp"],
            y=upper_bound,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        )

        # Lower bound with fill
        lower_trace = go.Scatter(
            x=df["timestamp"],
            y=lower_bound,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor=self.default_colors["confidence"],
            name=f"{int(confidence_level*100)}% Confidence Interval",
            hovertemplate="<b>Confidence Interval</b><br>"
            + "Date: %{x|%Y-%m-%d}<br>"
            + "Lower: %{y:.2f}<br>"
            + "<extra></extra>",
        )

        return upper_trace, lower_trace

    def _create_forecast_layout(self, metric: str, district_id: str) -> Dict[str, Any]:
        """Create layout for forecast plot."""
        layout = self.default_layout.copy()
        layout.update(
            {
                "title": {
                    "text": f"7-Day Forecast: {district_id} - {self._get_metric_label(metric)}",
                    "x": 0.5,
                    "xanchor": "center",
                    "font": {"size": 20},
                },
                "xaxis_title": "Date",
                "yaxis_title": self._get_metric_label(metric),
                "height": 500,
                "legend": dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
                "xaxis": dict(rangeslider=dict(visible=False), type="date"),
                "yaxis": dict(fixedrange=False),
            }
        )
        return layout

    def _get_metric_label(self, metric: str) -> str:
        """Get formatted label for metric."""
        labels = {
            "flow_rate": "Flow Rate (L/s)",
            "reservoir_level": "Reservoir Level (m)",
            "pressure": "Pressure (bar)",
        }
        return labels.get(metric, metric.replace("_", " ").title())
