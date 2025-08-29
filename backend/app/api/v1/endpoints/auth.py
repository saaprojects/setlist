"""
Authentication endpoints for user login, registration, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User, UserRole

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserLogin(BaseModel):
    """User login request model."""
    username: str  # Can be email or username
    password: str


class UserRegister(BaseModel):
    """User registration request model."""
    email: EmailStr
    username: str
    password: str
    display_name: str
    role: UserRole


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: EmailStr
    username: str
    display_name: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str


class RegistrationResponse(BaseModel):
    """User registration response model."""
    user: UserResponse
    access_token: str
    refresh_token: str


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    This endpoint allows users to create new accounts with basic information.
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
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.username})
    refresh_token = create_access_token(data={"sub": new_user.username}, expires_delta=None)  # TODO: Implement proper refresh token
    
    return RegistrationResponse(
        user=UserResponse.model_validate(new_user),
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    
    This endpoint validates user credentials and returns a JWT token
    for authenticated requests.
    """
    # Try to find user by email or username
    user = db.query(User).filter(
        (User.email == user_credentials.username) | (User.username == user_credentials.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Generate access token
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/token", response_model=Token)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Get access token using OAuth2 password flow.
    
    This endpoint is used by the OAuth2PasswordBearer for token generation.
    """
    # TODO: Implement OAuth2 token generation
    # This is a placeholder - we'll implement after writing tests
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token generation not yet implemented"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user information.
    
    This endpoint returns the profile of the currently authenticated user.
    """
    # TODO: Implement current user retrieval
    # This is a placeholder - we'll implement after writing tests
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Current user retrieval not yet implemented"
    )


@router.post("/logout")
async def logout_user(token: str = Depends(oauth2_scheme)):
    """
    Logout user by invalidating their token.
    
    This endpoint invalidates the current user's access token.
    """
    # TODO: Implement user logout logic
    # This is a placeholder - we'll implement after writing tests
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User logout not yet implemented"
    )
