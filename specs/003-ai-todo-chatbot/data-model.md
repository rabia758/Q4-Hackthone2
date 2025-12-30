# Data Model: AI-Powered Todo Chatbot

## Entities

### Todo
**Source**: Extended from existing todo model in phase-2-web-app

- `id` (UUID/Integer): Unique identifier for the todo
- `title` (String): The task description
- `completed` (Boolean): Whether the task is completed
- `user_id` (UUID/String): Reference to the owning user (from auth system)
- `created_at` (DateTime): Timestamp when todo was created
- `updated_at` (DateTime): Timestamp when todo was last modified

**Relationships**:
- Belongs to one User (via user_id)
- One User has many Todos

**Validation Rules**:
- Title must not be empty
- user_id must reference an existing authenticated user
- Cannot modify another user's todos

### ChatMessage
**Source**: New model for chatbot interactions

- `id` (UUID/Integer): Unique identifier for the chat message
- `user_id` (UUID/String): Reference to the user who sent the message
- `message` (String): The natural language command or query from user
- `intent` (String): Parsed intent (CREATE, UPDATE, DELETE, QUERY, etc.)
- `entities` (JSON): Extracted entities from the natural language (e.g., todo title, date, etc.)
- `response` (String): AI-generated response or confirmation
- `created_at` (DateTime): Timestamp when message was processed
- `session_id` (String): Reference to the chat session (for conversation context)

**Relationships**:
- Belongs to one User (via user_id)
- One User has many ChatMessages

**Validation Rules**:
- Message must not be empty
- user_id must reference an existing authenticated user
- Intent must be one of the recognized types

### User
**Source**: From existing Better Auth system in phase-2-web-app

- `id` (UUID/String): Unique identifier for the user
- `email` (String): User's email address
- `name` (String): User's name
- `created_at` (DateTime): Account creation timestamp

**Relationships**:
- Has many Todos
- Has many ChatMessages

## State Transitions

### Todo State Transitions
- `incomplete` → `completed` (when marked as done)
- `completed` → `incomplete` (when unmarked)

### ChatMessage States
- `pending` → `processing` → `completed` (during AI processing)

## API Contracts

### Chatbot API Endpoints

#### POST /api/v1/chatbot/process
Process a natural language command from the user
- Request: `{ message: string, user_id: string }`
- Response: `{ success: boolean, intent: string, entities: object, response: string, action_result?: object }`

#### GET /api/v1/chatbot/history
Retrieve chat history for a user
- Request: `{ user_id: string, limit?: number, offset?: number }`
- Response: `{ messages: Array<ChatMessage> }`

## Database Schema Considerations

The existing todo table structure from the web app will be extended to support the chatbot functionality:

```sql
-- Existing todos table (from phase-2-web-app)
CREATE TABLE todos (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New chat_messages table for chatbot interactions
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(50),
    entities JSONB,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(255)
);
```

## Data Flow

1. User sends natural language command through chat interface
2. Frontend sends command to backend API
3. AI service processes command, identifies intent and entities
4. AI service executes corresponding todo operation using existing services
5. Results are returned to frontend and stored in chat history
6. UI is updated to reflect changes to todos