"""
Playlist management endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class PlaylistCreate(BaseModel):
    """Playlist creation model."""
    name: str
    description: Optional[str] = None
    is_public: bool = True
    cover_image_url: Optional[str] = None


class PlaylistUpdate(BaseModel):
    """Playlist update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_image_url: Optional[str] = None


class PlaylistResponse(BaseModel):
    """Playlist response model."""
    id: str
    name: str
    description: Optional[str]
    user_id: str
    is_public: bool
    cover_image_url: Optional[str]
    tracks: List[str]
    created_at: str
    updated_at: str


@router.get("/", response_model=List[PlaylistResponse])
async def get_playlists():
    """Get list of all public playlists."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Playlist listing not yet implemented"
    )


@router.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist(playlist_data: PlaylistCreate):
    """Create a new playlist."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Playlist creation not yet implemented"
    )


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(playlist_id: str):
    """Get playlist by ID."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Playlist retrieval not yet implemented"
    )


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(playlist_id: str, playlist_data: PlaylistUpdate):
    """Update playlist information."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Playlist update not yet implemented"
    )


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(playlist_id: str):
    """Delete a playlist."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Playlist deletion not yet implemented"
    )


@router.post("/{playlist_id}/tracks/{track_id}")
async def add_track_to_playlist(playlist_id: str, track_id: str):
    """Add a track to a playlist."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Track addition not yet implemented"
    )


@router.delete("/{playlist_id}/tracks/{track_id}")
async def remove_track_from_playlist(playlist_id: str, track_id: str):
    """Remove a track from a playlist."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Track removal not yet implemented"
    )
