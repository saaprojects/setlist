"""
Show and event management endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()


class ShowCreate(BaseModel):
    """Show creation model."""
    title: str
    description: str
    venue_id: str
    promoter_id: str
    date: datetime
    doors_open: datetime
    show_start: datetime
    show_end: datetime
    ticket_price: Optional[float] = None
    ticket_url: Optional[str] = None
    poster_url: Optional[str] = None
    genres: List[str]
    age_restriction: Optional[str] = None
    capacity: Optional[int] = None


class ShowUpdate(BaseModel):
    """Show update model."""
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    doors_open: Optional[datetime] = None
    show_start: Optional[datetime] = None
    show_end: Optional[datetime] = None
    ticket_price: Optional[float] = None
    ticket_url: Optional[str] = None
    poster_url: Optional[str] = None
    genres: Optional[List[str]] = None
    age_restriction: Optional[str] = None
    capacity: Optional[int] = None


@router.get("/", response_model=List[dict])
async def get_shows():
    """Get list of all shows."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Show listing not yet implemented"
    )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_show(show_data: ShowCreate):
    """Create a new show."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Show creation not yet implemented"
    )


@router.get("/{show_id}", response_model=dict)
async def get_show(show_id: str):
    """Get show by ID."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Show retrieval not yet implemented"
    )


@router.put("/{show_id}", response_model=dict)
async def update_show(show_id: str, show_data: ShowUpdate):
    """Update show information."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Show update not yet implemented"
    )


@router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(show_id: str):
    """Delete a show."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Show deletion not yet implemented"
    )
