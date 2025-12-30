"""
Authentication middleware for chatbot endpoints
"""
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Verify the user's authentication token and return user info
    """
    try:
        # In a real implementation, this would verify the token with Better Auth
        # For now, we'll simulate the authentication process
        token = credentials.credentials

        # This is a simplified version - in production, verify with Better Auth
        # For now, we'll return a mock user (this would be replaced with actual verification)
        # In the actual implementation, you would decode and verify the JWT token
        # and return the actual user information
        return User(id="mock_user_id", email="mock@example.com", name="Mock User")

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")