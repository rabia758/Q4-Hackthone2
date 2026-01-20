import sys
import os
from mangum import Mangum

# Add the project root to sys.path so 'src' can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
backend_dir = os.path.join(project_root, 'src', 'backend')

if project_root not in sys.path:
    sys.path.append(project_root)
    
# Add src/backend to sys.path so local imports work if needed
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Import the FastAPI app
from src.backend.main import app

# Set root_path for Vercel deployment so /api/todos matches /todos
app.root_path = "/api"

# Create the mangum handler for serverless deployment
mangum_handler = Mangum(app, lifespan="off")

def main_handler(event, context):
    """
    Main handler for Vercel Python runtime
    """
    # Update environment variables if needed
    if 'NEXT_PUBLIC_API_URL' not in os.environ:
        os.environ['NEXT_PUBLIC_API_URL'] = '/api'

    # Handle the request using Mangum
    response = mangum_handler(event, context)
    return response

# Make the handler available for Vercel
handler = main_handler
