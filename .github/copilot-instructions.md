# Annuaire Contacts Backend — AI Agent Instructions

## Project Overview

FastAPI REST API for managing contacts with PostgreSQL persistence. Minimal CRUD service with search capabilities.

**Stack**: FastAPI + SQLAlchemy + PostgreSQL 15 + Docker Compose  
**Default port**: 8000  
**Swagger UI**: `http://localhost:8000/docs` (auto-enabled)

---

## Architecture

### Three-File Core Pattern

```
main.py          → FastAPI endpoints (CRUD + search)
database.py      → SQLAlchemy engine, session management
models.py        → ORM models (SQLAlchemy) + API schemas (Pydantic)
```

**Data flow**: Request → Pydantic validation → DB query via SessionLocal → SQLAlchemy model → Pydantic response

### Database Structure

PostgreSQL 15 (via Docker Compose) with single `contacts` table:
```
id (UUID PK) | nom | email (UNIQUE) | telephone | adresse | organisation | tags (JSON) | created_at | updated_at
```

---

## Key Patterns to Follow

### 1. **Dependency Injection for DB Sessions**
```python
# Always use this pattern for DB operations
def handler(db: Session = Depends(get_db)):
    contact = db.query(ContactDB).filter(...).first()
```
- Session cleanup is automatic (try/finally in `get_db()`)
- Never close session manually

### 2. **Pydantic Schemas for Validation**
- `ContactCreate`: POST requests (validates email with `EmailStr`)
- `ContactUpdate`: PUT requests (all fields optional via `Optional[...]`)
- `ContactResponse`: API responses (excludes sensitive fields)
- Use `model_dump(exclude_unset=True)` for partial updates

### 3. **Unique Constraint Handling**
Always query for existing email before create/update:
```python
existing = db.query(ContactDB).filter(ContactDB.email == contact.email).first()
if existing:
    raise HTTPException(status_code=400, detail="Email already used")
```

### 4. **HTTP Status Codes**
- `201`: POST success (use `status_code=status.HTTP_201_CREATED`)
- `204`: DELETE success (response body omitted)
- `400`: Validation/unique constraint failures
- `404`: Resource not found

### 5. **Logging on State Changes**
Log create/update/delete operations:
```python
logger.info(f"Contact created: {db_contact.id}")
```

### 6. **Search with Case-Insensitive Matching**
Use `ilike()` for flexible search across multiple fields:
```python
db.query(ContactDB).filter(
    (ContactDB.nom.ilike(f"%{query}%")) |
    (ContactDB.email.ilike(f"%{query}%"))
).all()
```

---

## Development Workflows

### Starting the Stack
```bash
docker-compose up --build
```
- PostgreSQL initializes on first run (credentials via environment variables)
- Backend auto-connects and creates schema via `init_db()` on startup
- Run with `--reload` flag enables auto-restart on code changes

### Testing Endpoints
- Swagger UI: http://localhost:8000/docs (interactive sandbox)
- Health check: `GET /health` (no DB dependency)
- All endpoints use `response_model=ContactResponse` for schema validation

### Database Migrations
Currently using SQLAlchemy's `metadata.create_all()` (not Alembic).
- Changes to `models.py` → delete DB volume, restart Docker to recreate tables
- For production migrations, consider building Alembic workflows

---

## Configuration & Credentials

### Environment Variables (docker-compose.yml)
```
DATABASE_URL=postgresql+psycopg2://annuaire_user:annuaire_password@postgres:5432/annuaire_contacts
```
- Connection string uses **psycopg2** driver (see `requirements.txt`)
- PostgreSQL health check prevents backend startup until DB is ready

### Local Development (.env)
Copy from `.env.example` and update `DATABASE_URL` for local testing without Docker

---

## Common Modifications

### Adding New Fields to Contact
1. Add column to `ContactDB` in `models.py`
2. Add field to `ContactCreate`, `ContactUpdate`, `ContactResponse` Pydantic models
3. Add to search filter in `search_contacts()` if searchable
4. Restart Docker or manually recreate DB

### Adding New Endpoints
1. Use `@app.get()`, `@app.post()`, `@app.put()`, `@app.delete()` decorators
2. Always include `response_model=ContactResponse` (or list variant)
3. Use `Depends(get_db)` for DB access
4. Validate input with Pydantic (automatic 422 errors for invalid schema)
5. Log important operations

### Error Handling Best Practices
- Use `HTTPException` for all client errors (400/404/409 etc.)
- Never expose internal database errors directly to client
- Include descriptive `detail` message for debugging

---

## Dependencies & Tools

| Package | Role |
|---------|------|
| `fastapi` | Web framework + auto-generated Swagger UI |
| `sqlalchemy` | ORM for database queries |
| `pydantic` | Request/response validation + serialization |
| `psycopg2-binary` | PostgreSQL connection driver |
| `uvicorn` | ASGI server (production-ready) |

See `requirements.txt` for versions and additional dependencies.

---

## Notes for AI Agents

- **No migrations tool**: Direct schema edits via `models.py` + Docker restart
- **No authentication**: All endpoints are public (add auth via middleware if needed)
- **No soft deletes**: Deletes are permanent
- **Swagger auto-enabled**: No setup needed, available at `/docs`
- **Timestamps auto-managed**: Use `func.now()` and `onupdate=func.now()` in model
- **Get session directly**: Use `SessionLocal()` only in special cases; normally inject via `Depends(get_db)`
