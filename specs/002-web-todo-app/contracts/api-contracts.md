# API Contracts: Phase II — Full-Stack Web Todo Application

---

## 1. Overview

This document defines the API contracts for the Full-Stack Web Todo Application, including request/response formats, authentication, and error handling.

---

## 2. Base URL and Versioning

### Base URL
- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

### Versioning
- API version is included in the URL path
- Current version: `v1`
- Example: `https://api.yourdomain.com/v1/todos`

---

## 3. Authentication

### JWT Token Authentication
All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

### Token Format
- Algorithm: HS256
- Expiration: 30 minutes
- Claims: `sub` (email), `exp` (expiration), `iat` (issued at)

---

## 4. Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

---

## 5. Authentication Endpoints

### 5.1 POST /auth/signup

#### Description
Register a new user account

#### Request
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Request Validation
- `email`: Required, valid email format, max 255 chars
- `password`: Required, min 8 chars

#### Successful Response (201 Created)
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "created_at": "2023-12-25T10:30:00Z"
    }
  },
  "message": "User registered successfully"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input data
- `409 Conflict`: Email already exists

---

### 5.2 POST /auth/signin

#### Description
Authenticate user and return access token

#### Request
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Request Validation
- `email`: Required, valid email format
- `password`: Required

#### Successful Response (200 OK)
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {
      "id": "uuid-string",
      "email": "user@example.com"
    }
  },
  "message": "Authentication successful"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid credentials

---

### 5.3 GET /auth/me

#### Description
Get current authenticated user information

#### Headers Required
```
Authorization: Bearer <jwt_token>
```

#### Successful Response (200 OK)
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "email": "user@example.com",
    "created_at": "2023-12-25T10:30:00Z"
  },
  "message": "User information retrieved"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token

---

## 6. Todo Management Endpoints

### 6.1 GET /todos

#### Description
Get all todos for the authenticated user

#### Headers Required
```
Authorization: Bearer <jwt_token>
```

#### Query Parameters
- `completed` (optional): Filter by completion status (`true`/`false`)
- `limit` (optional): Number of results to return (default: 50, max: 100)
- `offset` (optional): Number of results to skip (for pagination)

#### Successful Response (200 OK)
```json
{
  "success": true,
  "data": {
    "todos": [
      {
        "id": "uuid-string",
        "user_id": "user-uuid-string",
        "title": "Complete project",
        "description": "Finish the todo application",
        "completed": false,
        "created_at": "2023-12-25T10:30:00Z",
        "updated_at": "2023-12-25T10:30:00Z"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  },
  "message": "Todos retrieved successfully"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token

---

### 6.2 POST /todos

#### Description
Create a new todo for the authenticated user

#### Headers Required
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "title": "New todo item",
  "description": "Description of the todo (optional)"
}
```

#### Request Validation
- `title`: Required, 1-255 characters
- `description`: Optional, max 1000 characters

#### Successful Response (201 Created)
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "user_id": "user-uuid-string",
    "title": "New todo item",
    "description": "Description of the todo (optional)",
    "completed": false,
    "created_at": "2023-12-25T10:30:00Z",
    "updated_at": "2023-12-25T10:30:00Z"
  },
  "message": "Todo created successfully"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid or expired token

---

### 6.3 GET /todos/{id}

#### Description
Get a specific todo by ID

#### Path Parameters
- `id`: Todo UUID (required)

#### Headers Required
```
Authorization: Bearer <jwt_token>
```

#### Successful Response (200 OK)
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "user_id": "user-uuid-string",
    "title": "Todo title",
    "description": "Todo description",
    "completed": false,
    "created_at": "2023-12-25T10:30:00Z",
    "updated_at": "2023-12-25T10:30:00Z"
  },
  "message": "Todo retrieved successfully"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User doesn't own this todo
- `404 Not Found`: Todo doesn't exist

---

### 6.4 PUT /todos/{id}

#### Description
Update a specific todo by ID

#### Path Parameters
- `id`: Todo UUID (required)

#### Headers Required
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "title": "Updated todo title (optional)",
  "description": "Updated description (optional)",
  "completed": true
}
```

#### Request Validation
- `title`: Optional, 1-255 characters if provided
- `description`: Optional, max 1000 characters if provided
- `completed`: Optional, boolean if provided

#### Successful Response (200 OK)
```json
{
  "success": true,
  "data": {
    "id": "uuid-string",
    "user_id": "user-uuid-string",
    "title": "Updated todo title",
    "description": "Updated description",
    "completed": true,
    "created_at": "2023-12-25T10:30:00Z",
    "updated_at": "2023-12-25T11:45:00Z"
  },
  "message": "Todo updated successfully"
}
```

#### Error Responses
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User doesn't own this todo
- `404 Not Found`: Todo doesn't exist

---

### 6.5 DELETE /todos/{id}

#### Description
Delete a specific todo by ID

#### Path Parameters
- `id`: Todo UUID (required)

#### Headers Required
```
Authorization: Bearer <jwt_token>
```

#### Successful Response (200 OK)
```json
{
  "success": true,
  "data": null,
  "message": "Todo deleted successfully"
}
```

#### Error Responses
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User doesn't own this todo
- `404 Not Found`: Todo doesn't exist

---

## 7. Error Codes

### Common Error Codes
- `AUTH_001`: Invalid credentials
- `AUTH_002`: Token expired
- `AUTH_003`: Invalid token
- `AUTH_004`: Email already exists
- `VALIDATION_001`: Invalid input data
- `PERMISSION_001`: Insufficient permissions
- `RESOURCE_001`: Resource not found
- `SERVER_001`: Internal server error

---

## 8. HTTP Status Codes

### Success Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `204 No Content`: Request successful, no content to return

### Client Error Codes
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate email)

### Server Error Codes
- `500 Internal Server Error`: Server error

---

## 9. Rate Limiting

### Limits
- Authentication endpoints: 10 requests per minute per IP
- All other endpoints: 100 requests per minute per user

### Headers
Rate limiting information is provided in response headers:
- `X-RateLimit-Limit`: Maximum requests in the time period
- `X-RateLimit-Remaining`: Remaining requests in the time period
- `X-RateLimit-Reset`: Time when the rate limit resets

---

## 10. Pagination

### Standard Pagination Response
```json
{
  "data": {
    "items": [...],
    "total": 100,
    "limit": 10,
    "offset": 0,
    "has_more": true
  }
}
```

### Query Parameters
- `limit`: Number of items per page (default: 10, max: 100)
- `offset`: Number of items to skip
- `page`: Page number (alternative to offset)