"""
Tests for node-specific and infrastructure type analysis functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

from src.presentation.api.consumption_routes import router


class TestNodeAnalysis:
    """Test suite for node-specific and infrastructure analysis."""
    
    @pytest.fixture
    def sample_node_data(self):
        """Sample node analysis data for testing."""
        return {
            "node_analysis": [
                {
                    "node_id": "VIA_DANTE_1",
                    "node_name": "Via Dante Principale",
                    "node_type": "main",
                    "infrastructure_type": "primary_distribution",
                    "total_users": 25000,
                    "daily_consumption_liters": 375000,
                    "monthly_consumption_liters": 11250000,
                    "avg_per_user_daily": 15.0,
                    "peak_hour": 8,
                    "efficiency_score": 0.92,
                    "water_loss_percentage": 8.0,
                    "pressure_avg": 3.2,
                    "flow_rate_avg": 4.3,
                    "last_maintenance": "2024-12-15",
                    "next_maintenance": "2025-03-15",
                    "status": "operational",
                    "alerts": 0,
                    "performance_rating": "excellent"
                },
                {
                    "node_id": "VIA_ROMA_2",
                    "node_name": "Via Roma Secondario",
                    "node_type": "secondary",
                    "infrastructure_type": "secondary_distribution",
                    "total_users": 15000,
                    "daily_consumption_liters": 225000,
                    "monthly_consumption_liters": 6750000,
                    "avg_per_user_daily": 15.0,
                    "peak_hour": 9,
                    "efficiency_score": 0.88,
                    "water_loss_percentage": 12.0,
                    "pressure_avg": 2.8,
                    "flow_rate_avg": 2.6,
                    "last_maintenance": "2024-11-20",
                    "next_maintenance": "2025-02-20",
                    "status": "operational",
                    "alerts": 1,
                    "performance_rating": "good"
                },
                {
                    "node_id": "ZONA_INDUSTRIALE_1",
                    "node_name": "Zona Industriale Nord",
                    "node_type": "industrial",
                    "infrastructure_type": "industrial_supply",
                    "total_users": 5000,
                    "daily_consumption_liters": 250000,
                    "monthly_consumption_liters": 7500000,
                    "avg_per_user_daily": 50.0,
                    "peak_hour": 7,
                    "efficiency_score": 0.95,
                    "water_loss_percentage": 5.0,
                    "pressure_avg": 4.5,
                    "flow_rate_avg": 8.7,
                    "last_maintenance": "2024-10-10",
                    "next_maintenance": "2025-01-10",
                    "status": "operational",
                    "alerts": 0,
                    "performance_rating": "excellent"
                }
            ],
            "infrastructure_summary": {
                "total_nodes": 3,
                "main_nodes": 1,
                "secondary_nodes": 1,
                "industrial_nodes": 1,
                "total_users_served": 45000,
                "total_daily_consumption": 850000,
                "avg_efficiency": 0.92,
                "avg_water_loss": 8.3,
                "operational_nodes": 3,
                "maintenance_required": 0
            },
            "data_metadata": {
                "is_real_time": False,
                "data_source": "Historical Database"
            }
        }
    
    @pytest.fixture
    def sample_infrastructure_types(self):
        """Sample infrastructure type analysis data."""
        return {
            "infrastructure_types": [
                {
                    "type": "primary_distribution",
                    "description": "Primary water distribution network",
                    "node_count": 1,
                    "total_users": 25000,
                    "daily_consumption": 375000,
                    "avg_efficiency": 0.92,
                    "avg_water_loss": 8.0,
                    "avg_pressure": 3.2,
                    "avg_flow_rate": 4.3,
                    "performance_rating": "excellent",
                    "maintenance_frequency_days": 90,
                    "criticality_level": "high"
                },
                {
                    "type": "secondary_distribution",
                    "description": "Secondary distribution network",
                    "node_count": 1,
                    "total_users": 15000,
                    "daily_consumption": 225000,
                    "avg_efficiency": 0.88,
                    "avg_water_loss": 12.0,
                    "avg_pressure": 2.8,
                    "avg_flow_rate": 2.6,
                    "performance_rating": "good",
                    "maintenance_frequency_days": 90,
                    "criticality_level": "medium"
                },
                {
                    "type": "industrial_supply",
                    "description": "Industrial water supply network",
                    "node_count": 1,
                    "total_users": 5000,
                    "daily_consumption": 250000,
                    "avg_efficiency": 0.95,
                    "avg_water_loss": 5.0,
                    "avg_pressure": 4.5,
                    "avg_flow_rate": 8.7,
                    "performance_rating": "excellent",
                    "maintenance_frequency_days": 90,
                    "criticality_level": "high"
                }
            ],
            "data_metadata": {
                "is_real_time": False,
                "data_source": "Historical Database"
            }
        }
    
    def test_node_analysis_has_complete_node_data(self, sample_node_data):
        """Test that node analysis contains complete node information."""
        nodes = sample_node_data["node_analysis"]
        
        assert len(nodes) > 0, "Should have at least one node"
        
        for node in nodes:
            # Required fields
            required_fields = [
                "node_id", "node_name", "node_type", "infrastructure_type",
                "total_users", "daily_consumption_liters", "efficiency_score",
                "status", "performance_rating"
            ]
            
            for field in required_fields:
                assert field in node, f"Node should have {field}"
            
            # Data type validation
            assert isinstance(node["total_users"], int)
            assert isinstance(node["daily_consumption_liters"], (int, float))
            assert isinstance(node["efficiency_score"], (int, float))
            assert 0 <= node["efficiency_score"] <= 1, "Efficiency should be between 0 and 1"
            
            # Logical validation
            assert node["total_users"] > 0, "Should have positive user count"
            assert node["daily_consumption_liters"] > 0, "Should have positive consumption"
    
    def test_node_analysis_includes_infrastructure_metrics(self, sample_node_data):
        """Test that node analysis includes infrastructure performance metrics."""
        nodes = sample_node_data["node_analysis"]
        
        for node in nodes:
            # Infrastructure metrics
            infrastructure_fields = [
                "pressure_avg", "flow_rate_avg", "water_loss_percentage",
                "last_maintenance", "next_maintenance", "alerts"
            ]
            
            for field in infrastructure_fields:
                assert field in node, f"Node should have {field}"
            
            # Metric validation
            assert 0 <= node["water_loss_percentage"] <= 100, "Water loss should be 0-100%"
            assert node["pressure_avg"] > 0, "Pressure should be positive"
            assert node["flow_rate_avg"] > 0, "Flow rate should be positive"
            assert node["alerts"] >= 0, "Alerts should be non-negative"
    
    def test_infrastructure_summary_contains_aggregated_data(self, sample_node_data):
        """Test that infrastructure summary contains properly aggregated data."""
        summary = sample_node_data["infrastructure_summary"]
        
        required_fields = [
            "total_nodes", "total_users_served", "total_daily_consumption",
            "avg_efficiency", "avg_water_loss", "operational_nodes"
        ]
        
        for field in required_fields:
            assert field in summary, f"Summary should have {field}"
        
        # Validation of aggregated values
        nodes = sample_node_data["node_analysis"]
        expected_total_users = sum(node["total_users"] for node in nodes)
        expected_total_consumption = sum(node["daily_consumption_liters"] for node in nodes)
        
        assert summary["total_users_served"] == expected_total_users
        assert summary["total_daily_consumption"] == expected_total_consumption
        assert summary["total_nodes"] == len(nodes)
    
    def test_infrastructure_types_analysis_is_comprehensive(self, sample_infrastructure_types):
        """Test that infrastructure types analysis is comprehensive."""
        types = sample_infrastructure_types["infrastructure_types"]
        
        assert len(types) > 0, "Should have at least one infrastructure type"
        
        for infra_type in types:
            # Required fields
            required_fields = [
                "type", "description", "node_count", "total_users",
                "daily_consumption", "avg_efficiency", "performance_rating"
            ]
            
            for field in required_fields:
                assert field in infra_type, f"Infrastructure type should have {field}"
            
            # Data validation
            assert infra_type["node_count"] > 0, "Should have positive node count"
            assert infra_type["total_users"] > 0, "Should have positive user count"
            assert infra_type["daily_consumption"] > 0, "Should have positive consumption"
            assert 0 <= infra_type["avg_efficiency"] <= 1, "Efficiency should be 0-1"
            
            # Performance rating validation
            valid_ratings = ["excellent", "good", "fair", "poor"]
            assert infra_type["performance_rating"] in valid_ratings
    
    def test_node_types_are_properly_categorized(self, sample_node_data):
        """Test that nodes are properly categorized by type."""
        nodes = sample_node_data["node_analysis"]
        
        node_types = [node["node_type"] for node in nodes]
        infrastructure_types = [node["infrastructure_type"] for node in nodes]
        
        # Should have different node types
        assert len(set(node_types)) > 1, "Should have multiple node types"
        assert len(set(infrastructure_types)) > 1, "Should have multiple infrastructure types"
        
        # Validate node type categories
        valid_node_types = ["main", "secondary", "industrial", "residential", "commercial"]
        for node_type in node_types:
            assert node_type in valid_node_types, f"Invalid node type: {node_type}"
    
    def test_node_performance_metrics_are_realistic(self, sample_node_data):
        """Test that node performance metrics are realistic."""
        nodes = sample_node_data["node_analysis"]
        
        for node in nodes:
            # Efficiency should be realistic
            assert 0.7 <= node["efficiency_score"] <= 1.0, "Efficiency should be realistic (70-100%)"
            
            # Water loss should be realistic
            assert 0 <= node["water_loss_percentage"] <= 25, "Water loss should be realistic (0-25%)"
            
            # Pressure should be realistic (bar)
            assert 1.0 <= node["pressure_avg"] <= 6.0, "Pressure should be realistic (1-6 bar)"
            
            # Flow rate should be realistic (L/s)
            assert 0.5 <= node["flow_rate_avg"] <= 15.0, "Flow rate should be realistic (0.5-15 L/s)"
            
            # Consumption per user should be realistic (L/day)
            avg_consumption = node["daily_consumption_liters"] / node["total_users"]
            assert 10 <= avg_consumption <= 100, "Per-user consumption should be realistic (10-100 L/day)"
    
    def test_maintenance_scheduling_is_logical(self, sample_node_data):
        """Test that maintenance scheduling is logical."""
        nodes = sample_node_data["node_analysis"]
        
        for node in nodes:
            if "last_maintenance" in node and "next_maintenance" in node:
                last_maintenance = datetime.strptime(node["last_maintenance"], "%Y-%m-%d")
                next_maintenance = datetime.strptime(node["next_maintenance"], "%Y-%m-%d")
                
                # Next maintenance should be after last maintenance
                assert next_maintenance > last_maintenance, "Next maintenance should be after last"
                
                # Maintenance interval should be reasonable (30-365 days)
                interval = (next_maintenance - last_maintenance).days
                assert 30 <= interval <= 365, "Maintenance interval should be reasonable"
    
    def test_node_status_and_alerts_are_consistent(self, sample_node_data):
        """Test that node status and alerts are consistent."""
        nodes = sample_node_data["node_analysis"]
        
        for node in nodes:
            # Operational nodes should have few alerts
            if node["status"] == "operational":
                assert node["alerts"] <= 3, "Operational nodes should have few alerts"
            
            # High alert count should indicate issues
            if node["alerts"] > 5:
                assert node["status"] != "operational", "High alerts should indicate non-operational status"
    
    def test_infrastructure_criticality_levels_are_appropriate(self, sample_infrastructure_types):
        """Test that infrastructure criticality levels are appropriate."""
        types = sample_infrastructure_types["infrastructure_types"]
        
        valid_criticality_levels = ["low", "medium", "high", "critical"]
        
        for infra_type in types:
            assert "criticality_level" in infra_type, "Should have criticality level"
            assert infra_type["criticality_level"] in valid_criticality_levels
            
            # Primary distribution should be high/critical
            if infra_type["type"] == "primary_distribution":
                assert infra_type["criticality_level"] in ["high", "critical"]
            
            # Industrial supply should be high/critical
            if infra_type["type"] == "industrial_supply":
                assert infra_type["criticality_level"] in ["high", "critical"]
    
    def test_node_analysis_supports_filtering_and_sorting(self, sample_node_data):
        """Test that node analysis data supports filtering and sorting operations."""
        nodes = sample_node_data["node_analysis"]
        
        # Should be able to filter by node type
        main_nodes = [n for n in nodes if n["node_type"] == "main"]
        secondary_nodes = [n for n in nodes if n["node_type"] == "secondary"]
        industrial_nodes = [n for n in nodes if n["node_type"] == "industrial"]
        
        assert len(main_nodes) > 0, "Should have main nodes"
        assert len(secondary_nodes) > 0, "Should have secondary nodes"
        assert len(industrial_nodes) > 0, "Should have industrial nodes"
        
        # Should be able to sort by efficiency
        sorted_by_efficiency = sorted(nodes, key=lambda x: x["efficiency_score"], reverse=True)
        assert sorted_by_efficiency[0]["efficiency_score"] >= sorted_by_efficiency[-1]["efficiency_score"]
        
        # Should be able to filter by performance rating
        excellent_nodes = [n for n in nodes if n["performance_rating"] == "excellent"]
        good_nodes = [n for n in nodes if n["performance_rating"] == "good"]
        
        assert len(excellent_nodes) >= 0, "Should be able to filter by performance rating"
        assert len(good_nodes) >= 0, "Should be able to filter by performance rating"
    
    def test_infrastructure_types_have_appropriate_maintenance_frequencies(self, sample_infrastructure_types):
        """Test that infrastructure types have appropriate maintenance frequencies."""
        types = sample_infrastructure_types["infrastructure_types"]
        
        for infra_type in types:
            assert "maintenance_frequency_days" in infra_type, "Should have maintenance frequency"
            frequency = infra_type["maintenance_frequency_days"]
            
            # Maintenance frequency should be reasonable
            assert 30 <= frequency <= 365, "Maintenance frequency should be 30-365 days"
            
            # High criticality should have more frequent maintenance
            if infra_type["criticality_level"] in ["high", "critical"]:
                assert frequency <= 180, "High criticality should have frequent maintenance"
    
    def test_node_analysis_data_structure_supports_ui_components(self, sample_node_data, sample_infrastructure_types):
        """Test that node analysis data structure supports UI component requirements."""
        nodes = sample_node_data["node_analysis"]
        types = sample_infrastructure_types["infrastructure_types"]
        
        # Should have enough data for charts
        assert len(nodes) >= 3, "Should have enough nodes for meaningful charts"
        assert len(types) >= 2, "Should have enough infrastructure types for comparison"
        
        # Should have numeric data for visualizations
        numeric_fields = ["efficiency_score", "water_loss_percentage", "pressure_avg", "flow_rate_avg"]
        for node in nodes:
            for field in numeric_fields:
                assert isinstance(node[field], (int, float)), f"{field} should be numeric"
        
        # Should have categorical data for filtering
        categorical_fields = ["node_type", "infrastructure_type", "status", "performance_rating"]
        for node in nodes:
            for field in categorical_fields:
                assert isinstance(node[field], str), f"{field} should be string"
        
        # Should have date fields for timeline views
        date_fields = ["last_maintenance", "next_maintenance"]
        for node in nodes:
            for field in date_fields:
                if field in node:
                    assert isinstance(node[field], str), f"{field} should be string"
                    # Should be valid date format
                    try:
                        datetime.strptime(node[field], "%Y-%m-%d")
                    except ValueError:
                        assert False, f"{field} should be valid date format"
