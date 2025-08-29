"""
Music-related Pydantic schemas for the Setlist application.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MusicTrackCreate(BaseModel):
    """Schema for creating a music track."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    genre: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, max_items=10)
    is_public: bool = Field(True)


class MusicTrackUpdate(BaseModel):
    """Schema for updating a music track."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    genre: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None, max_items=10)
    is_public: Optional[bool] = None


class MusicTrackResponse(BaseModel):
    """Schema for music track responses."""
    id: int
    artist_id: int
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    audio_url: Optional[str] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime


class MusicTrackAnalytics(BaseModel):
    """Schema for music track analytics."""
    track_id: int
    play_count: int = Field(default=0, ge=0)
    download_count: int = Field(default=0, ge=0)
    like_count: int = Field(default=0, ge=0)
    share_count: int = Field(default=0, ge=0)
    average_listen_duration: int = Field(default=0, ge=0)  # in seconds
    created_at: datetime
    updated_at: datetime


class MusicCollaborationCreate(BaseModel):
    """Schema for creating a music collaboration."""
    collaborator_id: int = Field(..., gt=0)
    role: str = Field(..., min_length=1, max_length=100)  # e.g., "producer", "featured artist"
    message: str = Field(..., min_length=1, max_length=500)


class MusicCollaborationResponse(BaseModel):
    """Schema for music collaboration responses."""
    id: int
    track_id: int
    collaborator_id: int
    role: str
    message: str
    status: str = Field(..., pattern="^(pending|accepted|declined)$")
    created_at: datetime
    updated_at: datetime


class MusicContributionCreate(BaseModel):
    """Schema for creating a music contribution."""
    type: str = Field(..., min_length=1, max_length=100)  # e.g., "audio_contribution", "lyrics", "mixing"
    description: str = Field(..., min_length=1, max_length=500)
    file_url: Optional[str] = Field(None, max_length=500)


class MusicContributionResponse(BaseModel):
    """Schema for music contribution responses."""
    id: int
    track_id: int
    contributor_id: int
    type: str
    description: str
    file_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
