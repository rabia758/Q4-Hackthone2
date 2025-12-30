"""
Chatbot API endpoints for processing natural language commands
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from .auth import get_current_user, User
from ...models import Todo, TodoCreate, ChatMessageCreate
from ...services.todo_service import TodoService
from ...services.chat_service import ChatService
from .. import get_db
from ....lib.ai_service import ai_service, AIResponse
from ....lib.ai_utils import detect_intent, extract_entities, format_response

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = {}
    response: str = ""
    action_result: Optional[Dict[str, Any]] = None


@router.post("/process", response_model=ChatResponse)
async def process_chat_command(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Process a natural language command from the user
    """
    try:
        # First, try to detect intent using our rule-based system
        detected_intent, detected_entities = detect_intent(request.message)

        # If we detected a CREATE intent, process it
        if detected_intent == "CREATE":
            # Extract the todo title from entities
            todo_title = detected_entities.get("title")

            if not todo_title:
                # If we couldn't extract a title, ask the AI for help
                ai_result = await ai_service.process_command(current_user.id, request.message)
                if ai_result.success and ai_result.entities:
                    todo_title = ai_result.entities.get("title", request.message)

            if todo_title:
                # Create the todo using the todo service
                todo_service = TodoService(db)
                todo_create = TodoCreate(title=todo_title, user_id=current_user.id)
                new_todo = todo_service.create_todo(todo_create)

                response_text = format_response("CREATE", {"title": todo_title})

                # Log the chat message to database
                chat_service = ChatService(db)
                chat_message_create = ChatMessageCreate(
                    user_id=current_user.id,
                    message=request.message,
                    intent="CREATE",
                    entities=detected_entities,
                    response=response_text
                )
                chat_service.create_chat_message(chat_message_create)

                return ChatResponse(
                    success=True,
                    intent="CREATE",
                    entities=detected_entities,
                    response=response_text,
                    action_result=new_todo.dict()
                )

        # For other intents or if rule-based detection fails, use AI service
        ai_result = await ai_service.process_command(current_user.id, request.message)

        # Log the chat message to database
        chat_service = ChatService(db)
        chat_message_create = ChatMessageCreate(
            user_id=current_user.id,
            message=request.message,
            intent=ai_result.intent,
            entities=ai_result.entities,
            response=ai_result.response
        )
        chat_service.create_chat_message(chat_message_create)

        return ChatResponse(
            success=ai_result.success,
            intent=ai_result.intent,
            entities=ai_result.entities,
            response=ai_result.response,
            action_result=ai_result.action_result
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat command: {str(e)}")


@router.get("/history")
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    db=Depends(get_db)
):
    """
    Retrieve chat history for the current user
    """
    try:
        # Use the chat service to get chat history
        chat_service = ChatService(db)
        chat_messages = chat_service.get_chat_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )

        # Convert to response format
        history = []
        for msg in chat_messages:
            history.append({
                "id": str(msg.id),
                "user_id": msg.user_id,
                "message": msg.message,
                "intent": msg.intent,
                "entities": msg.entities,
                "response": msg.response,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })

        return {"messages": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")