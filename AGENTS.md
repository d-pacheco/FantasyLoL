## Agent skills

### Issue tracker
GitHub Issues on `d-pacheco/FantasyLoL`. See `docs/agents/issue-tracker.md`.

### Triage labels
Default vocabulary with `wontfix` mapped to existing label. See `docs/agents/triage-labels.md`.

### Domain docs
Single-context layout. See `docs/agents/domain.md`.

---

## Architecture overview

MythicForge is a Fantasy League of Legends platform. Read `docs/architecture.md` for the full picture. Key facts:

- **One unified API** (`src/app.py`, port 8002) serves both Riot data and Fantasy endpoints. There are no separate microservices for these — the old `src/riot/__init__.py` and `src/fantasy/__init__.py` apps are deprecated stubs kept for test compatibility.
- **Riot Scraper** (`src/riot_scraper/app.py`, port 8004) runs independently with `MASTER_SCRAPER=true`. Uses APScheduler for cron jobs.
- **UI** (`ui/`) is a Vue 3 + TypeScript SPA served by nginx on port 8000, which proxies `/api/*` to the API.
- **PostgreSQL 16** with Alembic migrations. A `db-migrate` init container runs migrations before app services start in Docker.

## Coding conventions

### Python backend

- **Endpoint pattern:** Use `classy_fastapi.Routable` classes. Each endpoint class takes a service in its constructor and delegates all logic to it.
- **Service layer:** Business logic lives in `src/{domain}/service/`. Services accept a `DatabaseService` instance.
- **DAO layer:** Database operations are pure functions in `src/db/riot_dao/` and `src/db/fantasy_dao/`. They accept a SQLAlchemy session and Pydantic schemas.
- **DatabaseService:** Facade that wraps all DAO calls with session management via `DatabaseConnectionProvider.get_db()` context manager.
- **Schemas:** Pydantic models in `src/common/schemas/`. Riot and Fantasy schemas are separate files. Use `NewType` for ID types (e.g., `RiotGameID`, `FantasyLeagueID`).
- **Enums in SQLAlchemy:** Use the custom `ValueEnum` TypeDecorator (stores enum `.value` as a string, reads back via `EnumClass(value)`).
- **Config:** `pydantic-settings` in `src/common/config.py`. All config comes from env vars / `.env` file.
- **Logging:** Use `logging.getLogger("service_name.module")`. The logger is configured per-service in `configure_logger()`.
- **Line length:** 100 characters (ruff config).
- **Imports:** Absolute imports from `src.*`. No relative imports.

### Frontend (Vue/TypeScript)

- `<script setup lang="ts">` exclusively. No Options API.
- Single Axios instance at `ui/src/api/client.ts` with relative baseURL `/api/v1`.
- PrimeVue components + Tailwind CSS for styling. No `<style>` blocks unless necessary.
- Pinia stores handle API calls. Components never call axios directly.
- See `docs/UI_AGENT_INSTRUCTIONS.md` for detailed UI conventions (note: some listed tools like VeeValidate, Vitest, ESLint are aspirational and not yet installed).

## Testing patterns

### Running tests

```bash
pytest                    # or ./scripts/run_tests.sh
```

Requires a `fantasy_lol_test` PostgreSQL database on localhost:5432 (or set `TEST_DATABASE_URL`).

### Key patterns

- Tests use `create_all`/`drop_all` directly — **not** Alembic.
- Session-scoped `db_provider` fixture creates tables + views once per test run.
- Autouse `setup_and_teardown_tables` fixture truncates all table data between tests.
- **Endpoint tests:** Use the `create_endpoint_client` fixture which creates a `TestClient` with auth bypassed and a mocked service.
- **Integration tests:** Use the `db` fixture (real `DatabaseService` against the test database).
- **Scraper tests:** Mock `RiotApiClient` and `JobRunner` to avoid real API calls.
- **Legacy tests:** Some older tests use `unittest.TestCase` inheriting from `TestBase` in `tests/test_base.py`. New tests should use pytest fixtures from `conftest.py`.

### Coverage

Minimum 50% enforced via `--cov-fail-under=50`. Coverage report shows missing lines in terminal output.

## Linting

```bash
./scripts/linter.sh       # Full check: ruff lint + format + mypy
./scripts/linter.sh --format  # Auto-fix formatting
```

- **ruff** for linting and formatting (line-length 100, ignore E402)
- **mypy** with SQLAlchemy plugin for type checking (`src/` and `tests/`)

## Migrations

```bash
./scripts/migrate.sh upgrade              # Apply pending
./scripts/migrate.sh generate "message"   # Autogenerate new migration
./scripts/migrate.sh downgrade -1         # Roll back one
```

Migration files: `alembic/versions/` with numeric prefixes (001, 002, ...).

## Key files to read first

When orienting in this codebase:

1. `src/app.py` — Entry point, shows all endpoints and how services are wired
2. `src/common/config.py` — All configuration and schedule definitions
3. `src/db/models.py` — Full database schema
4. `src/db/database_service.py` — All available database operations
5. `CONTEXT.md` — Domain glossary (Game Analysis, Multi-kill, frames_status)
6. `docs/architecture.md` — Runtime topology and service interactions
