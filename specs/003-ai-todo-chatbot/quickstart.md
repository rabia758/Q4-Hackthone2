# Quickstart Guide: AI-Powered Todo Chatbot

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL database
- Better Auth configured
- OpenAI API key (or alternative LLM service)

## Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Navigate to the web app directory
cd phase-2-web-app

# Install frontend dependencies
npm install

# Install backend dependencies
cd src/backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create/update `.env` file in `phase-2-web-app/`:

```env
# OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here

# Database configuration (existing)
DATABASE_URL=postgresql://user:password@localhost:5432/todo_app

# Better Auth configuration (existing)
# ... existing auth variables
```

### 3. Database Setup

The chatbot will use the existing database with an additional table for chat history:

```sql
-- Create the chat_messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(50),
    entities JSONB,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255)
);
```

### 4. Running the Application

```bash
# From phase-2-web-app directory
npm run dev:concurrent
```

This will start both the Next.js frontend and FastAPI backend.

## Development Workflow

### Frontend Development
- Chatbot UI components will be in `src/app/chatbot/`
- API calls to chatbot endpoints will be made from frontend
- Chat interface component will be reusable across the app

### Backend Development
- Chatbot API endpoints will be in `src/backend/api/v1/chatbot/`
- AI processing service will be in `src/backend/services/ai_service.py`
- Natural language processing utilities will be in `src/backend/lib/ai_utils.py`

## API Endpoints

### Chat Processing
- `POST /api/v1/chatbot/process` - Process natural language commands

### Chat History
- `GET /api/v1/chatbot/history` - Get user's chat history

## Testing

```bash
# Frontend tests
npm run test

# Backend tests
cd src/backend
pytest
```

## Key Components

### Frontend
- `ChatInterface` component - Reusable chat UI component
- `/chatbot` page - Dedicated chatbot interface
- Service layer to communicate with backend API

### Backend
- AI service for natural language processing
- Chatbot API routes
- Integration with existing todo services
- Authentication middleware to ensure user isolation