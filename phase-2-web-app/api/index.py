import sys
import os

# Add the project root to sys.path so 'src' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.main import app

# Set root_path for Vercel deployment so /api/todos matches /todos
app.root_path = "/api"
