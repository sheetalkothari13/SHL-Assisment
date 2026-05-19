from fastapi import APIRouter, Query, HTTPException
from typing import Dict, List
from app.catalog.data import SHL_CATALOG
from app.catalog.database import get_all_assessments, search_assessments, get_assessment_by_code

router = APIRouter(prefix="/catalog", tags=["Catalog"])

@router.get("", response_model=Dict)
async def get_catalog():
    """Retrieve the full, grouped SHL Assessment catalog"""
    return SHL_CATALOG

@router.get("/all", response_model=List[Dict])
async def get_all():
    """Retrieve all flattened assessments in the catalog"""
    return get_all_assessments()

@router.get("/search", response_model=List[Dict])
async def search(q: str = Query(..., min_length=1, description="The fuzzy search query string")):
    """Fuzzy search catalog items by name, description, skills, subtests, or use cases"""
    return search_assessments(q)

@router.get("/{code}", response_model=Dict)
async def get_by_code(code: str):
    """Retrieve a single assessment's metadata using its code"""
    assessment = get_assessment_by_code(code.upper())
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Assessment with code {code} not found.")
    return assessment
