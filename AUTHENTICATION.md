# Authentication System

This document provides an overview of the authentication system used in the PDV System Backend.

## Overview

The authentication system uses JWT (JSON Web Tokens) for stateless authentication. Users can authenticate using their username and password to receive an access token, which must be included in subsequent requests to protected endpoints.

## Setup

### 1. Environment Variables

Make sure you have the following environment variables set in your `.env` file:

```bash
# Authentication
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/your_database
```

### 2. Database Migrations

Run the database migrations to create the necessary tables:

```bash
alembic upgrade head
```

### 3. Create Admin User

Create an initial admin user using the provided script:

```bash
python -m scripts.create_admin admin yourpassword admin@example.com "Admin User"
```

## Authentication Flow

### 1. Login

To authenticate, send a POST request to `/api/v1/auth/login` with username and password:

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=yourpassword
```

Successful response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin",
    "is_active": true
  }
}
```

### 2. Using the Access Token

Include the access token in the `Authorization` header for protected endpoints:

```http
GET /api/v1/protected-route
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. Get Current User

To get information about the currently authenticated user:

```http
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Protected Endpoints

All endpoints that require authentication should include the `current_user` dependency:

```python
from fastapi import Depends, HTTPException
from app.core.security import get_current_active_user
from app.models.user import User

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user.username}"}
```

## Error Handling

The API returns appropriate HTTP status codes for different error scenarios:

- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User doesn't have permission to access the resource
- `400 Bad Request`: Invalid request data

## Security Notes

- Always use HTTPS in production
- Store the `SECRET_KEY` securely and never commit it to version control
- Set appropriate token expiration times based on your security requirements
- Implement rate limiting to prevent brute force attacks
- Consider implementing refresh tokens for better security
