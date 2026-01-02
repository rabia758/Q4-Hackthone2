"""
Data models for the chatbot application
"""
from sqlmodel import Field, SQLModel, JSON
import uuid
from datetime import datetime
from typing import Optional, Dict, Any


class Todo(SQLModel, table=True):
    """
    Represents a user's todo item
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(sa_column_kwargs={"nullable": False})
    completed: bool = Field(default=False)
    user_id: str = Field(index=True)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


class ChatMessage(SQLModel, table=True):
    """
    Represents a chat message between user and AI assistant
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True)
    message: str = Field(sa_column_kwargs={"nullable": False})
    intent: str = Field(default=None, index=True)  # CREATE, UPDATE, DELETE, QUERY, etc.
    entities: Dict[str, Any] = Field(default={}, sa_type=JSON)  # Extracted entities from the message
    response: str = Field(sa_column_kwargs={"nullable": False})
    created_at: Optional[datetime] = Field(default=None)
    session_id: Optional[str] = Field(default=None, index=True)


class TodoCreate(SQLModel):
    """
    Schema for creating a new todo
    """
    title: str
    user_id: str


class TodoUpdate(SQLModel):
    """
    Schema for updating an existing todo
    """
    title: Optional[str] = None
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