"""
Artist Pydantic schemas.
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class ArtistCreate(BaseModel):
    """Artist creation schema."""
    email: EmailStr
    username: str
    password: str
    display_name: str
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None


class ArtistUpdate(BaseModel):
    """Artist update schema."""
    bio: Optional[str] = None
    genres: Optional[List[str]] = None
    instruments: Optional[List[str]] = None
    location: Optional[str] = None
    website: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema for artist registration."""
    id: int
    email: EmailStr
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ArtistResponse(BaseModel):
    """Artist response schema."""
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


class ArtistRegistrationResponse(BaseModel):
    """Artist registration response schema."""
    user: UserResponse
    artist_profile: ArtistResponse
    access_token: str
    refresh_token: str


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


class MusicTrackCreate(BaseModel):
    """Music track creation schema."""
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = True


class MusicTrackUpdate(BaseModel):
    """Music track update schema."""
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class MusicTrackResponse(BaseModel):
    """Music track response schema."""
    id: int
    artist_id: int
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    tags: Optional[List[str]] = None
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class CollaborationCreate(BaseModel):
    """Collaboration request creation schema."""
    target_artist_id: int
    message: str
    project_type: Optional[str] = None


class CollaborationUpdate(BaseModel):
    """Collaboration update schema."""
    status: str  # "accepted" or "declined"


class CollaborationResponse(BaseModel):
    """Collaboration response schema."""
    id: int
    requester_id: int
    target_artist_id: int
    message: str
    project_type: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
