# Plan: Phase II — Full-Stack Web Todo Application

---

## 1. Architecture Overview

### System Context
```
[User] --> (Web Todo App) --> [PostgreSQL Database]
                |
                v
        (Authentication Service)
```

### Container Diagram
- **Frontend Container**: Next.js application
- **Backend Container**: FastAPI application
- **Database Container**: PostgreSQL database

---

## 2. Technology Decisions

### Frontend Framework Choice: Next.js
**Rationale**:
- React-based framework with App Router
- Built-in optimization features
- Server-side rendering capabilities
- Strong TypeScript support
- Large ecosystem

**Trade-offs**:
- ✅ Rich ecosystem and documentation
- ✅ Built-in routing and optimization
- ✅ Server-side rendering support
- ❌ Learning curve for new developers

### Backend Framework Choice: FastAPI
**Rationale**:
- High performance ASGI framework
- Built-in async support
- Automatic API documentation
- Strong typing with Pydantic
- Easy integration with SQLModel

**Trade-offs**:
- ✅ High performance
- ✅ Automatic OpenAPI/Swagger docs
- ✅ Strong typing support
- ❌ Smaller ecosystem than Django

### Database Choice: Neon PostgreSQL
**Rationale**:
- Serverless PostgreSQL
- Branching capabilities
- Strong SQL compliance
- Good performance
- Easy scaling

**Trade-offs**:
- ✅ Serverless scaling
- ✅ Branch/clone features
- ✅ Standard SQL support
- ❌ Potential cold start latency

### ORM Choice: SQLModel
**Rationale**:
- Combines SQLAlchemy and Pydantic
- Type safety
- Async support
- Maintained by FastAPI creator

**Trade-offs**:
- ✅ Type safety with Pydantic
- ✅ SQLAlchemy compatibility
- ✅ Async session support
- ❌ Relatively new technology

---

## 3. Data Architecture

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes
- `users.email`: Unique index for authentication
- `todos.user_id`: Index for user filtering
- `todos.created_at`: Index for chronological sorting

---

## 4. API Design

### Authentication Endpoints
```
POST /auth/signup
POST /auth/signin
GET /auth/me
```

### Todo Endpoints
```
GET /todos          # Get user's todos
POST /todos         # Create new todo
GET /todos/{id}     # Get specific todo
PUT /todos/{id}     # Update todo
DELETE /todos/{id}  # Delete todo
```

### Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

---

## 5. Frontend Architecture

### Component Structure
```
src/
├── components/
│   ├── Auth/
│   │   ├── SignupForm.tsx
│   │   └── SigninForm.tsx
│   ├── Todo/
│   │   ├── TodoList.tsx
│   │   ├── TodoItem.tsx
│   │   └── TodoForm.tsx
│   └── Layout/
│       ├── Header.tsx
│       └── Footer.tsx
├── pages/
│   ├── index.tsx
│   ├── auth/
│   │   ├── signup.tsx
│   │   └── signin.tsx
│   └── dashboard/
│       └── index.tsx
└── hooks/
    ├── useAuth.ts
    └── useTodos.ts
```

### State Management
- React hooks for local state
- Context API for global state
- SWR for server state caching

---

## 6. Security Architecture

### Authentication Flow
1. User submits credentials
2. Server validates and creates JWT
3. Client stores token in memory/storage
4. Subsequent requests include Authorization header
5. Server validates token on each request

### Password Security
- PBKDF2 with salt for password hashing
- Minimum 100,000 iterations
- 128-bit salt generation

### API Security
- JWT token validation
- User ownership verification
- Input validation and sanitization
- Rate limiting (future)

---

## 7. Implementation Phases

### Phase 1: Backend Foundation
- [ ] Set up FastAPI project
- [ ] Configure database connection
- [ ] Implement user models
- [ ] Create authentication endpoints
- [ ] Implement todo models
- [ ] Create todo endpoints
- [ ] Add authentication middleware

### Phase 2: Frontend Foundation
- [ ] Set up Next.js project
- [ ] Configure Tailwind CSS
- [ ] Create basic layout
- [ ] Implement authentication UI
- [ ] Create todo management UI
- [ ] Connect to backend API

### Phase 3: Integration & Polish
- [ ] Full integration testing
- [ ] UI/UX refinements
- [ ] Error handling
- [ ] Performance optimization
- [ ] Security hardening

---

## 8. Deployment Strategy

### Development
- Frontend: `npm run dev` on port 3000
- Backend: `uvicorn main:app --reload` on port 8000
- Database: Local PostgreSQL or Neon dev instance

### Production
- Frontend: Vercel deployment
- Backend: Containerized deployment
- Database: Neon production instance

---

## 9. Testing Strategy

### Backend Tests
- Unit tests for models
- Integration tests for API endpoints
- Authentication flow tests
- Database transaction tests

### Frontend Tests
- Unit tests for components
- Integration tests for API calls
- End-to-end tests for user flows

---

## 10. Performance Considerations

### Backend
- Async database operations
- Connection pooling
- Proper indexing
- Caching for frequently accessed data

### Frontend
- Code splitting
- Image optimization
- Efficient state updates
- Server-side rendering for critical paths