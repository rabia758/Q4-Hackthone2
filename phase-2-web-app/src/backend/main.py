import sys
import os

print(f"DEBUG: Starting Backend. Python Version: {sys.version}")
print(f"DEBUG: Initial sys.path: {sys.path}")

# Ensure the parent directory is in sys.path so 'src' can be imported correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)
    print(f"DEBUG: Added project_root to sys.path: {project_root}")

from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID, uuid4
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

print("DEBUG: Importing local modules...")
# Absolute imports from src.backend
try:
    from src.backend.models import Todo, ChatMessage, ChatMessageCreate, TodoCreate, TodoUpdate
    from src.backend.lib.ai_service import ai_service, AIResponse
    from src.backend.lib.ai_utils import detect_intent, extract_entities, format_response
    from src.backend.services.todo_service import TodoService
    from src.backend.services.chat_service import ChatService
    print("DEBUG: Local modules imported successfully.")
except ImportError as e:
    print(f"DEBUG: ImportError during module import: {e}")
    # Fallback to local imports if absolute fails
    print("DEBUG: Attempting fallback to local imports...")
    from models import Todo, ChatMessage, ChatMessageCreate, TodoCreate, TodoUpdate
    from lib.ai_service import ai_service, AIResponse
    from lib.ai_utils import detect_intent, extract_entities, format_response
    from services.todo_service import TodoService
    from services.chat_service import ChatService

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
print(f"DEBUG: Original DATABASE_URL: {DATABASE_URL[:50]}...")

# Handle Heroku/Neon postgres:// vs postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    print("DEBUG: Replaced postgres:// with postgresql://")

# For Vercel deployment, we might need to handle the database differently
# SQLite can be problematic on serverless platforms due to ephemeral filesystem
if "vercel" in os.getenv("VERCEL_ENV", "") or "Vercel" in os.getenv("HOSTING_ENV", ""):
    # On Vercel, ensure we have a proper database connection
    if DATABASE_URL.startswith("sqlite"):
        print("DEBUG: SQLite detected in Vercel environment - this may cause issues")
        # For now, we'll continue with SQLite, but in production, you'd want PostgreSQL
    else:
        print("DEBUG: Using PostgreSQL database on Vercel")

engine = create_engine(DATABASE_URL, echo=True)

# JWT Setup
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "your-shared-secret-key-at-least-32-chars")
ALGORITHM = "HS256"

security = HTTPBearer(auto_error=False)

class TodoRead(BaseModel):
    id: UUID
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

# Initialize database
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    # Ensure tables exist - important for serverless environments
    SQLModel.metadata.create_all(engine)
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

async def get_current_user(token: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not token:
        print("DEBUG: No token provided, returning demo user")
        return {"id": "demo_user", "email": "demo@example.com"}
    try:
        payload = jwt.decode(token.credentials, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return {"id": "demo_user", "email": "demo@example.com"}
        return {"id": user_id, "email": payload.get("email")}
    except Exception as e:
        print(f"DEBUG: Auth error: {e}, falling back to demo user")
        return {"id": "demo_user", "email": "demo@example.com"}

@app.on_event("startup")
def on_startup():
    try:
        print("DEBUG: Creating tables...")
        create_db_and_tables()
        # Test connection
        with Session(engine) as session:
            session.exec(select(1))
        print("DEBUG: Database connection successful.")
    except Exception as e:
        print(f"DEBUG: Startup error: {e}")
        # In serverless environments, startup events may not work as expected
        # The database creation will happen on first request if needed

@app.get("/")
def read_root():
    return {"status": "online", "message": "Todo API with JWT Auth"}

@app.post("/todos", response_model=TodoRead)
def create_todo_endpoint(todo: TodoCreate, current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
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
    try:
        detected_intent, detected_entities = detect_intent(request.message)

        if detected_intent == "CREATE":
            todo_title = detected_entities.get("title")

            if not todo_title:
                ai_result = await ai_service.process_command(current_user["id"], request.message)
                if ai_result.success and ai_result.entities:
                    todo_title = ai_result.entities.get("title") or ai_result.entities.get("task")

            if todo_title:
                todo_service = TodoService(session)
                # Create a new todo manually to avoid any Pydantic mismatch in service
                db_todo = Todo(
                    user_id=current_user["id"],
                    title=todo_title,
                    completed=False,
                    created_at=datetime.utcnow()
                )
                session.add(db_todo)
                session.commit()
                session.refresh(db_todo)

                response_text = format_response("CREATE", {"title": todo_title})

                chat_service = ChatService(session)
                chat_message_create = ChatMessageCreate(
                    user_id=current_user["id"],
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
                    action_result=db_todo.dict()
                )

        ai_result = await ai_service.process_command(current_user["id"], request.message)

        if ai_result.success and ai_result.intent == "CREATE":
             title = ai_result.entities.get("title") or ai_result.entities.get("task") or ai_result.entities.get("todo")
             if not title:
                 regex_entities = extract_entities(request.message)
                 title = regex_entities.get("title") or request.message
             
             db_todo = Todo(
                 user_id=current_user["id"],
                 title=title,
                 completed=False,
                 created_at=datetime.utcnow()
             )
             session.add(db_todo)
             session.commit()
             session.refresh(db_todo)
             ai_result.action_result = db_todo.dict()
             if not ai_result.response:
                 ai_result.response = f"I've added '{title}' to your list."

        elif ai_result.success and ai_result.intent == "UPDATE":
             title = ai_result.entities.get("title") or ai_result.entities.get("task")
             if title:
                 statement = select(Todo).where(Todo.user_id == current_user["id"], Todo.is_deleted == False)
                 todos = session.exec(statement).all()
                 target_todo = next((t for t in todos if title.lower() in t.title.lower()), None)
                 
                 if target_todo:
                     target_todo.completed = True
                     target_todo.updated_at = datetime.utcnow()
                     session.add(target_todo)
                     session.commit()
                     session.refresh(target_todo)
                     ai_result.action_result = target_todo.dict()
                 else:
                     ai_result.response = f"I couldn't find a task named '{title}' to update."

        elif ai_result.success and ai_result.intent == "DELETE":
             title = ai_result.entities.get("title") or ai_result.entities.get("task")
             if title:
                 statement = select(Todo).where(Todo.user_id == current_user["id"], Todo.is_deleted == False)
                 todos = session.exec(statement).all()
                 target_todo = next((t for t in todos if title.lower() in t.title.lower()), None)
                 
                 if target_todo:
                     target_todo.is_deleted = True
                     session.add(target_todo)
                     session.commit()
                     ai_result.action_result = target_todo.dict()
                 else:
                     ai_result.response = f"I couldn't find a task named '{title}' to delete."

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
        print(f"Chatbot process error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat command: {str(e)}")

@app.get("/chatbot/history")
async def get_chat_history_endpoint(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session)
):
    try:
        chat_service = ChatService(session)
        chat_messages = chat_service.get_chat_history(
            user_id=current_user["id"],
            limit=limit,
            offset=offset
        )
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
