# MythicForge — Fantasy League of Legends

A full-stack Fantasy League of Legends platform that scrapes professional esports data from Riot's API and lets users create and manage fantasy leagues around real competitive matches.

## Overview

MythicForge is composed of three microservices:

- **Fantasy API** (port 8000) — User registration, authentication, fantasy league creation, team drafting, and scoring
- **Riot Data API** (port 8002) — RESTful API to query professional League of Legends data (leagues, tournaments, matches, games, teams, players, and in-game stats)
- **Riot Scraper** (port 8004) — Background service that periodically fetches and stores esports data from Riot's public API on configurable cron schedules

## Tech Stack

- Python 3.12
- FastAPI + Uvicorn
- SQLAlchemy + PostgreSQL
- APScheduler (cron-based job scheduling)
- Pydantic (data validation and schemas)
- JWT authentication (PyJWT + bcrypt)
- Docker + Docker Compose
- GitHub Actions (CI/CD)
- mypy, ruff (code quality)

## Project Structure

```
src/
├── auth/            # JWT bearer token auth and permission handling
├── common/          # Shared config, schemas, logger, exceptions
├── db/              # SQLAlchemy models, DAOs (riot_dao, fantasy_dao), database service
├── fantasy/         # Fantasy API — endpoints and services for leagues, teams, users
├── riot/            # Riot Data API — endpoints and services for esports data
└── riot_scraper/    # Scraper — Riot API client, scrapers, job scheduler
tests/               # Unit tests
docker-files/        # Dockerfiles and docker-compose
scripts/             # Helper scripts for linting, testing, local Docker
.github/workflows/   # CI/CD pipelines (lint, test, Docker image build)
```

## Getting Started

### Prerequisites

- Python 3.12+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install .
   ```

4. Create a `.env` file in the project root:
   ```env
   DATABASE_URL="postgresql://postgres:postgres@localhost:5432/fantasy_lol"
   DEBUG_LOGGING=True
   AUTH_SECRET=<your-secret-key>
   AUTH_ALGORITHM=HS256
   VERIFICATION_DOMAIN_URL="http://localhost"
   VERIFICATION_SENDER_EMAIL=<your-email>
   VERIFICATION_SENDER_PASSWORD=<your-app-password>
   VERIFICATION_SMTP_HOST="smtp.gmail.com"
   VERIFICATION_SMTP_PORT=465
   ```

### Running the Services

Each service runs independently:

```bash
# Fantasy API (port 8000)
python -m src.fantasy.app

# Riot Data API (port 8002)
python -m src.riot.app

# Riot Scraper (port 8004) — requires MASTER_SCRAPER=true env var
MASTER_SCRAPER=true python -m src.riot_scraper.app
```

Once running, interactive API docs are available at:
- Fantasy API: http://localhost:8000/docs
- Riot Data API: http://localhost:8002/docs
- Scraper API: http://localhost:8004/docs

### Running with Docker

```bash
cd docker-files
docker-compose -p fantasy_lol -f docker-compose.local.yml up -d --build
```

Or use the helper script:

```bash
./scripts/docker_local.sh
```

## Development

Install dev dependencies:

```bash
pip install ".[dev]"
```

### Linting

```bash
# Run all checks (ruff lint + ruff format check + mypy)
./scripts/linter.sh

# Individual checks
./scripts/linter.sh --lint
./scripts/linter.sh --mypy

# Auto-format code
./scripts/linter.sh --format
```

### Testing

```bash
./scripts/run_tests.sh
```

Or directly:

```bash
python -m unittest discover -s tests -p "test*.py"
```

## API Highlights

### Fantasy API
- User signup/login with JWT authentication
- Create and manage fantasy leagues with configurable scoring settings
- Draft professional players onto fantasy teams
- League membership and invitation system

### Riot Data API
- Query leagues, tournaments, matches, and games
- Look up professional teams and players
- Retrieve per-game player and team statistics
- Paginated responses

### Scraper
- Automated data collection from Riot's esports API
- Configurable cron schedules for each data type
- Admin-triggered manual job runs via API
