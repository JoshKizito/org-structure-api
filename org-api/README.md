# Org Structure API

A production-ready REST API for managing **organisational departments and employees**.  
Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2.0** and **Alembic**.

---

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Runtime | Python 3.12 |
| Container | Docker + docker-compose |
| Tests | pytest + pytest-asyncio + httpx |

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/org-api.git
cd org-api

# 2. Copy environment variables
cp .env.example .env

# 3. Build and start everything
docker-compose up --build
```

The API is available at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

## Running Tests

Tests use an in-memory SQLite database – no Docker required.

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v
```

---

## Migrations

```bash
# Apply all pending migrations (runs automatically on container start)
docker-compose exec api alembic upgrade head

# Create a new migration
docker-compose exec api alembic revision --autogenerate -m "describe your change"

# Rollback one step
docker-compose exec api alembic downgrade -1
```

---

## API Endpoints

### Health

```
GET  /health                                  Health check
```

### Departments

```
POST   /api/v1/departments/                   Create department
GET    /api/v1/departments/{id}               Get department tree
PATCH  /api/v1/departments/{id}               Update department
DELETE /api/v1/departments/{id}               Delete department
```

### Employees

```
POST   /api/v1/departments/{id}/employees/    Create employee in department
```

---

## Example Requests

### Create a root department

```bash
curl -X POST http://localhost:8000/api/v1/departments/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Engineering"}'
```

### Create a child department

```bash
curl -X POST http://localhost:8000/api/v1/departments/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Backend", "parent_id": 1}'
```

### Create an employee

```bash
curl -X POST http://localhost:8000/api/v1/departments/2/employees/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "position": "Senior Developer",
    "hired_at": "2023-06-01"
  }'
```

### Get department tree (depth 3, with employees)

```bash
curl "http://localhost:8000/api/v1/departments/1?depth=3&include_employees=true"
```

### Update department name

```bash
curl -X PATCH http://localhost:8000/api/v1/departments/2 \
  -H "Content-Type: application/json" \
  -d '{"name": "Platform Engineering"}'
```

### Delete with cascade

```bash
curl -X DELETE "http://localhost:8000/api/v1/departments/2?mode=cascade"
```

### Delete and reassign employees

```bash
curl -X DELETE \
  "http://localhost:8000/api/v1/departments/2?mode=reassign&reassign_to_department_id=3"
```

---

## Architecture

```
app/
├── api/
│   ├── routes/
│   │   └── departments.py      # HTTP handlers
│   └── dependencies/
│       └── services.py         # FastAPI DI wiring
├── core/
│   ├── config.py               # Settings (pydantic-settings)
│   └── database.py             # Async engine + session
├── models/
│   ├── base.py                 # DeclarativeBase
│   ├── department.py           # Department ORM model
│   └── employee.py             # Employee ORM model
├── schemas/
│   ├── department.py           # Pydantic request/response schemas
│   └── employee.py
├── services/
│   ├── department_service.py   # Business logic
│   └── employee_service.py
├── repositories/
│   ├── department_repository.py # DB access layer
│   └── employee_repository.py
└── main.py                     # FastAPI app factory
alembic/
├── env.py
└── versions/
    └── 0001_initial.py
tests/
├── conftest.py
└── test_departments.py
```

---

## Business Rules

- Department **name** is trimmed and must be 1–200 characters.
- Department names must be **unique within the same parent**.
- A department **cannot be its own parent**.
- Setting a parent that is a **descendant** of the department is rejected with `409 Conflict`.
- `DELETE ?mode=cascade` removes the department, all descendants, and all their employees.
- `DELETE ?mode=reassign` moves employees from the entire subtree to a target department before deleting.
- Tree queries accept `depth` (1–5) and optionally embed `employees` sorted by `full_name`.
