# Copilot Instructions for auto-qm-form

## Project Overview

**AutoQM** is a FastAPI-based quality management system that auto-generates forms, budgets, and specifications from document inputs (PDF, DOCX, Excel, CSV). The backend runs on the host machine with PostgreSQL in Docker.

### Architecture Layers
- **API Layer** (`src/api/routes/`): Router-based endpoints (budget, specs, reference, form, ui)
- **Data Layer** (`src/models.py`, `src/schemas.py`): SQLAlchemy ORM models + Pydantic schemas
- **Service Layer** (`src/services/`): Business logic for ingestion and parsing (LLM integration stubs)
- **DB Layer** (`src/db.py`): Engine/session management with naming conventions for Alembic

## Essential Setup & Workflow

### Database Configuration
- **Primary**: PostgreSQL via Docker (`docker-compose.yml`)
- **Development**: SQLite fallback via `.env` (`DATABASE_URL=sqlite:///./local.db`)
- **Testing**: Separate test database (`TEST_DATABASE_URL`) with auto-migration via Alembic
- **Resolution order** (`src/db.py`): explicit > TEST_DATABASE_URL (if prefer_test=True) > DATABASE_URL > config.py settings

### Key Commands
```bash
# Start PostgreSQL Docker container
docker compose up -d

# Database migrations (auto-detected from models.py)
alembic revision --autogenerate -m "migration_name"
alembic upgrade head

# Run tests (uses test.sqlite by default, migrates automatically)
make test  # or ./scripts/test_with_migrate.sh

# Lint & format
make lint
make format

# Run app locally
uvicorn src.main:app --reload --port 8000
# Then visit http://127.0.0.1:8000/docs for Swagger UI
```

## Code Patterns & Conventions

### ORM & Naming Convention
- All models inherit from `Base` (defined in `src/db.py`) which includes `NAMING_CONVENTION` for stable Alembic diffs
- Use **SQLAlchemy 2.0 annotated types**:
  ```python
  from sqlalchemy.orm import Mapped, mapped_column
  item_id: Mapped[int] = mapped_column(primary_key=True)
  metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON)
  ```
- Column name in database differs from attribute (e.g., `metadata_json` attr → `"metadata"` col)

### Request/Response Patterns
- **Create schemas**: `XxxCreate` (input, no IDs, optional metadata)
- **Read schemas**: `XxxRead` (output, includes IDs, with `Config.orm_mode = True`)
- Example from `src/schemas.py`:
  ```python
  class BudgetItemCreate(BaseModel):
      budget_id: str
      name: str
      type: str
      # ...
      metadata: Optional[dict] = None

  class BudgetItemRead(BudgetItemCreate):
      item_id: int
      class Config:
          orm_mode = True
  ```

### API Router Pattern
- Routes modularized in `src/api/routes/` (budget.py, specs.py, reference.py, form.py, ui.py, budget_complex.py)
- Mounted in `src/main.py` with prefix (e.g., `app.include_router(budget.router, prefix="/budget", tags=["budget"])`)
- Use `Depends(get_db)` for session injection:
  ```python
  @router.post("/import")
  async def import_specs(spec_id: str = Form(...), file: UploadFile = None, db: Session = Depends(get_db)):
      return ingestion.import_technical_specs(db, ...)
  ```

### Configuration Management
- `src/config.py` uses **Pydantic Settings** with app environment resolution:
  - `APP_ENV=dev/test/prod` → loads `.env` or `.env.test`
  - Use `get_settings()` (cached) or `_compute_settings(override_db_url=...)` for tests
  - Property `effective_database_url` prioritizes TEST_DATABASE_URL if APP_ENV="test"

### CRUD Operations
- Generic pattern in `src/crud.py`:
  ```python
  def create_xxx(db: Session, data: schemas.XxxCreate):
      obj = models.Xxx(**data.model_dump())
      db.add(obj)
      db.commit()
      db.refresh(obj)
      return obj
  ```

## Testing Strategy

- **Test Database**: Auto-created via `conftest.py` migrations on session scope
- **Test Session**: Per-test rollback to isolate state (see `tests/conftest.py`)
- **Pytest Config**: `pythonpath = .` in `pytest.ini` allows `from src import ...`
- **Test Location**: `tests/test_*.py` files; run with `pytest` or `make test`

## External Integrations & Future Extensions

### File Upload & Parsing
- Routes accept **UploadFile** (PDF, DOCX, Excel, CSV) → format auto-detection
- Service layer (`src/services/ingestion`) parses files and stores raw content
- **LLM stub** (`LLM_PROVIDER=stub` in config) for future Claude/GPT integration

### Reference Data Seed
- `scripts/seed_quality_standards.py` populates `quality_standards` table
- Used for specification templates and acceptance criteria

### Git Integration
- `scripts/refresh_git_env.sh` generates `.env.git` with branch/commit info
- Useful for audit trails and deployment tracking

## Critical Patterns to Preserve

1. **Lazy Engine Init**: `src/db.py` uses lazy singleton for SQLAlchemy engine to allow test database switching
2. **Session Management**: Always call `dispose_engine_on_shutdown()` on app shutdown (in `src/main.py`)
3. **Health Checks**: Startup test connection; Alembic auto-upgrade before migrations
4. **Async File Handling**: Use `async def` for file upload routes; `await file.read()` for content
5. **JSON Columns**: Use SQLAlchemy `JSON` type; Pydantic handles serialization

## File Structure Quick Reference

```
src/
├── main.py              # FastAPI app, routers, startup/shutdown hooks
├── db.py                # Engine/session, naming convention, database URL resolution
├── config.py            # Pydantic Settings with APP_ENV-based .env loading
├── models.py            # SQLAlchemy ORM models (BudgetItem, SpecificationItem, etc.)
├── schemas.py           # Pydantic schemas (Create/Read pairs)
├── crud.py              # Generic CRUD helpers
├── api/routes/          # Router modules (budget.py, specs.py, etc.)
├── services/            # Business logic (ingestion, parsing, LLM stubs)
├── core/                # Shared utilities
migrations/              # Alembic versioned migrations
tests/                   # Unit/integration tests with conftest.py
scripts/                 # Utility scripts (init_test_db.py, seed_quality_standards.py)
```

## Dos and Don'ts

✅ **DO:**
- Always use `Mapped[]` with `mapped_column()` for new ORM fields
- Call `get_settings()` at module level for app config (cached singleton)
- Use Alembic for schema changes: `make revision`, verify output, then `make migrate`
- Test with `make test` which auto-migrates test database

❌ **DON'T:**
- Manually call `create_all()` if migrations exist; rely on Alembic
- Assume database URLs; always check .env or TEST_DATABASE_URL first
- Skip `db.refresh(obj)` after commit in CRUD—needed for auto-incremented IDs
- Use `orm_mode = True` in Create schemas; only in Read schemas

