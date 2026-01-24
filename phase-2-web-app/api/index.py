import sys
import os

# Add the project root to sys.path so 'src' can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'src', 'backend')

if project_root not in sys.path:
    sys.path.append(project_root)

# Add src/backend to sys.path so 'models', 'lib', 'services' can be imported directly
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import the FastAPI app
from src.backend.main import app

# Set root_path for Vercel deployment so /api/todos matches /todos
app.root_path = "/api"
