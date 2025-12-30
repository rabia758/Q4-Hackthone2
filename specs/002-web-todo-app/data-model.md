# Data Model: Phase II — Full-Stack Web Todo Application

---

## 1. Domain Overview

The application manages two primary entities:
- **Users**: Authentication and authorization
- **Todos**: Task management items owned by users

Relationship: One-to-Many (One user can have many todos)

---

## 2. Entity Models

### 2.1 User Entity

#### Logical Model
```
User {
  id: UUID
  email: String (unique, required)
  password_hash: String (required)
  created_at: DateTime (default: now)
}
```

#### Physical Model (PostgreSQL)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Constraints
- `id`: Primary key, UUID, auto-generated
- `email`: Unique constraint, NOT NULL, valid email format
- `password_hash`: NOT NULL, secure hash format
- `created_at`: Auto-timestamp, NOT NULL

#### Indexes
- `users.email`: B-tree index for authentication lookups

---

### 2.2 Todo Entity

#### Logical Model
```
Todo {
  id: UUID
  user_id: UUID (foreign key to User)
  title: String (required)
  description: String (optional)
  completed: Boolean (default: false)
  created_at: DateTime (default: now)
  updated_at: DateTime (default: now, auto-update)
}
```

#### Physical Model (PostgreSQL)
```sql
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Constraints
- `id`: Primary key, UUID, auto-generated
- `user_id`: Foreign key to users, cascading delete
- `title`: NOT NULL, max 255 characters
- `completed`: Boolean, defaults to false
- `created_at`: Auto-timestamp, NOT NULL
- `updated_at`: Auto-timestamp, updates on modification

#### Indexes
- `todos.user_id`: B-tree index for user filtering
- `todos.created_at`: B-tree index for chronological queries

---

## 3. Relationship Model

### 3.1 User-Todo Relationship
```
User (1) ←→ (0..n) Todo
```

- One User can own zero or many Todos
- One Todo belongs to exactly one User
- Delete User → Delete all associated Todos (CASCADE)

### 3.2 Foreign Key Constraints
```sql
ALTER TABLE todos
ADD CONSTRAINT fk_todo_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;
```

---

## 4. API Data Transfer Objects (DTOs)

### 4.1 User DTOs

#### User Registration
```typescript
interface UserRegistration {
  email: string;      // Required, valid email format
  password: string;   // Required, min 8 chars, strong format
}
```

#### User Login
```typescript
interface UserLogin {
  email: string;      // Required, valid email format
  password: string;   // Required
}
```

#### User Response
```typescript
interface UserResponse {
  id: string;         // UUID string
  email: string;      // User's email
  created_at: string; // ISO datetime string
}
```

### 4.2 Todo DTOs

#### Todo Creation
```typescript
interface TodoCreate {
  title: string;        // Required, max 255 chars
  description?: string; // Optional, text field
}
```

#### Todo Update
```typescript
interface TodoUpdate {
  title?: string;         // Optional, max 255 chars
  description?: string;   // Optional, text field
  completed?: boolean;    // Optional, boolean
}
```

#### Todo Response
```typescript
interface TodoResponse {
  id: string;           // UUID string
  user_id: string;      // Owner's UUID
  title: string;        // Todo title
  description?: string; // Optional description
  completed: boolean;   // Completion status
  created_at: string;   // ISO datetime string
  updated_at: string;   // ISO datetime string
}
```

---

## 5. Validation Rules

### 5.1 User Validation
- Email: Must be valid email format, max 255 chars
- Password: Min 8 chars, recommended complexity
- Uniqueness: Email must be unique across users

### 5.2 Todo Validation
- Title: Required, 1-255 characters
- Description: Optional, max 1000 characters
- Ownership: User can only access their own todos
- Completion: Boolean value (true/false)

---

## 6. Security Considerations

### 6.1 Data Protection
- Passwords: Never stored in plain text, always hashed
- User data: Protected by authentication
- Todo data: User isolation enforced

### 6.2 Access Control
- User authentication required for all operations
- Todo access limited to owner user
- API endpoints validate user identity

---

## 7. Performance Considerations

### 7.1 Indexing Strategy
- Primary keys automatically indexed
- Foreign keys indexed for JOIN operations
- Frequently queried fields indexed

### 7.2 Query Optimization
- Use parameterized queries to prevent injection
- Implement proper pagination for large datasets
- Optimize queries with proper indexing

---

## 8. Audit Trail

### 8.1 Timestamp Fields
- `created_at`: Set on record creation
- `updated_at`: Updated on record modification
- Automatic timestamp generation in database

---

## 9. Migration Strategy

### 9.1 Initial Schema Creation
```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create todos table
CREATE TABLE todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_created_at ON todos(created_at);
```

---

## 10. Future Extensions

### 10.1 Potential Additions
- Tags for todos
- Categories for organization
- Sharing capabilities
- Recurring tasks
- Attachments