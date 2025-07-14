"""
Unit tests for AdvancedFilteringService.

Tests all filtering business logic including complex queries, operators,
and advanced filtering features.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

from src.api.services.filters_service import AdvancedFilteringService
from src.schemas.api.filters import (
    FilterOperator, LogicalOperator, EntityType, FieldFilter, FilterGroup,
    DateRangeFilter, GeographicFilter, FilterPreset, AdvancedFilterRequest,
    FilteredResponse, FilterSchema, FilterSuggestion, FilterAnalytics
)


@pytest.mark.unit
@pytest.mark.filtering
class TestAdvancedFilteringService:
    """Test suite for AdvancedFilteringService."""

    @pytest.fixture
    def filtering_service(self):
        """Provide AdvancedFilteringService instance."""
        return AdvancedFilteringService()

    @pytest.fixture
    def sample_data(self):
        """Provide sample data for filtering tests."""
        return [
            {
                "node_id": "NODE_001",
                "region": "North",
                "consumption_value": 150.0,
                "timestamp": "2024-01-01T10:00:00",
                "zone": "Zone_A"
            },
            {
                "node_id": "NODE_002",
                "region": "South",
                "consumption_value": 200.0,
                "timestamp": "2024-01-01T11:00:00",
                "zone": "Zone_B"
            },
            {
                "node_id": "NODE_003",
                "region": "North",
                "consumption_value": 120.0,
                "timestamp": "2024-01-01T12:00:00",
                "zone": "Zone_A"
            }
        ]

    @pytest.mark.asyncio
    async def test_apply_filters_success(self, filtering_service, sample_data):
        """Test successful filter application."""
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="North"
                )
            ],
            logical_operator=LogicalOperator.AND
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        
        assert isinstance(result, FilteredResponse)
        assert len(result.data) == 2  # Only North region records
        assert all(item["region"] == "North" for item in result.data)

    @pytest.mark.asyncio
    async def test_apply_numeric_filters(self, filtering_service, sample_data):
        """Test numeric filter operations."""
        # Test greater_than filter
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.greater_than,
                    value=140.0
                )
            ]
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 2  # Values > 140
        assert all(item["consumption_value"] > 140 for item in result.data)

        # Test between filter
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.between,
                    value=[120.0, 180.0]
                )
            ]
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 2  # Values between 120-180
        assert all(120 <= item["consumption_value"] <= 180 for item in result.data)

    @pytest.mark.asyncio
    async def test_apply_string_filters(self, filtering_service, sample_data):
        """Test string filter operations."""
        # Test contains filter
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="node_id",
                    operator=FilterOperator.contains,
                    value="001"
                )
            ]
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 1
        assert "001" in result.data[0]["node_id"]

        # Test starts_with filter
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="node_id",
                    operator=FilterOperator.starts_with,
                    value="NODE"
                )
            ]
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 3  # All nodes start with "NODE"

    @pytest.mark.asyncio
    async def test_apply_multiple_filters_and_logic(self, filtering_service, sample_data):
        """Test multiple filters with AND logic."""
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="North"
                ),
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.greater_than,
                    value=130.0
                )
            ],
            logical_operator=LogicalOperator.AND
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 1  # Only NODE_001 matches both conditions

    @pytest.mark.asyncio
    async def test_apply_multiple_filters_or_logic(self, filtering_service, sample_data):
        """Test multiple filters with OR logic."""
        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="South"
                ),
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.greater_than,
                    value=180.0
                )
            ],
            logical_operator=LogicalOperator.OR
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 2  # NODE_002 matches both conditions

    @pytest.mark.asyncio
    async def test_apply_date_range_filter(self, filtering_service, sample_data):
        """Test date range filtering."""
        date_filter = DateRangeFilter(
            field="timestamp",
            start_date=datetime(2024, 1, 1, 10, 30),
            end_date=datetime(2024, 1, 1, 12, 30)
        )

        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            date_filters=[date_filter]
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 2  # Records between 10:30 and 12:30

    @pytest.mark.asyncio
    async def test_apply_geographic_filter(self, filtering_service, sample_data):
        """Test geographic filtering."""
        geo_filter = GeographicFilter(
            field="region",
            regions=["North"],
            zones=["Zone_A"]
        )

        filter_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            geographic_filters=[geo_filter]
        )

        result = await filtering_service.apply_filters(filter_request, sample_data)
        assert len(result.data) == 2  # Records in North region and Zone_A

    @pytest.mark.asyncio
    async def test_validate_filter_request_success(self, filtering_service):
        """Test successful filter request validation."""
        valid_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="North"
                )
            ]
        )

        validation_result = await filtering_service.validate_filter_request(valid_request)
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0

    @pytest.mark.asyncio
    async def test_validate_filter_request_failure(self, filtering_service):
        """Test filter request validation failure."""
        invalid_request = AdvancedFilterRequest(
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="invalid_field",
                    operator=FilterOperator.equals,
                    value="test"
                )
            ]
        )

        validation_result = await filtering_service.validate_filter_request(invalid_request)
        assert validation_result.is_valid is False
        assert len(validation_result.errors) > 0

    @pytest.mark.asyncio
    async def test_save_filter_preset(self, filtering_service):
        """Test saving filter presets."""
        preset = FilterPreset(
            name="North Region High Consumption",
            description="Filter for high consumption in North region",
            entity_type=EntityType.consumption,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="North"
                ),
                FieldFilter(
                    field="consumption_value",
                    operator=FilterOperator.greater_than,
                    value=140.0
                )
            ]
        )

        result = await filtering_service.save_filter_preset(preset)
        assert result.preset_id is not None
        assert result.name == "North Region High Consumption"

    @pytest.mark.asyncio
    async def test_get_filter_preset(self, filtering_service):
        """Test retrieving filter presets."""
        # Mock preset data
        with patch.object(filtering_service, '_get_preset_from_storage') as mock_get:
            mock_preset = FilterPreset(
                preset_id="preset_001",
                name="Test Preset",
                entity_type=EntityType.consumption,
                filters=[]
            )
            mock_get.return_value = mock_preset

            result = await filtering_service.get_filter_preset("preset_001")
            assert result.preset_id == "preset_001"
            assert result.name == "Test Preset"

    @pytest.mark.asyncio
    async def test_get_quick_filters(self, filtering_service):
        """Test retrieving quick filters."""
        result = await filtering_service.get_quick_filters(EntityType.consumption)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(hasattr(qf, 'name') for qf in result)
        assert all(hasattr(qf, 'filters') for qf in result)

    @pytest.mark.asyncio
    async def test_get_filter_suggestions(self, filtering_service, sample_data):
        """Test getting filter suggestions."""
        with patch.object(filtering_service, '_analyze_data_for_suggestions') as mock_analyze:
            mock_suggestions = [
                FilterSuggestion(
                    field="region",
                    suggested_operator=FilterOperator.equals,
                    suggested_values=["North", "South"],
                    reasoning="Common categorical values"
                )
            ]
            mock_analyze.return_value = mock_suggestions

            result = await filtering_service.get_filter_suggestions(
                EntityType.consumption, sample_data
            )
            
            assert isinstance(result, list)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_filter_analytics(self, filtering_service):
        """Test getting filter analytics."""
        with patch.object(filtering_service, '_get_usage_analytics') as mock_analytics:
            mock_analytics.return_value = FilterAnalytics(
                total_filters_applied=150,
                most_used_operators=["equals", "greater_than"],
                most_filtered_fields=["region", "consumption_value"],
                average_results_per_filter=75.5
            )

            result = await filtering_service.get_filter_analytics()
            assert isinstance(result, FilterAnalytics)
            assert result.total_filters_applied == 150

    def test_filter_operator_application(self, filtering_service):
        """Test individual filter operator applications."""
        # Test equals operator
        result = filtering_service._apply_operator(
            "test_value", FilterOperator.equals, "test_value"
        )
        assert result is True

        # Test not_equals operator
        result = filtering_service._apply_operator(
            "test_value", FilterOperator.not_equals, "different_value"
        )
        assert result is True

        # Test greater_than operator
        result = filtering_service._apply_operator(
            150.0, FilterOperator.greater_than, 100.0
        )
        assert result is True

        # Test less_than operator
        result = filtering_service._apply_operator(
            100.0, FilterOperator.less_than, 150.0
        )
        assert result is True

        # Test contains operator
        result = filtering_service._apply_operator(
            "test_string", FilterOperator.contains, "test"
        )
        assert result is True

        # Test in operator
        result = filtering_service._apply_operator(
            "value1", FilterOperator.in_list, ["value1", "value2", "value3"]
        )
        assert result is True

    def test_data_type_validation(self, filtering_service):
        """Test data type validation for filters."""
        # Test numeric field validation
        assert filtering_service._validate_field_type(
            "consumption_value", 150.0, EntityType.consumption
        ) is True

        # Test string field validation
        assert filtering_service._validate_field_type(
            "region", "North", EntityType.consumption
        ) is True

        # Test invalid type
        assert filtering_service._validate_field_type(
            "consumption_value", "invalid_number", EntityType.consumption
        ) is False

    def test_filter_performance_optimization(self, filtering_service):
        """Test filter performance optimization."""
        # Create large dataset
        large_dataset = [
            {
                "node_id": f"NODE_{i:03d}",
                "region": f"Region_{i % 5}",
                "consumption_value": i * 10.0
            }
            for i in range(10000)
        ]

        # Test index creation for frequently filtered fields
        indices = filtering_service._create_field_indices(large_dataset)
        assert "region" in indices
        assert "consumption_value" in indices

        # Test optimized filtering
        optimized_result = filtering_service._apply_optimized_filter(
            large_dataset, "region", FilterOperator.equals, "Region_1"
        )
        assert len(optimized_result) == 2000  # Every 5th record

    def test_filter_caching(self, filtering_service):
        """Test filter result caching."""
        # Test cache key generation
        cache_key = filtering_service._generate_cache_key({
            "field": "region",
            "operator": "equals",
            "value": "North"
        })
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0

        # Test cache storage and retrieval
        test_data = [{"node_id": "NODE_001", "region": "North"}]
        filtering_service._cache_filter_result(cache_key, test_data)
        cached_result = filtering_service._get_cached_filter_result(cache_key)
        assert cached_result == test_data

    def test_complex_nested_filters(self, filtering_service, sample_data):
        """Test complex nested filter groups."""
        filter_group = FilterGroup(
            logical_operator=LogicalOperator.OR,
            filters=[
                FieldFilter(
                    field="region",
                    operator=FilterOperator.equals,
                    value="North"
                )
            ],
            filter_groups=[
                FilterGroup(
                    logical_operator=LogicalOperator.AND,
                    filters=[
                        FieldFilter(
                            field="consumption_value",
                            operator=FilterOperator.greater_than,
                            value=180.0
                        ),
                        FieldFilter(
                            field="zone",
                            operator=FilterOperator.equals,
                            value="Zone_B"
                        )
                    ]
                )
            ]
        )

        result = filtering_service._apply_filter_group(sample_data, filter_group)
        assert len(result) == 3  # All North records + NODE_002 from nested group

    def test_field_discovery(self, filtering_service, sample_data):
        """Test field discovery functionality."""
        fields = filtering_service._discover_fields(sample_data, EntityType.consumption)
        
        expected_fields = ["node_id", "region", "consumption_value", "timestamp", "zone"]
        assert all(field in fields for field in expected_fields)

    def test_value_suggestions(self, filtering_service, sample_data):
        """Test value suggestions for fields."""
        # Test categorical field suggestions
        region_values = filtering_service._get_field_values(sample_data, "region")
        assert "North" in region_values
        assert "South" in region_values

        # Test numeric field suggestions (should provide range)
        consumption_values = filtering_service._get_field_values(sample_data, "consumption_value")
        assert "min" in consumption_values
        assert "max" in consumption_values
        assert "avg" in consumption_values

    @pytest.mark.parametrize("operator", [
        FilterOperator.equals,
        FilterOperator.not_equals,
        FilterOperator.greater_than,
        FilterOperator.less_than,
        FilterOperator.contains,
        FilterOperator.starts_with,
        FilterOperator.ends_with,
        FilterOperator.in_list,
        FilterOperator.not_in_list,
        FilterOperator.between
    ])
    def test_all_filter_operators(self, filtering_service, operator):
        """Test all filter operators individually."""
        # Test data setup based on operator type
        if operator in [FilterOperator.equals, FilterOperator.not_equals]:
            test_value = "test_value"
            comparison_value = "test_value"
        elif operator in [FilterOperator.greater_than, FilterOperator.less_than]:
            test_value = 150.0
            comparison_value = 100.0
        elif operator in [FilterOperator.contains, FilterOperator.starts_with, FilterOperator.ends_with]:
            test_value = "test_string"
            comparison_value = "test"
        elif operator in [FilterOperator.in_list, FilterOperator.not_in_list]:
            test_value = "value1"
            comparison_value = ["value1", "value2"]
        elif operator == FilterOperator.between:
            test_value = 150.0
            comparison_value = [100.0, 200.0]
        else:
            test_value = "default"
            comparison_value = "default"

        # Test operator application
        result = filtering_service._apply_operator(test_value, operator, comparison_value)
        assert isinstance(result, bool)

    def test_error_handling(self, filtering_service):
        """Test error handling in filtering service."""
        # Test invalid operator
        with pytest.raises(ValueError):
            filtering_service._apply_operator("test", "invalid_operator", "test")

        # Test invalid field
        with pytest.raises(ValueError):
            filtering_service._validate_field_type("invalid_field", "test", EntityType.consumption)

        # Test empty filter request
        with pytest.raises(ValueError):
            filtering_service._validate_filter_request(None) 