"""
Artist-related schemas for the Setlist application.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ArtistCreate(BaseModel):
    """Artist creation request model."""
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    location: Optional[str] = None
    website: Optional[str] = None


class ArtistUpdate(BaseModel):
    """Artist profile update request model."""
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    location: Optional[str] = None
    website: Optional[str] = None


class ArtistResponse(BaseModel):
    """Artist profile response model."""
    id: int
    user_id: int
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """User response model for artist endpoints."""
    id: int
    email: str
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ArtistProfileResponse(BaseModel):
    """Artist profile response schema that includes both user and profile info."""
    user: UserResponse
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    location: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Music Track Schemas

class MusicTrackCreate(BaseModel):
    """Music track creation request model."""
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = True


class MusicTrackUpdate(BaseModel):
    """Music track update request model."""
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class MusicTrackResponse(BaseModel):
    """Music track response model."""
    id: int
    artist_id: int
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    audio_url: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Collaboration Schemas

class CollaborationCreate(BaseModel):
    """Collaboration creation request model."""
    target_artist_id: int
    message: str
    project_type: str


class CollaborationUpdate(BaseModel):
    """Collaboration update request model."""
    message: Optional[str] = None
    project_type: Optional[str] = None


class CollaborationResponse(BaseModel):
    """Collaboration response model."""
    id: int
    requester_id: int
    target_artist_id: int
    message: str
    project_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
