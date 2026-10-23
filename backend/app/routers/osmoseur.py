"""
API router for Osmoseur machine endpoints.

This module defines all REST API endpoints for Osmoseur operations:
- POST /api/osmoseur - Create new record
- GET /api/osmoseur - List all records (paginated)
- GET /api/osmoseur/{id} - Get single record
- PUT /api/osmoseur/{id} - Update record
- DELETE /api/osmoseur/{id} - Delete record
- GET /api/osmoseur/latest - Get most recent record
- GET /api/osmoseur/stats - Get statistical summary
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas.osmoseur import (
    OsmoseurCreate,
    OsmoseurUpdate,
    OsmoseurResponse,
    OsmoseurListResponse
)
from app.services import osmoseur_service


# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

router = APIRouter(
    prefix="/osmoseur",
    tags=["Osmoseur"],
    responses={404: {"description": "Not found"}}
)
"""
API router for Osmoseur endpoints.
All routes are prefixed with /osmoseur and tagged for API documentation.
"""


# ============================================================================
# CREATE ENDPOINT
# ============================================================================

@router.post(
    "",
    response_model=OsmoseurResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new Osmoseur record",
    description="Create a new Osmoseur machine data record with all operational parameters."
)
def create_osmoseur(
    osmoseur: OsmoseurCreate,
    db: Session = Depends(get_db)
) -> OsmoseurResponse:
    """
    Create a new Osmoseur record.
    
    **Request Body:**
    - All operational parameters are required
    - Values are validated according to schema constraints
    
    **Returns:**
    - 201 Created: Record created successfully
    - 422 Validation Error: Invalid data provided
    
    **Example:**
    ```json
    {
        "debit_permeat": 15000,
        "debit_concentrat": 5000,
        "taux_recuperation": 75.0,
        "conductivite_permeat": 15.0,
        "ph_entree": 7.2,
        "ph_sortie": 6.8,
        "turbidite": 0.5,
        "chlore_libre": 0.1,
        "durete_totale": 0.0,
        "tds": 10.0
    }
    ```
    """
    return osmoseur_service.create_osmoseur(db, osmoseur)


# ============================================================================
# READ ENDPOINTS
# ============================================================================

@router.get(
    "",
    response_model=OsmoseurListResponse,
    summary="List all Osmoseur records",
    description="Retrieve a paginated list of Osmoseur records with optional sorting."
)
def get_all_osmoseur(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of records per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db)
) -> OsmoseurListResponse:
    """
    Get a paginated list of Osmoseur records.
    
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Records per page (default: 50, max: 100)
    - `sort_by`: Field to sort by (default: "created_at")
    - `sort_order`: "asc" or "desc" (default: "desc")
    
    **Returns:**
    - 200 OK: Paginated list of records
    
    **Example:**
    ```
    GET /api/osmoseur?page=1&page_size=20&sort_by=created_at&sort_order=desc
    ```
    """
    # Calculate skip value for pagination
    skip = (page - 1) * page_size
    
    # Get records and total count
    records = osmoseur_service.get_all_osmoseur(
        db,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total = osmoseur_service.get_osmoseur_count(db)
    
    return OsmoseurListResponse(
        total=total,
        page=page,
        page_size=page_size,
        data=records
    )


@router.get(
    "/latest",
    response_model=OsmoseurResponse,
    summary="Get latest Osmoseur record",
    description="Retrieve the most recent Osmoseur record."
)
def get_latest_osmoseur(
    db: Session = Depends(get_db)
) -> OsmoseurResponse:
    """
    Get the most recent Osmoseur record.
    
    **Returns:**
    - 200 OK: Most recent record
    - 404 Not Found: No records exist
    
    **Example:**
    ```
    GET /api/osmoseur/latest
    ```
    """
    record = osmoseur_service.get_latest_osmoseur(db)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Osmoseur records found"
        )
    
    return record


@router.get(
    "/stats",
    summary="Get Osmoseur statistics",
    description="Retrieve statistical summary of all Osmoseur records."
)
def get_osmoseur_stats(
    db: Session = Depends(get_db)
) -> dict:
    """
    Get statistical summary of Osmoseur data.
    
    Calculates average values for all operational parameters.
    
    **Returns:**
    - 200 OK: Statistical summary
    
    **Example Response:**
    ```json
    {
        "avg_debit_permeat": 15234.56,
        "avg_debit_concentrat": 5123.45,
        "avg_taux_recuperation": 74.8,
        "total_records": 150
    }
    ```
    """
    return osmoseur_service.get_osmoseur_stats(db)


@router.get(
    "/{osmoseur_id}",
    response_model=OsmoseurResponse,
    summary="Get Osmoseur record by ID",
    description="Retrieve a single Osmoseur record by its unique identifier."
)
def get_osmoseur_by_id(
    osmoseur_id: UUID,
    db: Session = Depends(get_db)
) -> OsmoseurResponse:
    """
    Get a single Osmoseur record by ID.
    
    **Path Parameters:**
    - `osmoseur_id`: UUID of the record
    
    **Returns:**
    - 200 OK: Record found
    - 404 Not Found: Record does not exist
    
    **Example:**
    ```
    GET /api/osmoseur/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    record = osmoseur_service.get_osmoseur_by_id(db, osmoseur_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Osmoseur record with ID {osmoseur_id} not found"
        )
    
    return record


# ============================================================================
# UPDATE ENDPOINT
# ============================================================================

@router.put(
    "/{osmoseur_id}",
    response_model=OsmoseurResponse,
    summary="Update Osmoseur record",
    description="Update an existing Osmoseur record. Only provided fields will be updated."
)
def update_osmoseur(
    osmoseur_id: UUID,
    osmoseur: OsmoseurUpdate,
    db: Session = Depends(get_db)
) -> OsmoseurResponse:
    """
    Update an existing Osmoseur record.
    
    **Path Parameters:**
    - `osmoseur_id`: UUID of the record to update
    
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
        "debit_permeat": 16000,
        "conductivite_permeat": 12.0
    }
    ```
    """
    updated_record = osmoseur_service.update_osmoseur(db, osmoseur_id, osmoseur)
    
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Osmoseur record with ID {osmoseur_id} not found"
        )
    
    return updated_record


# ============================================================================
# DELETE ENDPOINT
# ============================================================================

@router.delete(
    "/{osmoseur_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Osmoseur record",
    description="Delete an Osmoseur record from the database."
)
def delete_osmoseur(
    osmoseur_id: UUID,
    db: Session = Depends(get_db)
) -> None:
    """
    Delete an Osmoseur record.
    
    **Path Parameters:**
    - `osmoseur_id`: UUID of the record to delete
    
    **Returns:**
    - 204 No Content: Record deleted successfully
    - 404 Not Found: Record does not exist
    
    **Example:**
    ```
    DELETE /api/osmoseur/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    success = osmoseur_service.delete_osmoseur(db, osmoseur_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Osmoseur record with ID {osmoseur_id} not found"
        )
    
    return None
