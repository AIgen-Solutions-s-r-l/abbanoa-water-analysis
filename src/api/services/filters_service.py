"""
Advanced Filtering Service.

This service provides comprehensive filtering capabilities across all data entities,
including dynamic filtering, sorting, pagination, presets, and analytics.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
import pandas as pd

from src.schemas.api.filters import (
    AdvancedFilterRequest, FilteredResponse, FilterGroup, FieldFilter,
    DateRangeFilter, GeographicFilter, FilterOperator, LogicalOperator,
    FilterValidationResult, FilterMetadata, FilterPreset, FilterSchema,
    FilterField, FilterDataType, SortCriteria, SortDirection,
    FilterSuggestion, FilterAnalytics, QuickFilter, EntityType,
    FilterExportRequest, FilterImportRequest, PaginationOptions
)
from src.infrastructure.data.hybrid_data_service import HybridDataService

logger = logging.getLogger(__name__)


class AdvancedFilteringService:
    """Service for advanced filtering operations across all entities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._filter_schemas = self._initialize_filter_schemas()
        self._quick_filters = self._initialize_quick_filters()
    
    async def apply_advanced_filter(
        self,
        hybrid_service: HybridDataService,
        filter_request: AdvancedFilterRequest
    ) -> FilteredResponse:
        """Apply advanced filtering to specified entity."""
        start_time = time.time()
        
        try:
            # Validate filter request
            validation = await self.validate_filter_request(filter_request)
            if not validation.is_valid:
                raise ValueError(f"Invalid filter request: {validation.errors}")
            
            # Load preset if specified
            if filter_request.preset_id:
                preset = await self.get_filter_preset(hybrid_service, filter_request.preset_id)
                if preset:
                    filter_request = self._merge_preset_with_request(preset, filter_request)
            
            # Get base data from appropriate entity
            base_data = await self._get_entity_data(
                hybrid_service, filter_request.entity_type
            )
            
            # Apply filters
            filtered_data = self._apply_filters(base_data, filter_request)
            
            # Apply sorting
            if filter_request.sort_criteria:
                filtered_data = self._apply_sorting(filtered_data, filter_request.sort_criteria)
            
            # Apply pagination
            total_count = len(filtered_data)
            paginated_data, pagination_metadata = self._apply_pagination(
                filtered_data, filter_request.pagination
            )
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000
            
            # Build metadata
            metadata = FilterMetadata(
                total_count=len(base_data),
                filtered_count=total_count,
                page_count=pagination_metadata["page_count"],
                current_page=filter_request.pagination.page,
                has_next_page=pagination_metadata["has_next_page"],
                has_previous_page=pagination_metadata["has_previous_page"],
                execution_time_ms=execution_time,
                applied_filters_count=self._count_applied_filters(filter_request)
            )
            
            # Generate suggestions
            suggestions = await self._generate_filter_suggestions(
                hybrid_service, filter_request.entity_type, filtered_data
            )
            
            return FilteredResponse(
                data=paginated_data,
                metadata=metadata,
                applied_filters=filter_request.filters,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Error applying advanced filter: {str(e)}")
            raise
    
    async def validate_filter_request(
        self, filter_request: AdvancedFilterRequest
    ) -> FilterValidationResult:
        """Validate filter request structure and values."""
        errors = []
        warnings = []
        
        try:
            # Validate entity type
            if filter_request.entity_type not in [e.value for e in EntityType]:
                errors.append(f"Invalid entity type: {filter_request.entity_type}")
            
            # Validate filter groups
            if filter_request.filters:
                filter_errors = self._validate_filter_group(filter_request.filters)
                errors.extend(filter_errors)
            
            # Validate date range
            if filter_request.date_range:
                date_errors = self._validate_date_range(filter_request.date_range)
                errors.extend(date_errors)
            
            # Validate geographic filter
            if filter_request.geographic:
                geo_errors = self._validate_geographic_filter(filter_request.geographic)
                errors.extend(geo_errors)
            
            # Validate sort criteria
            if filter_request.sort_criteria:
                sort_errors = self._validate_sort_criteria(
                    filter_request.sort_criteria, filter_request.entity_type
                )
                errors.extend(sort_errors)
            
            # Check for performance warnings
            if filter_request.pagination and filter_request.pagination.page_size > 500:
                warnings.append("Large page size may impact performance")
            
            return FilterValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.error(f"Error validating filter request: {str(e)}")
            return FilterValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[]
            )
    
    async def get_filter_schema(self, entity_type: EntityType) -> FilterSchema:
        """Get filter schema for specified entity type."""
        try:
            return self._filter_schemas.get(entity_type, self._get_default_schema(entity_type))
        except Exception as e:
            self.logger.error(f"Error getting filter schema: {str(e)}")
            raise
    
    async def save_filter_preset(
        self,
        hybrid_service: HybridDataService,
        preset: FilterPreset
    ) -> str:
        """Save filter preset."""
        try:
            # Validate preset
            if not preset.name or not preset.entity_type:
                raise ValueError("Preset name and entity type are required")
            
            # Save to database
            preset_id = await hybrid_service.save_filter_preset(preset.dict())
            
            self.logger.info(f"Saved filter preset: {preset_id}")
            return preset_id
            
        except Exception as e:
            self.logger.error(f"Error saving filter preset: {str(e)}")
            raise
    
    async def get_filter_preset(
        self,
        hybrid_service: HybridDataService,
        preset_id: str
    ) -> Optional[FilterPreset]:
        """Get filter preset by ID."""
        try:
            preset_data = await hybrid_service.get_filter_preset(preset_id)
            if preset_data:
                return FilterPreset(**preset_data)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting filter preset: {str(e)}")
            return None
    
    async def list_filter_presets(
        self,
        hybrid_service: HybridDataService,
        entity_type: Optional[EntityType] = None,
        user_id: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> List[FilterPreset]:
        """List available filter presets."""
        try:
            presets_data = await hybrid_service.list_filter_presets(
                entity_type=entity_type.value if entity_type else None,
                user_id=user_id,
                is_public=is_public
            )
            
            return [FilterPreset(**preset) for preset in presets_data]
            
        except Exception as e:
            self.logger.error(f"Error listing filter presets: {str(e)}")
            return []
    
    async def delete_filter_preset(
        self,
        hybrid_service: HybridDataService,
        preset_id: str
    ) -> bool:
        """Delete filter preset."""
        try:
            success = await hybrid_service.delete_filter_preset(preset_id)
            if success:
                self.logger.info(f"Deleted filter preset: {preset_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting filter preset: {str(e)}")
            return False
    
    async def get_quick_filters(self, entity_type: EntityType) -> List[QuickFilter]:
        """Get quick filters for entity type."""
        try:
            return [qf for qf in self._quick_filters if qf.entity_type == entity_type]
        except Exception as e:
            self.logger.error(f"Error getting quick filters: {str(e)}")
            return []
    
    async def get_filter_suggestions(
        self,
        hybrid_service: HybridDataService,
        entity_type: EntityType,
        partial_filters: Optional[FilterGroup] = None
    ) -> List[FilterSuggestion]:
        """Get intelligent filter suggestions."""
        try:
            # Get sample data for analysis
            sample_data = await self._get_entity_data(hybrid_service, entity_type, limit=1000)
            
            return await self._generate_filter_suggestions(entity_type, sample_data, partial_filters)
            
        except Exception as e:
            self.logger.error(f"Error getting filter suggestions: {str(e)}")
            return []
    
    async def get_filter_analytics(
        self,
        hybrid_service: HybridDataService,
        entity_type: Optional[EntityType] = None,
        date_range: Optional[DateRangeFilter] = None
    ) -> FilterAnalytics:
        """Get filter usage analytics."""
        try:
            analytics_data = await hybrid_service.get_filter_analytics(
                entity_type=entity_type.value if entity_type else None,
                date_range=date_range.dict() if date_range else None
            )
            
            return FilterAnalytics(
                most_used_fields=analytics_data.get("most_used_fields", []),
                popular_presets=analytics_data.get("popular_presets", []),
                average_results_count=analytics_data.get("average_results_count", 0.0),
                performance_metrics=analytics_data.get("performance_metrics", {})
            )
            
        except Exception as e:
            self.logger.error(f"Error getting filter analytics: {str(e)}")
            return FilterAnalytics(
                most_used_fields=[],
                popular_presets=[],
                average_results_count=0.0,
                performance_metrics={}
            )
    
    async def export_filtered_data(
        self,
        hybrid_service: HybridDataService,
        export_request: FilterExportRequest
    ) -> str:
        """Export filtered data to specified format."""
        try:
            # Apply filters to get data
            filtered_response = await self.apply_advanced_filter(
                hybrid_service, export_request.filter_request
            )
            
            # Convert to DataFrame for export
            df = pd.DataFrame(filtered_response.data)
            
            # Select specific fields if requested
            if export_request.selected_fields:
                available_fields = [f for f in export_request.selected_fields if f in df.columns]
                df = df[available_fields]
            
            # Export to specified format
            export_path = f"exports/filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if export_request.export_format.lower() == "csv":
                export_path += ".csv"
                df.to_csv(export_path, index=False, header=export_request.include_headers)
            elif export_request.export_format.lower() == "xlsx":
                export_path += ".xlsx"
                df.to_excel(export_path, index=False, header=export_request.include_headers)
            elif export_request.export_format.lower() == "json":
                export_path += ".json"
                df.to_json(export_path, orient="records", date_format="iso")
            else:
                raise ValueError(f"Unsupported export format: {export_request.export_format}")
            
            self.logger.info(f"Exported filtered data to: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting filtered data: {str(e)}")
            raise
    
    async def import_filter_preset(
        self,
        hybrid_service: HybridDataService,
        import_request: FilterImportRequest
    ) -> str:
        """Import filter preset from serialized data."""
        try:
            # Parse preset data
            preset_data = json.loads(import_request.preset_data)
            
            # Create preset object
            preset = FilterPreset(
                preset_id=f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=import_request.preset_name,
                **preset_data
            )
            
            # Check if preset exists
            if import_request.overwrite_existing:
                existing_presets = await self.list_filter_presets(
                    hybrid_service, entity_type=preset.entity_type
                )
                existing = next((p for p in existing_presets if p.name == preset.name), None)
                if existing:
                    preset.preset_id = existing.preset_id
            
            # Save preset
            preset_id = await self.save_filter_preset(hybrid_service, preset)
            
            self.logger.info(f"Imported filter preset: {preset_id}")
            return preset_id
            
        except Exception as e:
            self.logger.error(f"Error importing filter preset: {str(e)}")
            raise
    
    # Private helper methods
    
    def _initialize_filter_schemas(self) -> Dict[EntityType, FilterSchema]:
        """Initialize filter schemas for all entity types."""
        schemas = {}
        
        # Consumption schema
        schemas[EntityType.CONSUMPTION] = FilterSchema(
            entity_type=EntityType.CONSUMPTION,
            available_fields=[
                FilterField(
                    field_name="node_id",
                    display_name="Node ID",
                    data_type=FilterDataType.STRING,
                    operators=[FilterOperator.EQUALS, FilterOperator.IN],
                    description="Water network node identifier"
                ),
                FilterField(
                    field_name="consumption_value",
                    display_name="Consumption",
                    data_type=FilterDataType.NUMBER,
                    operators=[FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN, FilterOperator.BETWEEN],
                    description="Water consumption value"
                ),
                FilterField(
                    field_name="timestamp",
                    display_name="Timestamp",
                    data_type=FilterDataType.DATETIME,
                    operators=[FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN, FilterOperator.BETWEEN],
                    description="Measurement timestamp"
                ),
                FilterField(
                    field_name="region",
                    display_name="Region",
                    data_type=FilterDataType.STRING,
                    operators=[FilterOperator.EQUALS, FilterOperator.IN],
                    description="Geographic region"
                )
            ],
            default_sort=SortCriteria(field="timestamp", direction=SortDirection.DESC)
        )
        
        # Water Quality schema
        schemas[EntityType.WATER_QUALITY] = FilterSchema(
            entity_type=EntityType.WATER_QUALITY,
            available_fields=[
                FilterField(
                    field_name="sensor_id",
                    display_name="Sensor ID",
                    data_type=FilterDataType.STRING,
                    operators=[FilterOperator.EQUALS, FilterOperator.IN],
                    description="Quality sensor identifier"
                ),
                FilterField(
                    field_name="ph_level",
                    display_name="pH Level",
                    data_type=FilterDataType.NUMBER,
                    operators=[FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN, FilterOperator.BETWEEN],
                    description="Water pH level"
                ),
                FilterField(
                    field_name="temperature",
                    display_name="Temperature",
                    data_type=FilterDataType.NUMBER,
                    operators=[FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN, FilterOperator.BETWEEN],
                    description="Water temperature"
                ),
                FilterField(
                    field_name="turbidity",
                    display_name="Turbidity",
                    data_type=FilterDataType.NUMBER,
                    operators=[FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN],
                    description="Water turbidity level"
                ),
                FilterField(
                    field_name="compliance_status",
                    display_name="Compliance",
                    data_type=FilterDataType.STRING,
                    operators=[FilterOperator.EQUALS, FilterOperator.IN],
                    sample_values=["compliant", "non_compliant", "warning"],
                    description="Quality compliance status"
                )
            ],
            default_sort=SortCriteria(field="timestamp", direction=SortDirection.DESC)
        )
        
        # Add more schemas for other entity types...
        
        return schemas
    
    def _initialize_quick_filters(self) -> List[QuickFilter]:
        """Initialize predefined quick filters."""
        quick_filters = []
        
        # Consumption quick filters
        quick_filters.extend([
            QuickFilter(
                filter_id="high_consumption",
                name="High Consumption",
                description="Show nodes with consumption above average",
                entity_type=EntityType.CONSUMPTION,
                filter_config=FilterGroup(
                    operator=LogicalOperator.AND,
                    filters=[
                        FieldFilter(
                            field="consumption_value",
                            operator=FilterOperator.GREATER_THAN,
                            value=1000,
                            data_type=FilterDataType.NUMBER
                        )
                    ]
                ),
                icon="trending-up"
            ),
            QuickFilter(
                filter_id="recent_consumption",
                name="Recent Data",
                description="Show data from last 24 hours",
                entity_type=EntityType.CONSUMPTION,
                filter_config=FilterGroup(
                    operator=LogicalOperator.AND,
                    filters=[
                        FieldFilter(
                            field="timestamp",
                            operator=FilterOperator.GREATER_THAN,
                            value=(datetime.now() - timedelta(days=1)).isoformat(),
                            data_type=FilterDataType.DATETIME
                        )
                    ]
                ),
                icon="clock"
            )
        ])
        
        # Water quality quick filters
        quick_filters.extend([
            QuickFilter(
                filter_id="quality_alerts",
                name="Quality Alerts",
                description="Show non-compliant quality readings",
                entity_type=EntityType.WATER_QUALITY,
                filter_config=FilterGroup(
                    operator=LogicalOperator.AND,
                    filters=[
                        FieldFilter(
                            field="compliance_status",
                            operator=FilterOperator.EQUALS,
                            value="non_compliant",
                            data_type=FilterDataType.STRING
                        )
                    ]
                ),
                icon="alert-triangle"
            ),
            QuickFilter(
                filter_id="extreme_ph",
                name="Extreme pH",
                description="Show readings with pH outside normal range",
                entity_type=EntityType.WATER_QUALITY,
                filter_config=FilterGroup(
                    operator=LogicalOperator.OR,
                    filters=[
                        FieldFilter(
                            field="ph_level",
                            operator=FilterOperator.LESS_THAN,
                            value=6.5,
                            data_type=FilterDataType.NUMBER
                        ),
                        FieldFilter(
                            field="ph_level",
                            operator=FilterOperator.GREATER_THAN,
                            value=8.5,
                            data_type=FilterDataType.NUMBER
                        )
                    ]
                ),
                icon="thermometer"
            )
        ])
        
        return quick_filters
    
    async def _get_entity_data(
        self,
        hybrid_service: HybridDataService,
        entity_type: EntityType,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get base data for specified entity type."""
        try:
            if entity_type == EntityType.CONSUMPTION:
                return await hybrid_service.get_consumption_data(limit=limit)
            elif entity_type == EntityType.WATER_QUALITY:
                return await hybrid_service.get_quality_data(limit=limit)
            elif entity_type == EntityType.FORECASTING:
                return await hybrid_service.get_forecasting_data(limit=limit)
            elif entity_type == EntityType.REPORTS:
                return await hybrid_service.get_reports_data(limit=limit)
            elif entity_type == EntityType.KPIS:
                return await hybrid_service.get_kpis_data(limit=limit)
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error getting entity data: {str(e)}")
            return []
    
    def _apply_filters(
        self,
        data: List[Dict[str, Any]],
        filter_request: AdvancedFilterRequest
    ) -> List[Dict[str, Any]]:
        """Apply filters to data."""
        filtered_data = data.copy()
        
        # Apply field filters
        if filter_request.filters:
            filtered_data = self._apply_filter_group(filtered_data, filter_request.filters)
        
        # Apply date range filter
        if filter_request.date_range:
            filtered_data = self._apply_date_range_filter(filtered_data, filter_request.date_range)
        
        # Apply geographic filter
        if filter_request.geographic:
            filtered_data = self._apply_geographic_filter(filtered_data, filter_request.geographic)
        
        return filtered_data
    
    def _apply_filter_group(
        self,
        data: List[Dict[str, Any]],
        filter_group: FilterGroup
    ) -> List[Dict[str, Any]]:
        """Apply filter group with logical operators."""
        if not filter_group.filters and not filter_group.groups:
            return data
        
        results = []
        
        for record in data:
            # Evaluate field filters
            field_results = []
            for field_filter in filter_group.filters:
                field_results.append(self._evaluate_field_filter(record, field_filter))
            
            # Evaluate nested groups
            group_results = []
            for nested_group in filter_group.groups or []:
                group_data = self._apply_filter_group([record], nested_group)
                group_results.append(len(group_data) > 0)
            
            # Combine results based on operator
            all_results = field_results + group_results
            
            if filter_group.operator == LogicalOperator.AND:
                if all(all_results):
                    results.append(record)
            elif filter_group.operator == LogicalOperator.OR:
                if any(all_results):
                    results.append(record)
            elif filter_group.operator == LogicalOperator.NOT:
                if not any(all_results):
                    results.append(record)
        
        return results
    
    def _evaluate_field_filter(
        self,
        record: Dict[str, Any],
        field_filter: FieldFilter
    ) -> bool:
        """Evaluate individual field filter."""
        field_value = record.get(field_filter.field)
        filter_value = field_filter.value
        
        if field_filter.operator == FilterOperator.EQUALS:
            return field_value == filter_value
        elif field_filter.operator == FilterOperator.NOT_EQUALS:
            return field_value != filter_value
        elif field_filter.operator == FilterOperator.GREATER_THAN:
            return field_value is not None and field_value > filter_value
        elif field_filter.operator == FilterOperator.GREATER_THAN_OR_EQUAL:
            return field_value is not None and field_value >= filter_value
        elif field_filter.operator == FilterOperator.LESS_THAN:
            return field_value is not None and field_value < filter_value
        elif field_filter.operator == FilterOperator.LESS_THAN_OR_EQUAL:
            return field_value is not None and field_value <= filter_value
        elif field_filter.operator == FilterOperator.CONTAINS:
            return field_value is not None and str(filter_value).lower() in str(field_value).lower()
        elif field_filter.operator == FilterOperator.NOT_CONTAINS:
            return field_value is None or str(filter_value).lower() not in str(field_value).lower()
        elif field_filter.operator == FilterOperator.STARTS_WITH:
            return field_value is not None and str(field_value).lower().startswith(str(filter_value).lower())
        elif field_filter.operator == FilterOperator.ENDS_WITH:
            return field_value is not None and str(field_value).lower().endswith(str(filter_value).lower())
        elif field_filter.operator == FilterOperator.IN:
            return field_value in filter_value if isinstance(filter_value, list) else False
        elif field_filter.operator == FilterOperator.NOT_IN:
            return field_value not in filter_value if isinstance(filter_value, list) else True
        elif field_filter.operator == FilterOperator.IS_NULL:
            return field_value is None
        elif field_filter.operator == FilterOperator.IS_NOT_NULL:
            return field_value is not None
        elif field_filter.operator == FilterOperator.BETWEEN:
            if isinstance(filter_value, list) and len(filter_value) == 2:
                return field_value is not None and filter_value[0] <= field_value <= filter_value[1]
        
        return False
    
    def _apply_date_range_filter(
        self,
        data: List[Dict[str, Any]],
        date_filter: DateRangeFilter
    ) -> List[Dict[str, Any]]:
        """Apply date range filter."""
        filtered_data = []
        
        for record in data:
            field_value = record.get(date_filter.field)
            if not field_value:
                continue
            
            # Convert to datetime if needed
            if isinstance(field_value, str):
                try:
                    field_value = datetime.fromisoformat(field_value.replace('Z', '+00:00'))
                except:
                    continue
            
            # Check date range
            include_record = True
            
            if date_filter.start_date and field_value < date_filter.start_date:
                include_record = False
            
            if date_filter.end_date and field_value > date_filter.end_date:
                include_record = False
            
            if date_filter.relative_days:
                cutoff_date = datetime.now() + timedelta(days=date_filter.relative_days)
                if date_filter.relative_days < 0:  # Past
                    if field_value < cutoff_date:
                        include_record = False
                else:  # Future
                    if field_value > cutoff_date:
                        include_record = False
            
            if include_record:
                filtered_data.append(record)
        
        return filtered_data
    
    def _apply_geographic_filter(
        self,
        data: List[Dict[str, Any]],
        geo_filter: GeographicFilter
    ) -> List[Dict[str, Any]]:
        """Apply geographic filter."""
        filtered_data = []
        
        for record in data:
            include_record = True
            
            # Filter by nodes
            if geo_filter.nodes:
                node_id = record.get("node_id") or record.get("sensor_id")
                if node_id not in geo_filter.nodes:
                    include_record = False
            
            # Filter by regions
            if geo_filter.regions:
                region = record.get("region")
                if region not in geo_filter.regions:
                    include_record = False
            
            # Filter by zones
            if geo_filter.zones:
                zone = record.get("zone")
                if zone not in geo_filter.zones:
                    include_record = False
            
            # TODO: Implement coordinate-based filtering
            
            if include_record:
                filtered_data.append(record)
        
        return filtered_data
    
    def _apply_sorting(
        self,
        data: List[Dict[str, Any]],
        sort_criteria: List[SortCriteria]
    ) -> List[Dict[str, Any]]:
        """Apply sorting to data."""
        if not sort_criteria:
            return data
        
        sorted_data = data.copy()
        
        # Apply sorts in reverse order for stable sorting
        for sort_criterion in reversed(sort_criteria):
            reverse = sort_criterion.direction == SortDirection.DESC
            
            sorted_data.sort(
                key=lambda x: x.get(sort_criterion.field, 0) or 0,
                reverse=reverse
            )
        
        return sorted_data
    
    def _apply_pagination(
        self,
        data: List[Dict[str, Any]],
        pagination: PaginationOptions
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Apply pagination to data."""
        total_count = len(data)
        page_size = pagination.page_size
        page = pagination.page
        
        # Calculate pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        paginated_data = data[start_index:end_index]
        
        page_count = (total_count + page_size - 1) // page_size
        
        metadata = {
            "page_count": page_count,
            "has_next_page": page < page_count,
            "has_previous_page": page > 1
        }
        
        return paginated_data, metadata
    
    async def _generate_filter_suggestions(
        self,
        entity_type: EntityType,
        data: List[Dict[str, Any]],
        partial_filters: Optional[FilterGroup] = None
    ) -> List[str]:
        """Generate intelligent filter suggestions."""
        suggestions = []
        
        if not data:
            return suggestions
        
        # Analyze data patterns
        sample_record = data[0]
        
        # Suggest common filters based on data patterns
        for field_name, field_value in sample_record.items():
            if isinstance(field_value, (int, float)):
                suggestions.append(f"Filter by {field_name} range")
            elif isinstance(field_value, str):
                suggestions.append(f"Filter by {field_name} value")
        
        # Add entity-specific suggestions
        if entity_type == EntityType.CONSUMPTION:
            suggestions.extend([
                "Filter by high consumption nodes",
                "Filter by time period",
                "Filter by region"
            ])
        elif entity_type == EntityType.WATER_QUALITY:
            suggestions.extend([
                "Filter by compliance status",
                "Filter by quality parameters",
                "Filter by alert conditions"
            ])
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _validate_filter_group(self, filter_group: FilterGroup) -> List[str]:
        """Validate filter group structure."""
        errors = []
        
        # Validate field filters
        for field_filter in filter_group.filters:
            if not field_filter.field:
                errors.append("Field name is required for filters")
            
            if field_filter.operator == FilterOperator.BETWEEN:
                if not isinstance(field_filter.value, list) or len(field_filter.value) != 2:
                    errors.append("BETWEEN operator requires array of 2 values")
        
        # Validate nested groups
        for nested_group in filter_group.groups or []:
            nested_errors = self._validate_filter_group(nested_group)
            errors.extend(nested_errors)
        
        return errors
    
    def _validate_date_range(self, date_range: DateRangeFilter) -> List[str]:
        """Validate date range filter."""
        errors = []
        
        if not date_range.field:
            errors.append("Date field is required for date range filter")
        
        if date_range.start_date and date_range.end_date:
            if date_range.start_date > date_range.end_date:
                errors.append("Start date must be before end date")
        
        return errors
    
    def _validate_geographic_filter(self, geo_filter: GeographicFilter) -> List[str]:
        """Validate geographic filter."""
        errors = []
        
        # Validate coordinates if provided
        if geo_filter.coordinates:
            required_coords = ["lat_min", "lat_max", "lng_min", "lng_max"]
            for coord in required_coords:
                if coord not in geo_filter.coordinates:
                    errors.append(f"Missing coordinate: {coord}")
        
        return errors
    
    def _validate_sort_criteria(
        self,
        sort_criteria: List[SortCriteria],
        entity_type: EntityType
    ) -> List[str]:
        """Validate sort criteria."""
        errors = []
        
        schema = self._filter_schemas.get(entity_type)
        if schema:
            available_fields = [f.field_name for f in schema.available_fields]
            
            for sort_criterion in sort_criteria:
                if sort_criterion.field not in available_fields:
                    errors.append(f"Invalid sort field: {sort_criterion.field}")
        
        return errors
    
    def _count_applied_filters(self, filter_request: AdvancedFilterRequest) -> int:
        """Count total number of applied filters."""
        count = 0
        
        if filter_request.filters:
            count += self._count_filter_group_filters(filter_request.filters)
        
        if filter_request.date_range:
            count += 1
        
        if filter_request.geographic:
            count += 1
        
        return count
    
    def _count_filter_group_filters(self, filter_group: FilterGroup) -> int:
        """Count filters in a filter group."""
        count = len(filter_group.filters)
        
        for nested_group in filter_group.groups or []:
            count += self._count_filter_group_filters(nested_group)
        
        return count
    
    def _merge_preset_with_request(
        self,
        preset: FilterPreset,
        request: AdvancedFilterRequest
    ) -> AdvancedFilterRequest:
        """Merge preset configuration with request."""
        # Start with preset configuration
        merged_request = request.copy()
        
        # Apply preset filters if not overridden
        if not merged_request.filters:
            merged_request.filters = preset.filters
        
        # Apply preset sort criteria if not overridden
        if not merged_request.sort_criteria:
            merged_request.sort_criteria = preset.sort_criteria
        
        return merged_request
    
    def _get_default_schema(self, entity_type: EntityType) -> FilterSchema:
        """Get default schema for entity type."""
        return FilterSchema(
            entity_type=entity_type,
            available_fields=[
                FilterField(
                    field_name="id",
                    display_name="ID",
                    data_type=FilterDataType.STRING,
                    operators=[FilterOperator.EQUALS],
                    description="Record identifier"
                )
            ],
            default_sort=SortCriteria(field="id", direction=SortDirection.ASC)
        ) 