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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("DEBUG: Importing local modules...")
try:
    from src.backend.database import create_db_and_tables
    from src.backend.api.v1.chatbot.main import router as chatbot_router
    print("DEBUG: Local modules imported successfully.")
except ImportError as e:
    print(f"DEBUG: ImportError during module import: {e}")
    print("DEBUG: Attempting fallback to local imports...")
    from database import create_db_and_tables
    from api.v1.chatbot.main import router as chatbot_router

app = FastAPI(title="AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"Database startup error: {e}")

@app.get("/")
def read_root():
    return {"status": "online", "message": "AI Chatbot API Running"}

# Include the router with prefix /v1 (FastAPI will handle /api via root_path)
app.include_router(chatbot_router, prefix="/v1")
