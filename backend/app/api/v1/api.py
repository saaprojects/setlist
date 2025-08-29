"""
Main API router for v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, artists, venues, shows, music, playlists

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(artists.router, prefix="/artists", tags=["artists"])
api_router.include_router(venues.router, prefix="/venues", tags=["venues"])
api_router.include_router(shows.router, prefix="/shows", tags=["shows"])
api_router.include_router(music.router, prefix="/music", tags=["music"])
api_router.include_router(playlists.router, prefix="/playlists", tags=["playlists"])
