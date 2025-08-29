"""
Shared type definitions for the Setlist application.
These types ensure consistency between backend and frontend.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID


class UserRole(str, Enum):
    """User roles in the system."""
    ARTIST = "artist"
    PROMOTER = "promoter"
    VENUE = "venue"
    USER = "user"
    ADMIN = "admin"


class MusicGenre(str, Enum):
    """Music genres supported by the platform."""
    ROCK = "rock"
    POP = "pop"
    JAZZ = "jazz"
    BLUES = "blues"
    COUNTRY = "country"
    HIP_HOP = "hip_hop"
    ELECTRONIC = "electronic"
    FOLK = "folk"
    CLASSICAL = "classical"
    METAL = "metal"
    PUNK = "punk"
    REGGAE = "reggae"
    R_AND_B = "r_andb"
    SOUL = "soul"
    FUNK = "funk"
    LATIN = "latin"
    WORLD = "world"
    EXPERIMENTAL = "experimental"
    OTHER = "other"


class FileType(str, Enum):
    """Types of files that can be uploaded."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"


class ShowStatus(str, Enum):
    """Status of a show/event."""
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class CollaborationStatus(str, Enum):
    """Status of collaboration requests."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# Base models for common entities
class BaseEntity:
    """Base class for all entities."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserProfile(BaseEntity):
    """User profile information."""
    username: str
    email: str
    role: UserRole
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    location: Optional[str]
    website: Optional[str]
    social_links: Dict[str, str]
    is_verified: bool
    is_active: bool


class ArtistProfile(UserProfile):
    """Artist-specific profile information."""
    band_name: Optional[str]
    genres: List[MusicGenre]
    instruments: List[str]
    experience_years: int
    influences: List[str]
    achievements: List[str]


class VenueProfile(UserProfile):
    """Venue-specific profile information."""
    venue_name: str
    capacity: int
    address: str
    city: str
    state: str
    country: str
    venue_type: str
    amenities: List[str]


class PromoterProfile(UserProfile):
    """Promoter-specific profile information."""
    company_name: Optional[str]
    specializations: List[MusicGenre]
    experience_years: int
    past_events: List[str]


class MusicTrack(BaseEntity):
    """Music track information."""
    title: str
    artist_id: UUID
    album: Optional[str]
    genres: List[MusicGenre]
    duration: int  # in seconds
    file_url: str
    file_size: int
    file_type: FileType
    is_explicit: bool
    release_date: Optional[datetime]
    plays_count: int
    likes_count: int


class VideoContent(BaseEntity):
    """Video content information."""
    title: str
    artist_id: UUID
    description: Optional[str]
    video_url: str
    video_type: str  # "youtube", "uploaded", etc.
    duration: Optional[int]
    thumbnail_url: Optional[str]
    views_count: int
    likes_count: int


class Show(BaseEntity):
    """Show/event information."""
    title: str
    description: str
    venue_id: UUID
    promoter_id: UUID
    date: datetime
    doors_open: datetime
    show_start: datetime
    show_end: datetime
    status: ShowStatus
    ticket_price: Optional[float]
    ticket_url: Optional[str]
    poster_url: Optional[str]
    genres: List[MusicGenre]
    age_restriction: Optional[str]
    capacity: Optional[int]


class ShowLineup(BaseEntity):
    """Lineup for a show."""
    show_id: UUID
    artist_id: UUID
    set_time: Optional[datetime]
    set_duration: Optional[int]  # in minutes
    order: int
    is_headliner: bool


class Collaboration(BaseEntity):
    """Collaboration between artists."""
    initiator_id: UUID
    collaborator_id: UUID
    project_name: str
    description: str
    status: CollaborationStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]


class Playlist(BaseEntity):
    """User playlist."""
    name: str
    user_id: UUID
    description: Optional[str]
    is_public: bool
    tracks: List[UUID]  # List of track IDs
    cover_image_url: Optional[str]


class Message(BaseEntity):
    """Message between users."""
    sender_id: UUID
    recipient_id: UUID
    subject: str
    content: str
    is_read: bool
    read_at: Optional[datetime]


# API Response types
class APIResponse:
    """Standard API response format."""
    success: bool
    message: str
    data: Optional[Any]
    errors: Optional[List[str]]


class PaginatedResponse(APIResponse):
    """Paginated API response."""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


# Search and filter types
class SearchFilters:
    """Search filters for various entities."""
    query: Optional[str]
    genres: Optional[List[MusicGenre]]
    location: Optional[str]
    date_range: Optional[tuple[datetime, datetime]]
    price_range: Optional[tuple[float, float]]
    limit: int = 20
    offset: int = 0


class SortOptions:
    """Sorting options for search results."""
    field: str
    direction: str  # "asc" or "desc"
