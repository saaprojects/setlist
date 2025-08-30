"""
Authentication endpoints for the Setlist application.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, decode_access_token
)
from app.models.user import User, UserRole
from app.models.artist import ArtistProfile
from app.schemas.auth import (
    UserCreate, UserLogin, UserResponse, TokenResponse, UserRegistrationResponse
)
from app.schemas.artist import ArtistProfileResponse

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    This endpoint handles registration for all user types (regular users, artists, promoters).
    If registering as an artist, it automatically creates an associated artist profile.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Validate password strength (minimum 8 characters)
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hashed_password,
        display_name=user_data.display_name,
        role=user_data.role,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # If registering as an artist, create associated artist profile
    artist_profile = None
    if user_data.role == UserRole.artist:
        artist_profile = ArtistProfile(
            user_id=new_user.id,
            bio=None,  # Can be updated later
            genres=None,  # Can be updated later
            instruments=None,  # Can be updated later
            location=None,  # Can be updated later
            website=None  # Can be updated later
        )
        db.add(artist_profile)
        db.commit()
        db.refresh(artist_profile)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.username})
    refresh_token = create_access_token(data={"sub": new_user.username}, expires_delta=None)
    
    # Prepare response
    response_data = {
        "user": UserResponse.model_validate(new_user),
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    
    # Include artist profile if created
    if artist_profile:
        response_data["artist_profile"] = ArtistProfileResponse.model_validate(artist_profile)
    
    return UserRegistrationResponse.model_validate(response_data)


@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login user and return access token.
    
    Supports login with either username or email.
    """
    # Find user by username OR email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current user information.
    """
    user = await get_current_user(token, db)
    
    # For artists, also fetch their profile data
    if user.role == "artist":
        artist_profile = db.query(ArtistProfile).filter(
            ArtistProfile.user_id == user.id
        ).first()
        
        if artist_profile:
            # Create a user response with profile data
            user_data = UserResponse.model_validate(user).model_dump()
            user_data.update({
                "bio": artist_profile.bio,
                "genres": artist_profile.genres,
                "instruments": artist_profile.instruments,
                "location": artist_profile.location,
                "website": artist_profile.website
            })
            return user_data
    
    return UserResponse.model_validate(user)


async def get_current_user(token: str, db: Session) -> User:
    """
    Get the current authenticated user from the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user
