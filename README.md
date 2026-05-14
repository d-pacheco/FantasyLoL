# MythicForge — Fantasy League of Legends

A full-stack Fantasy League of Legends platform that scrapes professional esports data from Riot's API and lets users create and manage fantasy leagues around real competitive matches.

Built with Python/FastAPI on the backend, Vue 3/TypeScript on the frontend, and PostgreSQL for persistence. A background scraper service keeps professional match data up-to-date on configurable cron schedules, while the main API powers both the esports data layer and the fantasy league system.

## What It Does

**Esports Data Pipeline** — Automatically ingests leagues, tournaments, matches, games, player stats, and team stats from Riot's public esports API. Includes frame-level game analysis that derives match duration, multi-kill events, and chronological dragon order from raw game frames.

**Fantasy League System** — Users create fantasy leagues, invite friends, draft professional players onto weekly rosters, and score points based on real match performance. Supports configurable scoring weights, draft ordering, and league membership management.

**Single-Page Application** — A responsive Vue 3 frontend with PrimeVue components, Tailwind CSS styling, and real-time data browsing for matches, players, and teams.

## Architecture

```
Browser → Nginx (port 8000) → Vue SPA + API proxy
                                    ↓
                            Unified API (port 8002)
                            ├── /api/v1/riot/*     (esports data)
                            ├── /api/v1/fantasy/*  (fantasy leagues)
                            └── /api/v1/user/*     (auth)
                                    ↓
                              PostgreSQL 16
                                    ↑
                            Riot Scraper (port 8004)
                            └── APScheduler cron jobs
```

The API is a single FastAPI application serving both the Riot data endpoints and the Fantasy league endpoints. Authentication uses JWT bearer tokens. The scraper runs independently, fetching data from Riot's API on configurable schedules (every 5–15 minutes for active match data, daily for league/team metadata).

Database schema is managed by Alembic migrations, run by a dedicated init container in Docker before app services start.

→ [Full architecture details](docs/architecture.md)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | Python 3.12, FastAPI, Uvicorn, Pydantic |
| Database | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| Scraper | APScheduler, cloudscraper, httpx |
| Auth | PyJWT, bcrypt |
| Frontend | Vue 3, TypeScript, Vite, PrimeVue, Tailwind CSS |
| Infrastructure | Docker, Docker Compose, Nginx |
| CI/CD | GitHub Actions (lint, test, Docker build) |
| Code Quality | ruff, mypy (with SQLAlchemy plugin) |

## Getting Started

### Quick Start (Docker)

```bash
cp example.env .env
# Edit .env — set AUTH_SECRET to any random string

./scripts/docker_local.sh
```

This starts the full stack: PostgreSQL → migrations → API → UI → Scraper.

Access the app at http://localhost:8000. API docs at http://localhost:8002/docs.

### Local Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install ".[dev]"
cp example.env .env

# Start PostgreSQL (via Docker or locally)
cd docker-files && docker compose -f docker-compose.dev.yml up -d && cd ..

# Run migrations
./scripts/migrate.sh upgrade

# Start the API
python -m src.app
```

→ [Full development guide](docs/development.md)

## API Highlights

### Fantasy API (`/api/v1/fantasy/*`, `/api/v1/user/*`)

- User signup/login with JWT authentication and email verification
- Create and manage fantasy leagues with configurable scoring settings
- Invite users, manage memberships, set draft order
- Draft professional players onto weekly fantasy rosters (5 roles: top, jungle, mid, adc, support)

### Riot Data API (`/api/v1/riot/*`)

- Query professional leagues, tournaments, matches, and games
- Browse professional teams and players with filtering and search
- Retrieve per-game player and team statistics
- Match schedule view with live/upcoming/recent grouping
- Paginated responses via `fastapi-pagination`

### Scraper (`/api/v1/*` on port 8004)

- Automated data collection from Riot's esports API on cron schedules
- Frame-level game analysis (multi-kills, dragon order, game duration)
- Admin-triggered manual job runs via API
- Retry logic with configurable backoff

## Project Structure

```
src/
├── app.py               # Unified FastAPI application
├── auth/                # JWT auth, permissions
├── common/              # Config, schemas, logging, exceptions
├── db/                  # SQLAlchemy models, DAOs, migrations support
├── fantasy/             # Fantasy API — endpoints, services, business logic
├── riot/                # Riot Data API — endpoints, services
└── riot_scraper/        # Scraper — schedulers, scrapers, Riot API client

ui/                      # Vue 3 + TypeScript frontend
alembic/                 # Database migration files
docker-files/            # Dockerfiles and compose configurations
scripts/                 # Helper scripts (lint, test, migrate, docker)
tests/                   # Python test suite (pytest)
docs/                    # Detailed documentation
```

## Documentation

- [Architecture](docs/architecture.md) — Runtime topology, services, database design, scraper internals
- [Development Guide](docs/development.md) — Local setup, running services, migrations, testing, linting
- [ADR-0001: Alembic Migrations](docs/adr/0001-alembic-for-schema-migrations.md) — Why and how schema migrations work

## License

MIT
