"""
API router for Remplisseuse machine endpoints.

This module defines all REST API endpoints for Remplisseuse operations:
- POST /api/remplisseuse - Create new record
- GET /api/remplisseuse - List all records (paginated)
- GET /api/remplisseuse/{id} - Get single record
- PUT /api/remplisseuse/{id} - Update record
- DELETE /api/remplisseuse/{id} - Delete record
- GET /api/remplisseuse/latest - Get most recent record
- GET /api/remplisseuse/stats - Get statistical summary
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.remplisseuse import (
    RemplisseuseCreate,
    RemplisseuseUpdate,
    RemplisseuseResponse,
    RemplisseuseListResponse
)
from app.services import remplisseuse_service


# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

router = APIRouter(
    prefix="/remplisseuse",
    tags=["Remplisseuse"],
    responses={404: {"description": "Not found"}}
)
"""
API router for Remplisseuse endpoints.
All routes are prefixed with /remplisseuse and tagged for API documentation.
"""


# ============================================================================
# CREATE ENDPOINT
# ============================================================================

@router.post(
    "",
    response_model=RemplisseuseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new Remplisseuse record",
    description="Create a new Remplisseuse (filling machine) data record with all operational parameters."
)
def create_remplisseuse(
    remplisseuse: RemplisseuseCreate,
    db: Session = Depends(get_db)
) -> RemplisseuseResponse:
    """
    Create a new Remplisseuse record.
    
    **Request Body:**
    - All operational parameters are required
    - Values are validated according to schema constraints
    
    **Returns:**
    - 201 Created: Record created successfully
    - 422 Validation Error: Invalid data provided
    
    **Example:**
    ```json
    {
        "temperature_remplissage": 4.0,
        "volume_remplissage": 1.5,
        "carbonation": 8.0,
        "mtbf": 48.0,
        "rendement": 98.5,
        "conso_air_co2": 120.0,
        "vibrations": 2.5
    }
    ```
    """
    return remplisseuse_service.create_remplisseuse(db, remplisseuse)


# ============================================================================
# READ ENDPOINTS
# ============================================================================

@router.get(
    "",
    response_model=RemplisseuseListResponse,
    summary="List all Remplisseuse records",
    description="Retrieve a paginated list of Remplisseuse records with optional sorting."
)
def get_all_remplisseuse(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of records per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db)
) -> RemplisseuseListResponse:
    """
    Get a paginated list of Remplisseuse records.
    
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Records per page (default: 50, max: 100)
    - `sort_by`: Field to sort by (default: "created_at")
    - `sort_order`: "asc" or "desc" (default: "desc")
    
    **Returns:**
    - 200 OK: Paginated list of records
    
    **Example:**
    ```
    GET /api/remplisseuse?page=1&page_size=20&sort_by=created_at&sort_order=desc
    ```
    """
    # Calculate skip value for pagination
    skip = (page - 1) * page_size
    
    # Get records and total count
    records = remplisseuse_service.get_all_remplisseuse(
        db,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total = remplisseuse_service.get_remplisseuse_count(db)
    
    return RemplisseuseListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=records
    )


@router.get(
    "/latest",
    response_model=RemplisseuseResponse,
    summary="Get latest Remplisseuse record",
    description="Retrieve the most recent Remplisseuse record."
)
def get_latest_remplisseuse(
    db: Session = Depends(get_db)
) -> RemplisseuseResponse:
    """
    Get the most recent Remplisseuse record.
    
    **Returns:**
    - 200 OK: Most recent record
    - 404 Not Found: No records exist
    
    **Example:**
    ```
    GET /api/remplisseuse/latest
    ```
    """
    record = remplisseuse_service.get_latest_remplisseuse(db)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Remplisseuse records found"
        )
    
    return record


@router.get(
    "/stats",
    summary="Get Remplisseuse statistics",
    description="Retrieve statistical summary of all Remplisseuse records."
)
def get_remplisseuse_stats(
    db: Session = Depends(get_db)
) -> dict:
    """
    Get statistical summary of Remplisseuse data.
    
    Calculates average values for all operational parameters.
    
    **Returns:**
    - 200 OK: Statistical summary
    
    **Example Response:**
    ```json
    {
        "avg_temperature_remplissage": 4.2,
        "avg_volume_remplissage": 1.48,
        "avg_carbonation": 8.1,
        "avg_mtbf": 52.3,
        "avg_rendement": 97.8,
        "avg_conso_air_co2": 118.5,
        "avg_vibrations": 2.6,
        "total_records": 120
    }
    ```
    """
    return remplisseuse_service.get_remplisseuse_stats(db)


@router.get(
    "/{remplisseuse_id}",
    response_model=RemplisseuseResponse,
    summary="Get Remplisseuse record by ID",
    description="Retrieve a single Remplisseuse record by its unique identifier."
)
def get_remplisseuse_by_id(
    remplisseuse_id: UUID,
    db: Session = Depends(get_db)
) -> RemplisseuseResponse:
    """
    Get a single Remplisseuse record by ID.
    
    **Path Parameters:**
    - `remplisseuse_id`: UUID of the record
    
    **Returns:**
    - 200 OK: Record found
    - 404 Not Found: Record does not exist
    
    **Example:**
    ```
    GET /api/remplisseuse/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    record = remplisseuse_service.get_remplisseuse_by_id(db, remplisseuse_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Remplisseuse record with ID {remplisseuse_id} not found"
        )
    
    return record


# ============================================================================
# UPDATE ENDPOINT
# ============================================================================

@router.put(
    "/{remplisseuse_id}",
    response_model=RemplisseuseResponse,
    summary="Update Remplisseuse record",
    description="Update an existing Remplisseuse record. Only provided fields will be updated."
)
def update_remplisseuse(
    remplisseuse_id: UUID,
    remplisseuse: RemplisseuseUpdate,
    db: Session = Depends(get_db)
) -> RemplisseuseResponse:
    """
    Update an existing Remplisseuse record.
    
    **Path Parameters:**
    - `remplisseuse_id`: UUID of the record to update
    
    **Request Body:**
    - All fields are optional
    - Only provided fields will be updated
    
    **Returns:**
    - 200 OK: Record updated successfully
    - 404 Not Found: Record does not exist
    - 422 Validation Error: Invalid data provided
    
    **Example:**
    ```json
    {
        "temperature_remplissage": 3.5,
        "vibrations": 2.8
    }
    ```
    """
    updated_record = remplisseuse_service.update_remplisseuse(db, remplisseuse_id, remplisseuse)
    
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Remplisseuse record with ID {remplisseuse_id} not found"
        )
    
    return updated_record


# ============================================================================
# DELETE ENDPOINT
# ============================================================================

@router.delete(
    "/{remplisseuse_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Remplisseuse record",
    description="Delete a Remplisseuse record from the database."
)
def delete_remplisseuse(
    remplisseuse_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a Remplisseuse record.
    
    **Path Parameters:**
    - `remplisseuse_id`: UUID of the record to delete
    
    **Returns:**
    - 204 No Content: Record deleted successfully
    - 404 Not Found: Record does not exist
    
    **Example:**
    ```
    DELETE /api/remplisseuse/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    success = remplisseuse_service.delete_remplisseuse(db, remplisseuse_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Remplisseuse record with ID {remplisseuse_id} not found"
        )
    
    return None
