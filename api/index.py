import sys
import os

# For the root API handler, we need to point to phase-2-web-app
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(os.path.dirname(current_dir), 'phase-2-web-app')
backend_dir = os.path.join(project_root, 'src', 'backend')

if project_root not in sys.path:
    sys.path.append(project_root)

# Add src/backend to sys.path so 'models', 'lib', 'services' can be imported directly
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import the FastAPI app from the phase-2-web-app source
try:
    from src.backend.main import app
    # Set root_path for Vercel deployment so /api/todos matches /todos
    app.root_path = "/api"
except ImportError as e:
    print(f"Error importing from phase-2-web-app: {e}")
    # Fallback or error handling
    raise