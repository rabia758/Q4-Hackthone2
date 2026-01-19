import sys
import os

print(f"DEBUG: index.py entering. sys.path: {sys.path}")

# Add the project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
    print(f"DEBUG: added {project_root} to sys.path")

from src.backend.main import app

# Set root_path for Vercel deployment
app.root_path = "/api"
print("DEBUG: app imported and root_path set to /api")
