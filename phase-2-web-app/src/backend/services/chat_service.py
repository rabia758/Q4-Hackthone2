"""
Chat service for handling chat message operations
"""
from typing import List, Optional
import uuid
from datetime import datetime
from sqlmodel import Session, select
from models import ChatMessage, ChatMessageCreate


class ChatService:
    """
    Service class for handling chat message operations
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_chat_message(self, chat_message_create: ChatMessageCreate) -> ChatMessage:
        """
        Create a new chat message
        """
        chat_message = ChatMessage(
            user_id=chat_message_create.user_id,
            message=chat_message_create.message,
            intent=chat_message_create.intent,
            entities=chat_message_create.entities,
            response=chat_message_create.response,
            session_id=chat_message_create.session_id,
            created_at=datetime.now()
        )
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message

    def get_chat_history(self, user_id: str, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """
        Get chat history for a user
        """
        query = select(ChatMessage).where(
            ChatMessage.user_id == user_id
        ).order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit)

        return self.db.exec(query).all()

    def get_chat_by_session(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """
        Get chat messages for a specific session
        """
        query = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit)

        return self.db.exec(query).all()