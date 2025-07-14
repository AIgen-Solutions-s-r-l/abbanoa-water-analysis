"""
Advanced Filtering API Router.

This router provides comprehensive filtering capabilities across all data entities
with advanced features like presets, suggestions, analytics, and export functionality.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse

from src.schemas.api.filters import (
    AdvancedFilterRequest, FilteredResponse, FilterPreset, FilterSchema,
    FilterValidationResult, FilterSuggestion, FilterAnalytics, QuickFilter,
    EntityType, FilterExportRequest, FilterImportRequest
)
from src.api.services.filters_service import AdvancedFilteringService
from src.infrastructure.data.hybrid_data_service import HybridDataService

router = APIRouter(prefix="/api/v1/filters", tags=["Advanced Filtering"])

# Service dependencies
async def get_filtering_service() -> AdvancedFilteringService:
    """Get filtering service instance."""
    return AdvancedFilteringService()

async def get_hybrid_service() -> HybridDataService:
    """Get hybrid data service instance."""
    return HybridDataService()


@router.post(
    "/apply",
    response_model=FilteredResponse,
    summary="Apply Advanced Filter",
    description="Apply comprehensive filtering to any data entity with advanced features"
)
async def apply_advanced_filter(
    filter_request: AdvancedFilterRequest,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Apply advanced filtering to specified entity with support for:
    - Complex field filtering with logical operators
    - Date range and geographic filtering
    - Sorting and pagination
    - Filter presets
    - Performance optimization
    """
    try:
        return await filtering_service.apply_advanced_filter(hybrid_service, filter_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/validate",
    response_model=FilterValidationResult,
    summary="Validate Filter Request",
    description="Validate filter request structure and values before execution"
)
async def validate_filter_request(
    filter_request: AdvancedFilterRequest,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service)
):
    """
    Validate filter request including:
    - Field existence and data types
    - Operator compatibility
    - Value format validation
    - Performance warnings
    """
    try:
        return await filtering_service.validate_filter_request(filter_request)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/schema/{entity_type}",
    response_model=FilterSchema,
    summary="Get Filter Schema",
    description="Get available filter fields and operators for entity type"
)
async def get_filter_schema(
    entity_type: EntityType,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service)
):
    """
    Get comprehensive filter schema including:
    - Available filter fields
    - Supported operators per field
    - Data types and validation rules
    - Sample values and descriptions
    """
    try:
        return await filtering_service.get_filter_schema(entity_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/presets",
    response_model=str,
    summary="Save Filter Preset",
    description="Save filter configuration as reusable preset"
)
async def save_filter_preset(
    preset: FilterPreset,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Save filter preset with:
    - Named filter configurations
    - Public/private visibility
    - Default sorting preferences
    - Reusable across sessions
    """
    try:
        return await filtering_service.save_filter_preset(hybrid_service, preset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/presets/{preset_id}",
    response_model=FilterPreset,
    summary="Get Filter Preset",
    description="Retrieve saved filter preset by ID"
)
async def get_filter_preset(
    preset_id: str,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """Get saved filter preset configuration."""
    try:
        preset = await filtering_service.get_filter_preset(hybrid_service, preset_id)
        if not preset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
        return preset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/presets",
    response_model=List[FilterPreset],
    summary="List Filter Presets",
    description="List available filter presets with optional filtering"
)
async def list_filter_presets(
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    List filter presets with optional filtering by:
    - Entity type
    - User ownership
    - Public/private visibility
    """
    try:
        return await filtering_service.list_filter_presets(
            hybrid_service, entity_type, user_id, is_public
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/presets/{preset_id}",
    response_model=bool,
    summary="Delete Filter Preset",
    description="Delete saved filter preset"
)
async def delete_filter_preset(
    preset_id: str,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """Delete filter preset by ID."""
    try:
        success = await filtering_service.delete_filter_preset(hybrid_service, preset_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
        return success
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/quick-filters/{entity_type}",
    response_model=List[QuickFilter],
    summary="Get Quick Filters",
    description="Get predefined quick filters for entity type"
)
async def get_quick_filters(
    entity_type: EntityType,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service)
):
    """
    Get predefined quick filters including:
    - Common filter scenarios
    - One-click filtering options
    - Entity-specific filters
    - Popular filter combinations
    """
    try:
        return await filtering_service.get_quick_filters(entity_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/suggestions/{entity_type}",
    response_model=List[FilterSuggestion],
    summary="Get Filter Suggestions",
    description="Get intelligent filter suggestions based on data analysis"
)
async def get_filter_suggestions(
    entity_type: EntityType,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Get intelligent filter suggestions including:
    - Data-driven recommendations
    - Common filter patterns
    - Anomaly detection filters
    - Performance optimized filters
    """
    try:
        return await filtering_service.get_filter_suggestions(hybrid_service, entity_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/analytics",
    response_model=FilterAnalytics,
    summary="Get Filter Analytics",
    description="Get filter usage analytics and performance metrics"
)
async def get_filter_analytics(
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Get filter usage analytics including:
    - Most used filter fields
    - Popular presets
    - Performance metrics
    - Usage patterns
    """
    try:
        return await filtering_service.get_filter_analytics(hybrid_service, entity_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/export",
    response_class=FileResponse,
    summary="Export Filtered Data",
    description="Export filtered data to various formats (CSV, Excel, JSON)"
)
async def export_filtered_data(
    export_request: FilterExportRequest,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Export filtered data with options for:
    - Multiple formats (CSV, Excel, JSON)
    - Field selection
    - Header inclusion
    - Large dataset handling
    """
    try:
        export_path = await filtering_service.export_filtered_data(hybrid_service, export_request)
        
        # Determine media type based on format
        media_type_map = {
            "csv": "text/csv",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json"
        }
        
        media_type = media_type_map.get(
            export_request.export_format.lower(), 
            "application/octet-stream"
        )
        
        return FileResponse(
            path=export_path,
            media_type=media_type,
            filename=export_path.split("/")[-1]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/import-preset",
    response_model=str,
    summary="Import Filter Preset",
    description="Import filter preset from serialized data"
)
async def import_filter_preset(
    import_request: FilterImportRequest,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Import filter preset from external source:
    - JSON serialized presets
    - Preset sharing between users
    - Backup/restore functionality
    - Migration support
    """
    try:
        return await filtering_service.import_filter_preset(hybrid_service, import_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Advanced search and discovery endpoints

@router.get(
    "/fields/{entity_type}",
    response_model=List[str],
    summary="Get Available Fields",
    description="Get list of filterable fields for entity type"
)
async def get_available_fields(
    entity_type: EntityType,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service)
):
    """Get list of all filterable fields for the specified entity type."""
    try:
        schema = await filtering_service.get_filter_schema(entity_type)
        return [field.field_name for field in schema.available_fields]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/operators/{entity_type}/{field_name}",
    response_model=List[str],
    summary="Get Field Operators",
    description="Get supported operators for specific field"
)
async def get_field_operators(
    entity_type: EntityType,
    field_name: str,
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service)
):
    """Get list of supported filter operators for a specific field."""
    try:
        schema = await filtering_service.get_filter_schema(entity_type)
        field = next((f for f in schema.available_fields if f.field_name == field_name), None)
        
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Field '{field_name}' not found for entity type '{entity_type}'"
            )
        
        return [op.value for op in field.operators]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/values/{entity_type}/{field_name}",
    response_model=List[str],
    summary="Get Field Values",
    description="Get sample/distinct values for field to assist filter creation"
)
async def get_field_values(
    entity_type: EntityType,
    field_name: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of values to return"),
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Get sample or distinct values for a field to help users create filters.
    Useful for dropdown menus and filter assistance.
    """
    try:
        # Get sample data for the entity
        if entity_type == EntityType.CONSUMPTION:
            data = await hybrid_service.get_consumption_data(limit=1000)
        elif entity_type == EntityType.WATER_QUALITY:
            data = await hybrid_service.get_quality_data(limit=1000)
        elif entity_type == EntityType.FORECASTING:
            data = await hybrid_service.get_forecasting_data(limit=1000)
        else:
            data = []
        
        # Extract unique values for the field
        values = set()
        for record in data:
            value = record.get(field_name)
            if value is not None:
                values.add(str(value))
        
        # Return limited, sorted list
        return sorted(list(values))[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Batch operations

@router.post(
    "/batch-apply",
    response_model=List[FilteredResponse],
    summary="Apply Multiple Filters",
    description="Apply multiple filter requests in a single batch operation"
)
async def batch_apply_filters(
    filter_requests: List[AdvancedFilterRequest],
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service),
    hybrid_service: HybridDataService = Depends(get_hybrid_service)
):
    """
    Apply multiple filter requests in batch for:
    - Comparative analysis
    - Multi-entity filtering
    - Performance optimization
    - Dashboard widgets
    """
    try:
        if len(filter_requests) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 filter requests allowed per batch"
            )
        
        results = []
        for request in filter_requests:
            result = await filtering_service.apply_advanced_filter(hybrid_service, request)
            results.append(result)
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/batch-validate",
    response_model=List[FilterValidationResult],
    summary="Validate Multiple Filters",
    description="Validate multiple filter requests in batch"
)
async def batch_validate_filters(
    filter_requests: List[AdvancedFilterRequest],
    filtering_service: AdvancedFilteringService = Depends(get_filtering_service)
):
    """Validate multiple filter requests for batch processing."""
    try:
        if len(filter_requests) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 20 filter requests allowed per validation batch"
            )
        
        results = []
        for request in filter_requests:
            result = await filtering_service.validate_filter_request(request)
            results.append(result)
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Health and monitoring

@router.get(
    "/health",
    summary="Filter Service Health",
    description="Check filter service health and performance"
)
async def get_filter_service_health():
    """Get filter service health status and performance metrics."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "features": {
                "advanced_filtering": True,
                "presets": True,
                "suggestions": True,
                "analytics": True,
                "export": True,
                "batch_operations": True
            },
            "limits": {
                "max_batch_filters": 10,
                "max_validation_batch": 20,
                "max_page_size": 1000,
                "max_export_records": 100000
            }
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 