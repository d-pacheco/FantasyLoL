# Architecture

## Runtime Topology

MythicForge runs as two backend processes, a Vue SPA, and a PostgreSQL database:

```
┌─────────────────────────────────────────────────────────────┐
│  Browser                                                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Nginx (port 8000)                                          │
│  ├── /api/*  → proxy to API (port 8002)                     │
│  └── /*      → serve Vue SPA (static files)                 │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌──────────────────────────┐  ┌──────────────────────────────┐
│  Unified API (port 8002) │  │  Riot Scraper (port 8004)    │
│  ├── /api/v1/riot/*      │  │  ├── APScheduler (cron jobs) │
│  ├── /api/v1/fantasy/*   │  │  ├── Riot API client         │
│  ├── /api/v1/admin/*     │  │  └── /api/v1/* (job triggers)│
│  └── /api/v1/user/*      │  │                              │
└────────────┬─────────────┘  └──────────────┬───────────────┘
             │                                │
             └────────────┬───────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  PostgreSQL 16                                              │
│  ├── Riot data tables (leagues, tournaments, matches, etc.) │
│  ├── Fantasy tables (users, leagues, teams, scoring)        │
│  └── Database views (player_game_view, match_view, etc.)    │
└─────────────────────────────────────────────────────────────┘
```

## Services

### Unified API (`src/app.py` — port 8002)

A single FastAPI application that serves both the Riot Data API and the Fantasy API. Endpoints are organized by domain:

- **`/api/v1/riot/*`** — Read-only esports data (leagues, tournaments, matches, games, teams, players, stats). Paginated via `fastapi-pagination`.
- **`/api/v1/fantasy/*`** — Fantasy league CRUD, team drafting, scoring settings, membership management.
- **`/api/v1/user/*`** — Signup, login (JWT), email verification, account deletion.
- **`/api/v1/admin/*`** — Admin-only operations (scrape-enabled toggles).

Authentication uses JWT bearer tokens (PyJWT + bcrypt). The `JWTBearer` dependency checks permissions per-endpoint.

Endpoint classes use `classy_fastapi.Routable` — each endpoint file is a class with decorated route methods that delegate to a service layer.

### Riot Scraper (`src/riot_scraper/app.py` — port 8004)

A background service that periodically fetches professional League of Legends data from Riot's public esports API. Only runs when `MASTER_SCRAPER=true` is set.

**Internal architecture:**

```
JobScheduler (APScheduler)
  │
  ├── league_service_job      → RiotLeagueScraper.fetch_leagues_from_riot_retry_job
  ├── tournament_service_job  → RiotTournamentScraper.fetch_tournaments_retry_job
  ├── team_service_job        → RiotTeamScraper.fetch_professional_teams_from_riot_retry_job
  ├── match_service_job       → RiotMatchScraper (sync_schedule + backfill + refresh_stale)
  ├── games_from_match_ids    → RiotGameScraper.fetch_games_from_match_ids_retry_job
  ├── update_game_states      → RiotGameScraper.update_game_states_retry_job
  ├── player_metadata_job     → RiotGameStatsScraper.run_player_metadata_retry_job
  ├── player_stats_job        → RiotGameStatsScraper.run_player_stats_retry_job
  └── game_analysis_job       → GameAnalysisScraper.analyze_games_retry_job
```

Each scraper uses `JobRunner.run_retry_job()` which retries up to 3 times with 5-second backoff on failure.

The scraper also exposes a small FastAPI app with manual trigger endpoints (`/api/v1/fetch-leagues`, `/api/v1/run-game-analysis`, etc.) for admin use.

**Default schedules:**

| Job | Schedule |
|-----|----------|
| Leagues | Daily at 10:00 |
| Tournaments | Daily at 10:05 |
| Teams | Daily at 10:10 |
| Matches | Every 15 minutes |
| Games | Every 15 minutes |
| Game stats | Every 5 minutes |
| Game analysis | Every 10 minutes |

### Vue UI (`ui/` — served on port 8000 via nginx)

A Vue 3 + TypeScript SPA using PrimeVue components and Tailwind CSS. Nginx serves the built static files and proxies `/api/*` requests to the API on port 8002.

See `docs/UI_AGENT_INSTRUCTIONS.md` for UI-specific conventions (note: some sections are aspirational and list tools not yet adopted).

## Database

### Schema Management

Alembic manages all DDL. See [ADR-0001](adr/0001-alembic-for-schema-migrations.md).

- In Docker: a `db-migrate` init container runs `alembic upgrade head` before app services start.
- Locally: run `./scripts/migrate.sh upgrade` before starting the API.
- Tests: use `create_all`/`drop_all` directly (independent of Alembic).

Migration files live in `alembic/versions/` with sequential numeric prefixes (001, 002, ...).

### Data Model

**Riot domain** — Mirrors Riot's esports data hierarchy:

```
League → Tournament → Match → Game
                        ├── EventTeams (sides, outcomes)
                        └── Game
                              ├── GameTeams (red/blue side)
                              ├── GameMetadata (patch version)
                              ├── PlayerGameMetadata (champion, role)
                              ├── PlayerGameStats (kills, deaths, assists, etc.)
                              ├── TeamGameStats (gold, towers, barons, etc.)
                              ├── GameParticipantPerks (runes)
                              ├── GameDragons (chronological dragon order)
                              └── GameMultiKills (double/triple/quadra/penta)
```

Professional teams and players are top-level entities referenced by games and events.

**Fantasy domain:**

```
User → FantasyLeague (owner)
         ├── FantasyLeagueMembership (pending/accepted)
         ├── FantasyLeagueScoringSettings
         ├── FantasyLeagueDraftOrder
         └── FantasyTeam (per user, per week — 5 role slots)
```

### Database Views

Three SQL views join commonly-queried data:

- **`player_game_view`** — Joins `player_game_metadata` + `player_game_stats` for a single query to get full player game data.
- **`match_view`** — Joins `matches` + `event_teams` to produce a flat match row with team names, wins, outcomes, and images.
- **`game_view`** — Joins `games` + `game_teams` to show red/blue team IDs and data availability flags.

### DAO Pattern

Database operations are organized into DAO modules under `src/db/riot_dao/` and `src/db/fantasy_dao/`. Each DAO module contains pure functions that accept a SQLAlchemy session and domain schemas. The `DatabaseService` class wraps all DAO calls with session management via `DatabaseConnectionProvider.get_db()` context manager.

## Docker Compose

Three compose files serve different environments:

| File | Purpose |
|------|---------|
| `docker-compose.local.yml` | Full local stack (db + migrate + api + ui + scraper) |
| `docker-compose.server.yml` | Production deployment (uses env vars for credentials) |
| `docker-compose.dev.yml` | Database only (for local Python development) |

The `db-migrate` service uses `condition: service_completed_successfully` to ensure migrations finish before app services start.
