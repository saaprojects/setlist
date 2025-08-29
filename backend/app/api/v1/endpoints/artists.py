"""
Artist-specific endpoints for band profiles and music management.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class ArtistProfileUpdate(BaseModel):
    """Artist profile update model."""
    band_name: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    experience_years: Optional[int] = None
    influences: Optional[List[str]] = None
    achievements: Optional[List[str]] = None


@router.get("/", response_model=List[dict])
async def get_artists():
    """Get list of all artists."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Artist listing not yet implemented"
    )


@router.get("/{artist_id}", response_model=dict)
async def get_artist(artist_id: str):
    """Get artist profile by ID."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Artist retrieval not yet implemented"
    )


@router.put("/{artist_id}", response_model=dict)
async def update_artist(artist_id: str, profile_data: ArtistProfileUpdate):
    """Update artist profile."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Artist update not yet implemented"
    )
