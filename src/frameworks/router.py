"""API router for teaching frameworks."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .loader import (
    FRAMEWORKS,
    get_framework,
    get_frameworks_by_category,
    load_frameworks,
)

router = APIRouter(prefix="/frameworks", tags=["frameworks"])

load_frameworks()


class FrameworkSummary(BaseModel):
    key: str
    topic: str
    category: str
    age_range: list[int]


class FrameworkListResponse(BaseModel):
    count: int
    frameworks: list[FrameworkSummary]


class CategoryFramework(BaseModel):
    key: str
    topic: str


class CategoryResponse(BaseModel):
    category: str
    frameworks: list[CategoryFramework]


@router.get("", response_model=FrameworkListResponse)
async def list_frameworks():
    """List all available teaching frameworks."""
    return {
        "count": len(FRAMEWORKS),
        "frameworks": [
            {
                "key": k,
                "topic": v.get("topic", k),
                "category": v.get("category", "unknown"),
                "age_range": v.get("age_range_months", [0, 216]),
            }
            for k, v in sorted(FRAMEWORKS.items())
        ],
    }


@router.get("/categories")
async def list_categories():
    """List all available categories with counts."""
    categories: dict[str, int] = {}
    for v in FRAMEWORKS.values():
        cat = v.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "categories": [
            {"name": k, "count": v}
            for k, v in sorted(categories.items())
        ]
    }


@router.get("/category/{category}", response_model=CategoryResponse)
async def get_by_category(category: str):
    """Get all frameworks in a specific category."""
    frameworks = get_frameworks_by_category(category)
    
    if not frameworks:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found or has no frameworks")
    
    return {
        "category": category,
        "frameworks": [
            {"key": f["key"], "topic": f.get("topic", f["key"])}
            for f in frameworks
        ],
    }


@router.get("/{key}")
async def get_framework_by_key(key: str):
    """Get a specific teaching framework by key."""
    framework = get_framework(key)
    
    if not framework:
        raise HTTPException(status_code=404, detail=f"Framework '{key}' not found")
    
    return {"key": key, **framework}
