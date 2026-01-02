import sys
import os

# Ensure src is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(src_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.database import create_db_and_tables
from src.backend.api.v1.chatbot.main import router as chatbot_router

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
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "AI Chatbot API Running"}

# Include the router with prefix to match /api/v1/chatbot/...
app.include_router(chatbot_router, prefix="/api/v1")
