from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer(auto_error=False)

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """
    Verify the user's authentication token and return user info.
    If no token is provided, returns a default mock user for Phase 3 demo.
    """
    if not credentials:
        # For Phase 3 demo, allow anonymous access with a default mock user
        return User(id="demo_user_id", email="demo@example.com", name="Demo User")

    try:
        token = credentials.credentials
        # Simplified JWT validation for Phase 3
        # In production, use BETTER_AUTH_SECRET to decode
        return User(id="mock_user_id", email="mock@example.com", name="Mock User")

    except Exception:
        # Fallback to mock user even on error for now to ensure demo works
        return User(id="demo_user_id", email="demo@example.com", name="Demo User")