import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID, uuid4
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
# Use SQLite for local development if no DATABASE_URL is set
engine = create_engine(DATABASE_URL, echo=True)

# JWT Setup
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-shared-secret-key-at-least-32-chars")
ALGORITHM = "HS256"

security = HTTPBearer()

# Define the models
from models import Todo, ChatMessage, ChatMessageCreate, TodoCreate, TodoUpdate

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    is_deleted: bool = False

class TodoRead(TodoBase):
    id: UUID
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

# Initialize database
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# FastAPI app
app = FastAPI(title="Todo API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        # In a real app, you might check if the user exists in a Users table here
        return {"id": user_id, "email": payload.get("email")}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

@app.get("/")
def read_root():
    return {"message": "Todo API with JWT Auth"}

@app.post("/todos", response_model=TodoRead)
def create_todo(todo: TodoCreate, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    db_todo = Todo(
        user_id=current_user["id"],
        title=todo.title,
        description=todo.description,
        completed=todo.completed,
        created_at=datetime.utcnow()
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@app.get("/todos", response_model=List[TodoRead])
def read_todos(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    # Return all tasks including deleted ones for the user (Frontend will filter)
    statement = select(Todo).where(Todo.user_id == current_user["id"]).order_by(Todo.created_at.desc())
    results = session.exec(statement).all()
    return results

@app.get("/todos/{todo_id}", response_model=TodoRead)
def read_todo(todo_id: UUID, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user["id"])
    todo = session.exec(statement).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: UUID, todo_update: TodoUpdate, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user["id"])
    db_todo = session.exec(statement).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    update_data = todo_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    
    db_todo.updated_at = datetime.utcnow()
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: UUID, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user["id"])
    todo = session.exec(statement).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Soft delete
    todo.is_deleted = True
    session.add(todo)
    session.commit()
    return {"message": "Todo deleted"}


# Chatbot endpoints
from pydantic import BaseModel
from typing import Optional
from lib.ai_service import ai_service, AIResponse
from lib.ai_utils import detect_intent, extract_entities, format_response
from services.todo_service import TodoService
from services.chat_service import ChatService


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    success: bool
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = {}
    response: str = ""
    action_result: Optional[Dict[str, Any]] = None


@app.post("/chatbot/process", response_model=ChatResponse)
async def process_chat_command(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Process a natural language command from the user
    """
    try:
        # First, try to detect intent using our rule-based system
        detected_intent, detected_entities = detect_intent(request.message)
        print(f"DEBUG: Rule-based Intent: {detected_intent}, Entities: {detected_entities}")

        # If we detected a CREATE intent, process it
        if detected_intent == "CREATE":
            # Extract the todo title from entities
            todo_title = detected_entities.get("title")

            if not todo_title:
                # If we couldn't extract a title, ask the AI for help
                ai_result = await ai_service.process_command(current_user["id"], request.message)
                if ai_result.success and ai_result.entities:
                    todo_title = ai_result.entities.get("title", request.message)

            if todo_title:
                print(f"DEBUG: Creating Todo with title: {todo_title}")
                # Create the todo using the todo service
                todo_service = TodoService(session)
                todo_create = TodoCreate(title=todo_title, user_id=current_user["id"])
                new_todo = todo_service.create_todo(todo_create)

                response_text = format_response("CREATE", {"title": todo_title})

                # Log the chat message to database
                chat_service = ChatService(session)
                chat_message_create = ChatMessageCreate(
                    user_id=current_user["id"],
                    message=request.message,
                    intent="CREATE",
                    entities=detected_entities,
                    response=response_text
                )
                chat_service.create_chat_message(chat_message_create)
                
                print(f"DEBUG: Returning Rule-based Response with Action Result: {new_todo.dict()}")
                return ChatResponse(
                    success=True,
                    intent="CREATE",
                    entities=detected_entities,
                    response=response_text,
                    action_result=new_todo.dict()
                )

        # For other intents or if rule-based detection fails, use AI service
        print("DEBUG: Falling back to AI Service")
        ai_result = await ai_service.process_command(current_user["id"], request.message)
        print(f"DEBUG: AI Result - Intent: {ai_result.intent}, Entities: {ai_result.entities}")

        # Handle CREATE intent from AI service
        if ai_result.success and ai_result.intent == "CREATE":
             # Try multiple ways to get the title
             title = ai_result.entities.get("title") or ai_result.entities.get("task") or ai_result.entities.get("todo")
             
             if not title:
                 # Fallback: Try our regex extraction
                 regex_entities = extract_entities(request.message)
                 title = regex_entities.get("title")
             
             if not title:
                 # Final Fallback: Use the message itself, maybe cleaning it slightly?
                 # For now, just use the message to ensure SOMETHING is created.
                 title = request.message
                 
             print(f"DEBUG: AI Service detected CREATE. Final Title: {title}")
             
             if title:
                 todo_service = TodoService(session)
                 todo_create = TodoCreate(title=title, user_id=current_user["id"])
                 new_todo = todo_service.create_todo(todo_create)
                 ai_result.action_result = new_todo.dict()
                 print(f"DEBUG: Created Todo from AI: {ai_result.action_result}")
                 
                 # Force response update to be natural if needed
                 if not ai_result.response:
                     ai_result.response = f"I've added '{title}' to your list."

        # Handle UPDATE intent (e.g., "mark buy milk as done")
        elif ai_result.success and ai_result.intent == "UPDATE":
             title = ai_result.entities.get("title") or ai_result.entities.get("task")
             if title:
                 # Find the task
                 statement = select(Todo).where(Todo.user_id == current_user["id"], Todo.is_deleted == False)
                 todos = session.exec(statement).all()
                 # Simple fuzzy match: find todo that contains the title text
                 target_todo = next((t for t in todos if title.lower() in t.title.lower()), None)
                 
                 if target_todo:
                     target_todo.completed = True # Assume update means complete for now
                     target_todo.updated_at = datetime.utcnow()
                     session.add(target_todo)
                     session.commit()
                     session.refresh(target_todo)
                     ai_result.action_result = target_todo.dict()
                     print(f"DEBUG: Updated Todo from AI: {ai_result.action_result}")
                 else:
                     ai_result.response = f"I couldn't find a task named '{title}' to update."

        # Handle DELETE intent
        elif ai_result.success and ai_result.intent == "DELETE":
             title = ai_result.entities.get("title") or ai_result.entities.get("task")
             if title:
                 # Find the task
                 statement = select(Todo).where(Todo.user_id == current_user["id"], Todo.is_deleted == False)
                 todos = session.exec(statement).all()
                 target_todo = next((t for t in todos if title.lower() in t.title.lower()), None)
                 
                 if target_todo:
                     target_todo.is_deleted = True
                     session.add(target_todo)
                     session.commit()
                     ai_result.action_result = target_todo.dict()
                     print(f"DEBUG: Deleted Todo from AI: {ai_result.action_result}")
                 else:
                     ai_result.response = f"I couldn't find a task named '{title}' to delete."

        # Log the chat message to database
        chat_service = ChatService(session)
        chat_message_create = ChatMessageCreate(
            user_id=current_user["id"],
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


@app.get("/chatbot/history")
async def get_chat_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    """
    Retrieve chat history for the current user
    """
    try:
        # Use the chat service to get chat history
        chat_service = ChatService(session)
        chat_messages = chat_service.get_chat_history(
            user_id=current_user["id"],
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
