"""
Authentication API endpoints
Login and token management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from ..auth import create_access_token, verify_token, get_current_user
from ..config import get_settings
from datetime import timedelta

router = APIRouter()
settings = get_settings()


class LoginRequest(BaseModel):
    email: str
    tenant_id: str
    password: Optional[str] = None  # In production, validate password


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    tenant_id: str


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - generates JWT token
    In production, validate credentials against user database
    """
    # In development, accept any credentials
    if settings.ENVIRONMENT == "development":
        # Create token with user info
        token_data = {
            "sub": f"user_{request.email}",
            "user_id": f"user_{request.email}",
            "tenant_id": request.tenant_id,
            "email": request.email,
            "name": request.email.split("@")[0]
        }
    else:
        # In production, validate credentials
        # TODO: Validate against user database
        # For now, accept any email/tenant_id combination
        token_data = {
            "sub": f"user_{request.email}",
            "user_id": f"user_{request.email}",
            "tenant_id": request.tenant_id,
            "email": request.email,
            "name": request.email.split("@")[0]
        }
    
    # Create access token
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=token_data["user_id"],
        tenant_id=token_data["tenant_id"]
    )


@router.get("/me")
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return user

