# Technical Test - Backend Developer Python (FastAPI)

Functional, secure, and maintainable REST API for managing Tasks with JWT Authentication, built with FastAPI, SQLAlchemy (Async), and PostgreSQL.

## Tech Stack
- **Python**: 3.11.8
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.x (Async with asyncpg)
- **Database**: PostgreSQL 15
- **Authentication**: JWT (python-jose) + bcrypt
- **Migrations**: Alembic

## Features
- **Authentication**: JWT-based login (`POST /api/v1/auth/login`).
- **Tasks CRUD**: Create, Read, Update, Delete tasks (`/api/v1/tasks`).
- **Pagination**: Efficient pagination for task listing.
- **Soft Delete**: Tasks are not permanently deleted, allowing data recovery.
- **Timestamps**: Automatic `created_at` and `updated_at` tracking on all entities.
- **Dockerized**: Fully containerized setup (App + DB).
- **Auto-Migrations**: Database tables and seed data created automatically on startup.
- **Error Handling**: RFC 7807 Problem Details format for all errors.

## Architecture

```
app/
├── api/              # API routes and controllers
│   └── v1/
│       ├── controllers/  # Request handlers
│       └── routes/       # Route definitions
├── core/             # Configuration, security, middleware
├── db/               # Database session, migrations (Alembic)
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── services/         # Business logic
└── main.py           # Application entry point
```

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| email | String | Unique, indexed |
| hashed_password | String | bcrypt hash |
| is_active | Boolean | Account status |
| created_at | DateTime | Auto-set on creation |
| updated_at | DateTime | Auto-updated on changes |
| is_deleted | Boolean | Soft delete flag (indexed) |
| deleted_at | DateTime | Soft delete timestamp |

### Tasks Table
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | String | Required, indexed |
| description | Text | Optional |
| status | String | `pending`, `in_progress`, `done` (indexed) |
| owner_id | Integer | Foreign key to users |
| created_at | DateTime | Auto-set on creation (indexed) |
| updated_at | DateTime | Auto-updated on changes |
| is_deleted | Boolean | Soft delete flag (indexed) |
| deleted_at | DateTime | Soft delete timestamp |

### Index Strategy
- **`ix_tasks_title`**: Fast search by task title.
- **`ix_tasks_status`**: Filter tasks by status efficiently.
- **`ix_tasks_created_at`**: Order by creation date (default sorting).
- **`ix_tasks_is_deleted`**: Quick filtering of active vs deleted tasks.
- **`ix_users_email`**: Unique constraint + fast login lookup.

## Prerequisites
- Docker & Docker Compose

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | postgres | Database user |
| `POSTGRES_PASSWORD` | postgres | Database password |
| `POSTGRES_DB` | technical_test | Database name |
| `POSTGRES_SERVER` | localhost | Database host |
| `POSTGRES_PORT` | 5432 | Database port |
| `SECRET_KEY` | (set in .env) | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |

## Quick Start (Docker)

The easiest way to run the application is with Docker Compose. This runs both the database and the FastAPI application.

1. **Build and Start**
   ```bash
   cp .env.example .env
   docker compose -f compose.dev.yml up --build
   ```
   *The application will automatically run migrations and seed the initial user.*

2. **Access API**
   - Swagger Documentation: http://localhost:8000/docs
   - API Root: http://localhost:8000/api/v1

## Local Development (Without Docker for App)

If you prefer to run the app locally while keeping the DB in Docker:

1. **Start Database**
   ```bash
   cp .env.example .env
   docker-compose -f compose.dev.yml up -d db
   ```

2. **Setup Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start Application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Initial User
The initial user is created automatically via Alembic migration (`220c960a97d9_seed_initial_user.py`).

- **Email**: `admin@example.com`
- **Password**: `changeme`

## API Usage (cURL Examples)

### 1. Login (Get Token)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@gmail.com",
    "password": "test1234"
  }'
```

**Response:**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "meta": { "request_id": "..." }
}
```

> **Note**: Replace `<TOKEN>` in the following commands with the `access_token` from the login response.

---

### 2. Create Task
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Task",
    "description": "This is a test task"
  }'
```

---

### 3. List Tasks (Paginated)
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/?page=1&size=10" \
  -H "Authorization: Bearer <TOKEN>"
```

---

### 4. Get Single Task
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <TOKEN>"
```

---

### 5. Update Task
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Task Title",
    "status": "in_progress"
  }'
```

**Available status values:** `pending`, `in_progress`, `done`

---

### 6. Delete Task (Soft Delete)
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1" \
  -H "Authorization: Bearer <TOKEN>"
```

**Response:** `204 No Content`

> **Note**: Tasks are soft-deleted (marked as `is_deleted=true`) and will not appear in listings.

---

## Technical Decisions & Trade-offs

1. **Soft Delete**: Implemented soft delete instead of hard delete to preserve data integrity and allow recovery. Trade-off: slightly more complex queries.

2. **Base Class Timestamps**: `created_at`, `updated_at`, `is_deleted`, and `deleted_at` are defined in the base class so all models inherit them automatically.

3. **Async SQLAlchemy**: Used async database operations for better performance under load.

4. **RFC 7807 Error Format**: All errors follow the Problem Details standard for consistent API responses.

5. **JWT in Header**: Token is passed via `Authorization: Bearer <token>` header (industry standard).

6. **Pagination**: Uses `page` and `size` parameters with sensible defaults (page=1, size=10).

## HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET/PUT |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE |
| 400 | Bad request |
| 401 | Unauthorized (invalid/missing token) |
| 404 | Resource not found |
| 422 | Validation error |
