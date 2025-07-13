"""
Pydantic models for Network Efficiency API responses.

These models define the structure of JSON responses returned by the efficiency
endpoints, providing type validation and automatic API documentation.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class EfficiencyMetrics(BaseModel):
    """Network efficiency metrics."""
    
    network_efficiency_percentage: float = Field(..., description="Overall network efficiency percentage")
    total_throughput_m3h: float = Field(..., description="Total system throughput in m³/hour")
    average_pressure_bar: float = Field(..., description="Average system pressure in bar")
    quality_score: float = Field(..., description="Average data quality score (0-1)")
    operational_efficiency: float = Field(..., description="Operational efficiency percentage")
    flow_consistency_score: float = Field(..., description="Flow consistency score (0-1)")


class SystemMetrics(BaseModel):
    """System-wide metrics."""
    
    total_system_volume_m3: float = Field(..., description="Total system volume in m³")
    avg_system_flow_rate: float = Field(..., description="Average system flow rate in L/s")
    avg_system_pressure: float = Field(..., description="Average system pressure in bar")
    avg_system_quality: float = Field(..., description="Average system data quality score")
    active_nodes: int = Field(..., description="Number of active nodes")
    total_readings: int = Field(..., description="Total number of readings")


class NodePerformance(BaseModel):
    """Individual node performance data."""
    
    node_id: str = Field(..., description="Unique node identifier")
    node_name: str = Field(..., description="Human-readable node name")
    node_type: str = Field(..., description="Type of node (e.g., 'meter', 'sensor')")
    reading_count: int = Field(..., description="Number of readings in the time period")
    avg_flow_rate: float = Field(..., description="Average flow rate in L/s")
    avg_pressure: float = Field(..., description="Average pressure in bar")
    avg_temperature: float = Field(..., description="Average temperature in °C")
    total_volume_m3: float = Field(..., description="Total volume processed in m³")
    avg_quality_score: float = Field(..., description="Average quality score (0-1)")
    uptime_percentage: float = Field(..., description="Node uptime percentage")
    first_reading: Optional[str] = Field(None, description="Timestamp of first reading")
    last_reading: Optional[str] = Field(None, description="Timestamp of last reading")


class EfficiencySummary(BaseModel):
    """Summary information for the efficiency analysis."""
    
    time_range: str = Field(..., description="Time range analyzed (e.g., '24h', '7d')")
    period_start: str = Field(..., description="Start of analysis period (ISO 8601)")
    period_end: str = Field(..., description="End of analysis period (ISO 8601)")
    total_nodes: int = Field(..., description="Total number of nodes analyzed")
    active_nodes: int = Field(..., description="Number of active nodes")
    analyzed_hours: int = Field(..., description="Number of hours analyzed")


class ResponseMetadata(BaseModel):
    """Response metadata."""
    
    generated_at: str = Field(..., description="Timestamp when response was generated")
    data_source: str = Field(..., description="Source of the data")
    version: str = Field(..., description="API version")


class EfficiencyResponse(BaseModel):
    """Complete efficiency summary response."""
    
    summary: EfficiencySummary = Field(..., description="Summary information")
    efficiency_metrics: EfficiencyMetrics = Field(..., description="Efficiency metrics")
    system_metrics: SystemMetrics = Field(..., description="System-wide metrics")
    node_performance: List[NodePerformance] = Field(..., description="Individual node performance data")
    metadata: ResponseMetadata = Field(..., description="Response metadata")

    class Config:
        """Pydantic configuration."""
        
        schema_extra = {
            "example": {
                "summary": {
                    "time_range": "24h",
                    "period_start": "2024-01-15T00:00:00Z",
                    "period_end": "2024-01-16T00:00:00Z",
                    "total_nodes": 12,
                    "active_nodes": 10,
                    "analyzed_hours": 24
                },
                "efficiency_metrics": {
                    "network_efficiency_percentage": 87.5,
                    "total_throughput_m3h": 1250.75,
                    "average_pressure_bar": 4.2,
                    "quality_score": 0.95,
                    "operational_efficiency": 83.3,
                    "flow_consistency_score": 0.92
                },
                "system_metrics": {
                    "total_system_volume_m3": 30018.0,
                    "avg_system_flow_rate": 15.8,
                    "avg_system_pressure": 4.2,
                    "avg_system_quality": 0.95,
                    "active_nodes": 10,
                    "total_readings": 240
                },
                "node_performance": [
                    {
                        "node_id": "215542",
                        "node_name": "Main Sensor 215542",
                        "node_type": "meter",
                        "reading_count": 24,
                        "avg_flow_rate": 7.76,
                        "avg_pressure": 6.77,
                        "avg_temperature": 18.5,
                        "total_volume_m3": 669.6,
                        "avg_quality_score": 0.98,
                        "uptime_percentage": 100.0,
                        "first_reading": "2024-01-15T00:00:00Z",
                        "last_reading": "2024-01-15T23:00:00Z"
                    }
                ],
                "metadata": {
                    "generated_at": "2024-01-16T10:30:00Z",
                    "data_source": "sensor_readings_hourly",
                    "version": "1.0"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        """Pydantic configuration."""
        
        schema_extra = {
            "example": {
                "error": "invalid_time_range",
                "message": "Invalid time range: 48h. Must be one of: ['1h', '6h', '24h', '3d', '7d', '30d']",
                "details": {
                    "provided_value": "48h",
                    "valid_values": ["1h", "6h", "24h", "3d", "7d", "30d"]
                }
            }
        } 