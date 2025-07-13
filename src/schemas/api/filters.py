"""
Advanced Filtering API Schemas.

This module defines Pydantic models for advanced filtering capabilities
across all data entities (consumption, quality, forecasting, etc.).
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class FilterOperator(str, Enum):
    """Filter operators for field-level filtering."""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"


class LogicalOperator(str, Enum):
    """Logical operators for combining filters."""
    AND = "and"
    OR = "or"
    NOT = "not"


class SortDirection(str, Enum):
    """Sort direction options."""
    ASC = "asc"
    DESC = "desc"


class FilterDataType(str, Enum):
    """Data types for filter validation."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"


class EntityType(str, Enum):
    """Entity types that can be filtered."""
    CONSUMPTION = "consumption"
    WATER_QUALITY = "water_quality"
    FORECASTING = "forecasting"
    REPORTS = "reports"
    KPIS = "kpis"
    NODES = "nodes"
    SENSORS = "sensors"
    ALERTS = "alerts"


class FieldFilter(BaseModel):
    """Individual field filter specification."""
    field: str = Field(..., description="Field name to filter on")
    operator: FilterOperator = Field(..., description="Filter operator")
    value: Union[str, int, float, bool, List[Any], None] = Field(
        ..., description="Filter value(s)"
    )
    data_type: Optional[FilterDataType] = Field(
        None, description="Expected data type for validation"
    )


class DateRangeFilter(BaseModel):
    """Date range filter for time-based filtering."""
    field: str = Field(..., description="Date field to filter on")
    start_date: Optional[datetime] = Field(None, description="Start date (inclusive)")
    end_date: Optional[datetime] = Field(None, description="End date (inclusive)")
    relative_days: Optional[int] = Field(
        None, description="Relative days from now (negative for past)"
    )


class GeographicFilter(BaseModel):
    """Geographic filtering options."""
    nodes: Optional[List[str]] = Field(None, description="Specific node IDs")
    regions: Optional[List[str]] = Field(None, description="Region names")
    zones: Optional[List[str]] = Field(None, description="Zone identifiers")
    coordinates: Optional[Dict[str, float]] = Field(
        None, description="Bounding box coordinates (lat/lng)"
    )
    radius_km: Optional[float] = Field(None, description="Radius in kilometers")


class FilterGroup(BaseModel):
    """Group of filters with logical operator."""
    operator: LogicalOperator = Field(LogicalOperator.AND, description="Logical operator")
    filters: List[FieldFilter] = Field([], description="List of field filters")
    groups: Optional[List["FilterGroup"]] = Field([], description="Nested filter groups")


class SortCriteria(BaseModel):
    """Sort criteria specification."""
    field: str = Field(..., description="Field to sort by")
    direction: SortDirection = Field(SortDirection.ASC, description="Sort direction")


class PaginationOptions(BaseModel):
    """Pagination options."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(50, ge=1, le=1000, description="Items per page")
    total_count: Optional[bool] = Field(True, description="Include total count")


class FilterPreset(BaseModel):
    """Saved filter preset."""
    preset_id: str = Field(..., description="Unique preset identifier")
    name: str = Field(..., description="Human-readable preset name")
    description: Optional[str] = Field(None, description="Preset description")
    entity_type: EntityType = Field(..., description="Target entity type")
    filters: FilterGroup = Field(..., description="Filter configuration")
    sort_criteria: Optional[List[SortCriteria]] = Field([], description="Default sorting")
    is_public: bool = Field(False, description="Whether preset is public")
    created_by: Optional[str] = Field(None, description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AdvancedFilterRequest(BaseModel):
    """Advanced filter request."""
    entity_type: EntityType = Field(..., description="Type of entity to filter")
    filters: Optional[FilterGroup] = Field(None, description="Filter criteria")
    date_range: Optional[DateRangeFilter] = Field(None, description="Date range filter")
    geographic: Optional[GeographicFilter] = Field(None, description="Geographic filter")
    sort_criteria: Optional[List[SortCriteria]] = Field([], description="Sort criteria")
    pagination: Optional[PaginationOptions] = Field(
        default_factory=PaginationOptions, description="Pagination options"
    )
    include_metadata: bool = Field(True, description="Include result metadata")
    preset_id: Optional[str] = Field(None, description="Use saved preset")


class FilterValidationResult(BaseModel):
    """Filter validation result."""
    is_valid: bool = Field(..., description="Whether filter is valid")
    errors: List[str] = Field([], description="Validation error messages")
    warnings: List[str] = Field([], description="Validation warnings")


class FilterMetadata(BaseModel):
    """Metadata about filter results."""
    total_count: int = Field(..., description="Total matching records")
    filtered_count: int = Field(..., description="Count after filtering")
    page_count: int = Field(..., description="Total pages")
    current_page: int = Field(..., description="Current page number")
    has_next_page: bool = Field(..., description="Whether there's a next page")
    has_previous_page: bool = Field(..., description="Whether there's a previous page")
    execution_time_ms: float = Field(..., description="Filter execution time")
    applied_filters_count: int = Field(..., description="Number of applied filters")


class FilteredResponse(BaseModel):
    """Generic filtered response wrapper."""
    data: List[Dict[str, Any]] = Field(..., description="Filtered data results")
    metadata: FilterMetadata = Field(..., description="Filter execution metadata")
    applied_filters: Optional[FilterGroup] = Field(None, description="Applied filters")
    suggestions: Optional[List[str]] = Field([], description="Filter suggestions")


class FilterField(BaseModel):
    """Available filter field specification."""
    field_name: str = Field(..., description="Field name")
    display_name: str = Field(..., description="Human-readable name")
    data_type: FilterDataType = Field(..., description="Field data type")
    operators: List[FilterOperator] = Field(..., description="Supported operators")
    sample_values: Optional[List[Any]] = Field([], description="Sample values")
    is_required: bool = Field(False, description="Whether field is required")
    description: Optional[str] = Field(None, description="Field description")


class FilterSchema(BaseModel):
    """Filter schema for an entity type."""
    entity_type: EntityType = Field(..., description="Entity type")
    available_fields: List[FilterField] = Field(..., description="Available filter fields")
    default_sort: Optional[SortCriteria] = Field(None, description="Default sort")
    max_page_size: int = Field(1000, description="Maximum page size")


class FilterSuggestion(BaseModel):
    """Filter suggestion based on data analysis."""
    field: str = Field(..., description="Suggested filter field")
    operator: FilterOperator = Field(..., description="Suggested operator")
    values: List[Any] = Field(..., description="Suggested values")
    reasoning: str = Field(..., description="Why this filter is suggested")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")


class FilterAnalytics(BaseModel):
    """Analytics about filter usage."""
    most_used_fields: List[str] = Field(..., description="Most frequently filtered fields")
    popular_presets: List[str] = Field(..., description="Most used presets")
    average_results_count: float = Field(..., description="Average results per query")
    performance_metrics: Dict[str, float] = Field(..., description="Performance statistics")


class QuickFilter(BaseModel):
    """Quick filter option for common scenarios."""
    filter_id: str = Field(..., description="Quick filter identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Filter description")
    entity_type: EntityType = Field(..., description="Target entity")
    filter_config: FilterGroup = Field(..., description="Pre-configured filter")
    icon: Optional[str] = Field(None, description="Icon identifier")


class FilterExportRequest(BaseModel):
    """Request to export filtered data."""
    filter_request: AdvancedFilterRequest = Field(..., description="Filter configuration")
    export_format: str = Field("csv", description="Export format (csv, xlsx, json)")
    include_headers: bool = Field(True, description="Include column headers")
    selected_fields: Optional[List[str]] = Field(None, description="Fields to export")


class FilterImportRequest(BaseModel):
    """Request to import filter preset."""
    preset_data: str = Field(..., description="Serialized preset data")
    preset_name: str = Field(..., description="Name for imported preset")
    overwrite_existing: bool = Field(False, description="Overwrite if exists")


# Allow forward references for nested models
FilterGroup.model_rebuild() 