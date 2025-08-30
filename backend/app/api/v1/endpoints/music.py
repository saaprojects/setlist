"""
General music system endpoints for the Setlist application.
These endpoints handle public music browsing, streaming, analytics, and collaborations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import io

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user, oauth2_scheme
from app.models.music import MusicTrack
from app.models.user import User, UserRole
from app.schemas.music import MusicTrackResponse
from app.schemas.music import (
    MusicTrackCreate, MusicTrackUpdate, MusicTrackAnalytics,
    MusicCollaborationCreate, MusicCollaborationResponse,
    MusicContributionCreate, MusicContributionResponse
)

router = APIRouter()


# Public Music Browsing Endpoints

@router.get("/tracks", response_model=dict)
async def browse_public_tracks(
    genre: Optional[str] = None,
    artist: Optional[str] = None,
    title: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Browse public music tracks.
    
    This endpoint allows users to discover and browse public music tracks.
    """
    # Get all public tracks first, then filter in Python
    tracks = db.query(MusicTrack).filter(MusicTrack.is_public == True).all()
    
    # Filter by genre if specified
    if genre:
        tracks = [track for track in tracks if track.genre == genre]
    
    # Filter by artist if specified
    if artist:
        tracks = [track for track in tracks if track.artist and artist.lower() in track.artist.username.lower()]
    
    # Filter by title if specified
    if title:
        tracks = [track for track in tracks if title.lower() in track.title.lower()]
    
    # Apply pagination
    total_tracks = len(tracks)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    tracks = tracks[start_idx:end_idx]
    
    # Calculate pagination info
    total_pages = (total_tracks + limit - 1) // limit
    
    return {
        "tracks": [MusicTrackResponse.model_validate(track) for track in tracks],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_tracks,
            "pages": total_pages
        }
    }


@router.post("/tracks", response_model=MusicTrackResponse, status_code=status.HTTP_201_CREATED)
async def upload_music_track(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    tags: Optional[List[str]] = Form(None),
    is_public: bool = Form(True),
    audio_file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Upload a new music track.
    
    This endpoint allows artists to upload music tracks.
    """
    # Validate file type
    if not audio_file.content_type.startswith("audio/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only audio files are allowed."
        )
    
    # Validate file size (max 10MB)
    if audio_file.size and audio_file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Validate genre if provided
    valid_genres = ["rock", "pop", "jazz", "blues", "country", "electronic", "hip-hop", "classical", "folk", "metal", "punk", "reggae", "r&b", "soul", "alternative", "indie"]
    if genre and genre not in valid_genres:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid genre. Must be one of: {', '.join(valid_genres)}"
        )
    

    
    # Get authenticated user
    user = await get_current_user(token, db)
    
    # For now, return a mock URL (in production, you'd upload to S3/cloud storage)
    audio_url = f"https://example.com/audio/{user.username}/{audio_file.filename}"
    
    # Create music track
    music_track = MusicTrack(
        artist_id=user.id,
        title=title,
        description=description,
        genre=genre,
        tags=tags,
        audio_url=audio_url,
        is_public=is_public
    )
    
    db.add(music_track)
    db.commit()
    db.refresh(music_track)
    
    # Convert SQLAlchemy model to dict for Pydantic validation
    track_dict = {
        "id": music_track.id,
        "artist_id": music_track.artist_id,
        "uploaded_by": user.username,  # Add artist username
        "title": music_track.title,
        "description": music_track.description,
        "genre": music_track.genre,
        "tags": music_track.tags,
        "audio_url": music_track.audio_url,
        "duration": music_track.duration,
        "file_size": music_track.file_size,
        "is_public": music_track.is_public,
        "created_at": music_track.created_at,
        "updated_at": music_track.updated_at
    }
    
    return MusicTrackResponse.model_validate(track_dict)


# Music Streaming Endpoints

@router.get("/tracks/{track_id}/stream")
async def stream_music_track(
    track_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stream a music track.
    
    This endpoint allows users to stream public tracks or their own private tracks.
    """
    # Get the track
    track = db.query(MusicTrack).filter(MusicTrack.id == track_id).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # Check if user can access this track
    # For now, we'll allow access to public tracks only
    # TODO: Add authentication to allow artists to stream their private tracks
    if not track.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This track is private"
        )
    
    # For now, return a mock stream since we don't have actual audio files stored
    # In production, this would stream the actual audio file
    mock_audio_data = b"mock-audio-stream-data"
    
    # Check for range requests
    range_header = request.headers.get("range")
    if range_header:
        # Parse range request (e.g., "bytes=0-1023")
        try:
            range_str = range_header.replace("bytes=", "")
            start, end = map(int, range_str.split("-"))
            content_length = end - start + 1
            mock_audio_data = mock_audio_data[start:end+1]
            
            return Response(
                content=mock_audio_data,
                media_type="audio/mpeg",
                status_code=206,
                headers={
                    "Content-Range": f"bytes {start}-{end}/{len(mock_audio_data)}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length)
                }
            )
        except (ValueError, IndexError):
            pass
    
    # Return full track
    return Response(
        content=mock_audio_data,
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(mock_audio_data))
        }
    )


# Music Analytics Endpoints

@router.get("/tracks/{track_id}/analytics", response_model=MusicTrackAnalytics)
async def get_track_analytics(
    track_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a music track.
    
    This endpoint allows artists to view analytics for their own tracks.
    """
    # Get authenticated user
    user = await get_current_user(token, db)
    
    # Get the track
    track = db.query(MusicTrack).filter(MusicTrack.id == track_id).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # Check if user owns this track
    if track.artist_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view analytics for your own tracks"
        )
    
    # For now, return mock analytics
    # TODO: Implement actual analytics tracking
    analytics = MusicTrackAnalytics(
        track_id=track_id,
        play_count=0,  # TODO: Track actual plays
        download_count=0,  # TODO: Track downloads
        like_count=0,  # TODO: Track likes
        share_count=0,  # TODO: Track shares
        average_listen_duration=0,  # TODO: Track listen duration
        created_at=track.created_at,
        updated_at=track.updated_at
    )
    
    return analytics


# Music Collaboration Endpoints

@router.post("/tracks/{track_id}/collaborations", response_model=MusicCollaborationResponse)
async def create_music_collaboration(
    track_id: int,
    collaboration_data: MusicCollaborationCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Create a collaboration request for a music track.
    
    This endpoint allows artists to request collaborations on tracks.
    """
    # Get authenticated user
    user = await get_current_user(token, db)
    
    # Get the track
    track = db.query(MusicTrack).filter(MusicTrack.id == track_id).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # Check if user owns this track
    if track.artist_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create collaborations on your own tracks"
        )
    
    # For now, return a mock collaboration response
    # TODO: Implement actual collaboration system
    collaboration = MusicCollaborationResponse(
        id=1,  # Mock ID
        track_id=track_id,
        collaborator_id=collaboration_data.collaborator_id,
        role=collaboration_data.role,
        message=collaboration_data.message,
        status="pending",
        created_at=track.created_at,
        updated_at=track.updated_at
    )
    
    return collaboration


@router.post("/tracks/{track_id}/contributions", response_model=MusicContributionResponse)
async def create_music_contribution(
    track_id: int,
    contribution_data: MusicContributionCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Create a contribution to a music track.
    
    This endpoint allows collaborators to contribute to tracks.
    """
    # Get authenticated user
    user = await get_current_user(token, db)
    
    # Get the track
    track = db.query(MusicTrack).filter(MusicTrack.id == track_id).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # For now, return a mock contribution response
    # TODO: Implement actual contribution system
    contribution = MusicContributionResponse(
        id=1,  # Mock ID
        track_id=track_id,
        contributor_id=user.id,
        type=contribution_data.type,
        description=contribution_data.description,
        file_url=contribution_data.file_url,
        created_at=track.created_at,
        updated_at=track.updated_at
    )
    
    return contribution


# Music Management Endpoints

@router.get("/tracks/me", response_model=dict)
async def get_artist_tracks(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current artist's tracks.
    
    This endpoint returns all tracks by the currently authenticated artist.
    """
    user = await get_current_user(token, db)
    
    tracks = db.query(MusicTrack).filter(MusicTrack.artist_id == user.id).all()
    
    track_list = [MusicTrackResponse.model_validate(track) for track in tracks]
    
    return {"tracks": track_list}


@router.put("/tracks/{track_id}", response_model=MusicTrackResponse)
async def update_music_track(
    track_id: int,
    track_update: MusicTrackUpdate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Update a music track.
    
    This endpoint allows artists to update their track information.
    """
    user = await get_current_user(token, db)
    
    # Find track and verify ownership
    track = db.query(MusicTrack).filter(
        MusicTrack.id == track_id,
        MusicTrack.artist_id == user.id
    ).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    # Update track fields
    if track_update.title is not None:
        track.title = track_update.title
    if track_update.description is not None:
        track.description = track_update.description
    if track_update.genre is not None:
        track.genre = track_update.genre
    if track_update.tags is not None:
        track.tags = track_update.tags
    if track_update.is_public is not None:
        track.is_public = track_update.is_public
    
    db.commit()
    db.refresh(track)
    
    return MusicTrackResponse.model_validate(track)


@router.delete("/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_music_track(
    track_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Delete a music track.
    
    This endpoint allows artists to delete their tracks.
    """
    user = await get_current_user(token, db)
    
    # Find track and verify ownership
    track = db.query(MusicTrack).filter(
        MusicTrack.id == track_id,
        MusicTrack.artist_id == user.id
    ).first()
    
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Track not found"
        )
    
    db.delete(track)
    db.commit()
    
    return None
