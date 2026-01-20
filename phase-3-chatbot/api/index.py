import sys
import os
from mangum import Mangum

# Add the project root to sys.path so 'src' can be imported
sys_path_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path_dir not in sys.path:
    sys.path.append(sys_path_dir)

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