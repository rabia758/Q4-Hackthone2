"""
Data models for the application
"""
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON
from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional, Dict, Any


class Todo(SQLModel, table=True):
    """
    Represents a user's todo item
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)
    is_deleted: bool = Field(default=False)
    user_id: str = Field(index=True)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class ChatMessage(SQLModel, table=True):
    """
    Represents a chat message between user and AI assistant
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)
    message: str = Field(nullable=False)
    intent: str = Field(default=None, index=True)  # CREATE, UPDATE, DELETE, QUERY, etc.
    entities: Dict[str, Any] = Field(default={}, sa_type=JSON)  # Extracted entities from the message
    response: str = Field(nullable=False)
    created_at: Optional[datetime] = Field(default=None)
    session_id: Optional[str] = Field(default=None, index=True)


class TodoCreate(SQLModel):
    """
    Schema for creating a new todo
    """
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoUpdate(SQLModel):
    """
    Schema for updating an existing todo
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class ChatMessageCreate(SQLModel):
    """
    Schema for creating a new chat message
    """
    user_id: str
    message: str
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = {}
    response: str
    session_id: Optional[str] = None