# Development Guide

## Prerequisites

- Python 3.12+
- PostgreSQL 16 (or Docker)
- Node.js 22+ (for UI development)

## Local Setup

### 1. Clone and install

```bash
git clone https://github.com/d-pacheco/FantasyLoL.git
cd FantasyLoL

python -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
```

### 2. Environment

Copy the example env file and adjust as needed:

```bash
cp example.env .env
```

Required variables (no defaults):
- `AUTH_SECRET` — Any random string for JWT signing

Optional but useful:
- `DEBUG_LOGGING=True` — Verbose log output
- `REQUIRE_EMAIL_VERIFICATION=False` — Skip email verification locally

See `example.env` for the full list with descriptions.

### 3. Database

**Option A — Docker (recommended):**

```bash
cd docker-files
docker compose -f docker-compose.dev.yml up -d
```

This starts PostgreSQL on `localhost:5432` with user/pass `postgres/postgres` and database `fantasy_lol`.

**Option B — Local PostgreSQL:**

Create the database manually:

```sql
CREATE DATABASE fantasy_lol;
```

### 4. Run migrations

```bash
./scripts/migrate.sh upgrade
```

This runs `alembic upgrade head` against the `DATABASE_URL` in your `.env`.

### 5. Start the API

```bash
python -m src.app
```

The unified API starts on port 8002. Swagger docs at http://localhost:8002/docs.

### 6. Start the scraper (optional)

```bash
MASTER_SCRAPER=true python -m src.riot_scraper.app
```

Starts on port 8004. Swagger docs at http://localhost:8004/docs.

### 7. Start the UI (optional)

```bash
cd ui
npm install
npm run dev
```

Vite dev server starts on http://localhost:5173. API calls are proxied to port 8002 via the Vite config.

## Running with Docker (full stack)

```bash
./scripts/docker_local.sh
```

Or manually:

```bash
cd docker-files
docker compose -p fantasy_lol -f docker-compose.local.yml up -d --build
```

This starts: PostgreSQL → db-migrate → API (8002) → UI/nginx (8000) → Scraper (8004).

Access the app at http://localhost:8000.

## Migrations

Helper script at `./scripts/migrate.sh`:

```bash
./scripts/migrate.sh upgrade          # Apply all pending migrations
./scripts/migrate.sh upgrade 003      # Upgrade to specific revision
./scripts/migrate.sh downgrade -1     # Roll back one migration
./scripts/migrate.sh current          # Show current revision
./scripts/migrate.sh history          # Show all migrations
./scripts/migrate.sh generate "add foo column"  # Autogenerate new migration
```

Migration files live in `alembic/versions/` with sequential numeric prefixes.

**Important:** After creating a new migration, always test it:
1. `./scripts/migrate.sh downgrade -1`
2. `./scripts/migrate.sh upgrade`
3. Run the test suite

## Testing

### Setup

Tests require a separate test database:

```sql
CREATE DATABASE fantasy_lol_test;
```

Or set `TEST_DATABASE_URL` to point to your test database.

### Running tests

```bash
./scripts/run_tests.sh
```

Or directly:

```bash
pytest
```

Coverage is enforced at 50% minimum (`--cov-fail-under=50`). Coverage report prints to terminal with missing lines.

### Test architecture

- Tests use `create_all`/`drop_all` directly (not Alembic) for speed.
- Database views are created in the session-scoped `db_provider` fixture.
- Each test gets a clean database — the `setup_and_teardown_tables` autouse fixture truncates all tables after each test.
- Two test styles coexist:
  - **pytest fixtures** (`conftest.py`) — newer tests use `db_provider`, `db`, and `create_endpoint_client` fixtures.
  - **unittest.TestCase** (`test_base.py`) — older tests inherit from `TestBase` which manages its own setup/teardown.
- The `create_endpoint_client` fixture creates a `TestClient` with auth bypassed for endpoint testing.
- Scraper tests mock the `RiotApiClient` and `JobRunner` to avoid real API calls.

### Test database URL

Default: `postgresql://postgres:postgres@localhost:5432/fantasy_lol_test`

Override with `TEST_DATABASE_URL` environment variable.

## Linting

```bash
./scripts/linter.sh            # Run all checks (ruff lint + format check + mypy)
./scripts/linter.sh --lint     # Ruff lint only
./scripts/linter.sh --mypy     # mypy only (src + tests)
./scripts/linter.sh --format   # Auto-format with ruff
./scripts/linter.sh --files    # Show diff of what would be reformatted
```

Configuration:
- **ruff** — Line length 100, ignores E402 (import order). Config in `pyproject.toml`.
- **mypy** — Uses the SQLAlchemy plugin. Config in `pyproject.toml`.

## CI/CD

GitHub Actions pipeline (`.github/workflows/pipeline.yml`) runs on all PRs and pushes to main:

1. **Lint** — `ruff format --check`, `ruff check`, `mypy src`, `mypy tests`
2. **Test** — Spins up PostgreSQL 16 service container, runs `pytest`

A separate workflow builds Docker images on push to main.

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `scripts/docker_local.sh` | Build and start the full local Docker stack |
| `scripts/docker_server.sh` | Manage the production Docker stack (up/down/restart) |
| `scripts/migrate.sh` | Alembic migration helper (upgrade/downgrade/generate/history) |
| `scripts/linter.sh` | Run ruff + mypy checks or auto-format |
| `scripts/run_tests.sh` | Run pytest |
| `scripts/find_python.sh` | Locate the correct Python binary (used by other scripts) |

## Project Structure

```
src/
├── app.py                  # Unified FastAPI application (serves both Riot + Fantasy APIs)
├── auth/                   # JWT bearer auth, permissions, principal
├── common/
│   ├── config.py           # Pydantic settings (env vars, schedules)
│   ├── logger.py           # Logging setup (console, file, Loki)
│   ├── middleware.py       # Request logging middleware
│   ├── schemas/            # Pydantic models for Riot data and Fantasy domain
│   └── exceptions/         # Domain exceptions
├── db/
│   ├── models.py           # SQLAlchemy ORM models
│   ├── views.py            # SQL view definitions
│   ├── database_service.py # Facade over all DAO operations
│   ├── database_connection_provider.py  # Engine + session factory
│   ├── riot_dao/           # DAO modules for Riot data tables
│   └── fantasy_dao/        # DAO modules for Fantasy tables
├── fantasy/
│   ├── endpoints/          # Fantasy API route classes (classy_fastapi)
│   ├── service/            # Business logic layer
│   ├── util/               # Fantasy helpers
│   └── exceptions/         # Fantasy-specific exceptions
├── riot/
│   ├── endpoints/          # Riot Data API route classes
│   ├── service/            # Business logic layer
│   └── exceptions/         # Riot-specific exceptions
└── riot_scraper/
    ├── app.py              # Scraper FastAPI app + scheduler setup
    ├── job_scheduler.py    # APScheduler configuration
    ├── job_runner.py       # Retry logic for scraper jobs
    ├── job_runner_endpoint.py  # Manual trigger endpoints
    ├── game_analysis.py    # Frame analysis (multi-kills, dragons, duration)
    ├── timestamp_util.py   # Timestamp parsing utilities
    ├── scrapers/           # Individual scraper classes (one per data type)
    └── riot_api/           # Riot API client + response schemas

ui/                         # Vue 3 + TypeScript + Vite frontend
alembic/                    # Alembic migration config and version files
docker-files/               # Dockerfiles and compose files
scripts/                    # Helper scripts
tests/                      # Python test suite
docs/                       # Documentation
```
