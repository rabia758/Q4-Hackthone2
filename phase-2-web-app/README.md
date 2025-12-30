# Phase 2: Full-Stack Web Todo Application

This is the implementation of the Phase 2 application: a full-stack web todo application with authentication, following the specifications.

## Features

- Next.js frontend with App Router
- FastAPI backend with SQLModel ORM
- User authentication (signup/signin)
- Todo management (CRUD operations)
- Responsive UI with modern minimalist design
- Neon PostgreSQL database integration

## Tech Stack

- **Frontend**: Next.js 14+, TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: JWT-based (Better Auth)

## Installation

### Single Command Setup (Recommended)

1. Install all dependencies for both frontend and backend:
```bash
npm run setup
```

2. Run both servers concurrently:
```bash
npm run dev:concurrent
```

This will start both the Next.js frontend server and the FastAPI backend server simultaneously.

### Individual Setup

#### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
# Copy the example environment file
cp .env.local.example .env.local
```

3. Run the development server:
```bash
npm run dev
```

#### Backend Setup

1. Install Python dependencies:
```bash
cd src/backend
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file with database connection
cp .env.example .env
```

3. Run the backend server:
```bash
npm run backend
```

## Styling

- **CSS Framework**: Tailwind CSS
- **Configuration**: Automatically processes CSS through PostCSS with tailwindcss and autoprefixer plugins
- **Build Commands**:
  - `npm run tailwind:build` - Build and minify Tailwind CSS
  - `npm run tailwind:watch` - Watch and rebuild Tailwind CSS during development
- **Note**: Turbopack disabled to ensure Tailwind CSS compatibility with Next.js

## API Endpoints

### Authentication
- `POST /auth/signup` - Create a new user
- `POST /auth/signin` - Authenticate user

### Todo Management
- `GET /todos` - Get all todos for authenticated user
- `POST /todos` - Create a new todo
- `GET /todos/{id}` - Get a specific todo
- `PUT /todos/{id}` - Update a todo
- `DELETE /todos/{id}` - Delete a todo

### AI Chatbot
- `POST /chatbot/process` - Process natural language commands for todo management
- `GET /chatbot/history` - Get chat history for the authenticated user

## Project Structure

```
phase-2-web-app/
├── src/
│   ├── app/                 # Next.js App Router pages
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Main dashboard page
│   │   ├── chatbot/         # AI chatbot interface
│   │   │   └── page.tsx     # Chatbot page
│   │   ├── globals.css      # Global styles
│   │   └── api/             # API routes
│   ├── components/          # React components
│   │   └── chatbot/         # Chatbot components
│   │       └── ChatInterface.tsx  # Chat interface component
│   ├── lib/                 # Utility functions
│   └── backend/             # FastAPI application
│       ├── main.py          # FastAPI application with AI endpoints
│       ├── models.py        # Data models (todos and chat messages)
│       ├── auth.py          # Authentication logic
│       ├── lib/             # AI utilities and services
│       │   ├── ai_service.py    # AI service for processing commands
│       │   └── ai_utils.py      # AI utilities for intent detection
│       ├── services/        # Backend services
│       │   ├── todo_service.py  # Todo management service
│       │   └── chat_service.py  # Chat message service
│       └── requirements.txt # Python dependencies (including AI dependencies)
├── public/                  # Static assets
├── package.json             # Frontend dependencies (including AI dependencies)
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Development

To run the full application:

1. Start the backend: `cd src/backend && uvicorn main:app --reload`
2. In another terminal, start the frontend: `npm run dev`
3. Visit `http://localhost:3000` in your browser

## Environment Variables

- `NEXT_PUBLIC_API_URL`: URL of the backend API (default: http://localhost:8000)
- `DATABASE_URL`: PostgreSQL connection string for the backend
- `AUTH_SECRET`: Secret key for JWT tokens