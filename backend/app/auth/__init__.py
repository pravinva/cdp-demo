from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config import get_settings

settings = get_settings()
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> Dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict:
    """
    Extract and validate user from JWT token
    Returns user context with user_id, tenant_id, email, etc.
    In development mode, allows bypassing authentication
    """
    # In development, allow bypassing auth
    if settings.ENVIRONMENT == "development" and not credentials:
        return {
            "user_id": "dev_user",
            "tenant_id": "demo_tenant",
            "email": "dev@example.com",
            "name": "Development User"
        }
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # In development, allow bypass with special token
    if settings.ENVIRONMENT == "development" and token == "dev-token":
        return {
            "user_id": "dev_user",
            "tenant_id": "demo_tenant",
            "email": "dev@example.com",
            "name": "Development User"
        }
    
    # Verify token
    payload = verify_token(token)
    
    # Extract user information
    user_id = payload.get("sub") or payload.get("user_id")
    tenant_id = payload.get("tenant_id")
    email = payload.get("email")
    name = payload.get("name")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user identifier"
        )
    
    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "email": email,
        "name": name,
        "permissions": payload.get("permissions", []),
        "roles": payload.get("roles", [])
    }


async def get_tenant_from_user(user: Dict = Depends(get_current_user)) -> str:
    """Extract tenant_id from authenticated user"""
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have a tenant assigned"
        )
    return tenant_id


def get_user_id_from_context(user: Dict = Depends(get_current_user)) -> str:
    """Extract user_id from authenticated user context"""
    return user.get("user_id", "system")

