# AI-Powered Todo Chatbot - Phase III

This project extends the existing todo application with an AI-powered chatbot interface that allows users to manage their todos using natural language commands.

## Features

- Natural language processing for todo creation, modification, and querying
- Integration with existing authentication system
- Real-time chat interface
- AI-powered intent detection and entity extraction

## Tech Stack

- Next.js 14.1 (Frontend)
- FastAPI 0.104.1 (Backend)
- OpenAI API (AI Processing)
- PostgreSQL (Database)
- TypeScript/Python

## Setup

1. Install dependencies:
   ```bash
   npm install
   cd src/backend && pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to the .env file
   ```

3. Run the application:
   ```bash
   npm run dev:concurrent
   ```

## Architecture

- Frontend: Next.js app with chatbot interface at `/chatbot`
- Backend: FastAPI with AI processing services
- Database: PostgreSQL with existing todos table and new chat_messages table
- AI: OpenAI API for natural language processing