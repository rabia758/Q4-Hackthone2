"""
Database migration for chat_messages table
"""

import uuid
from sqlmodel import Field, SQLModel


class ChatMessage(SQLModel, table=True):
    """
    Represents a chat message between user and AI assistant
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True)
    message: str = Field(sa_column_kwargs={"nullable": False})
    intent: str = Field(default=None, index=True)  # CREATE, UPDATE, DELETE, QUERY, etc.
    entities: dict = Field(default={})  # Extracted entities from the message
    response: str = Field(sa_column_kwargs={"nullable": False})
    created_at: str = Field(default=None, sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"})
    session_id: str = Field(default=None, index=True)