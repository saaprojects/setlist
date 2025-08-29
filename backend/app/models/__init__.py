# Models package

from .base import Base, BaseModel
from .user import User, UserRole
from .artist import ArtistProfile, Collaboration
from .music import MusicTrack

__all__ = [
    "Base",
    "BaseModel", 
    "User",
    "UserRole",
    "ArtistProfile",
    "Collaboration",
    "MusicTrack"
]
