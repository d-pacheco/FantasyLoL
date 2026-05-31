# Context

## Glossary

| Term | Definition |
|------|-----------|
| **db-migrate** | A one-shot Docker container that runs Alembic migrations to completion before app services start. It is the sole owner of DDL execution. |
| **DatabaseConnectionProvider** | Provides a SQLAlchemy engine and scoped session factory. Does not perform schema management. |
| **Migration** | An Alembic version file that describes a schema change (tables, enums, views). Migrations are the single source of truth for database DDL in Docker and production contexts. |
| **Game Analysis** | A single unit of work that walks all frames of a completed game to derive duration, multi-kills, and chronological dragon order. Tracked by `frames_status` on the games table. |
| **Multi-kill** | The highest-tier streak (double/triple/quadra/penta) achieved by a player within a 10-second rolling window per kill (30 seconds for penta after quadra). Only the final tier is recorded. |
| **frames_status** | Lifecycle column on the games table tracking Game Analysis state: NULL (not eligible), "pending" (queued), "completed" (done), "unavailable" (no API data). Independent from `details_status`. |
| **Elder Dragon** | A dragon type value `"elder"` in the `game_dragons` table. Distinguished from elemental dragons (infernal, mountain, ocean, etc.) for scoring purposes. |
| **Dragon Soul** | A derived state: a team has Soul when they have taken 4 or more non-elder dragons in a single game. Not stored explicitly — computed at scoring time by counting `game_dragons` rows where `dragon_type != 'elder'` for a given team in a game. |
| **Snake Draft** | The draft order pattern used for fantasy leagues. In odd rounds, picks go in order (position 1→N). In even rounds, the order reverses (N→1). Ensures fairness by giving the last picker in one round the first pick in the next. |
| **Draft Pick** | A single selection during a snake draft. Can be either a professional player (fills a role slot) or a professional team (fills the team slot). Once picked, the player/team is exclusive to that fantasy team for the league. Stored in the `draft_picks` table. |
| **Auto-pick** | A `DraftService` method that picks a random valid player for the first unfilled role slot (top → jungle → mid → adc → support → team). Called by the timer system (Phase 3) when a user's turn expires. |
| **Draft Pool** | The set of professional players and teams eligible for drafting in a fantasy league. Scoped by `available_leagues` on the league settings. Players with `role = 'none'` are excluded. |
| **DraftService** | Owns all draft lifecycle logic: `start_draft`, `make_pick`, `auto_pick`, `get_draft_state`, `get_available_players`, `get_available_teams`. `FantasyTeamService.pickup_player` rejects calls during DRAFT status — all draft-time picks go through `DraftService`. |
| **DraftConnectionManager** | In-memory singleton that tracks WebSocket connections per draft room (`dict[league_id, set[WebSocket]]`). Provides `connect`, `disconnect`, `broadcast(event: DraftEvent)`, and `close_room`. Used by the pick endpoint to push real-time events to connected clients. |
| **DraftEvent** | Base Pydantic model for WebSocket messages pushed to draft room clients. Subclasses: `PickMadeEvent` (includes pick data + next turn user) and `DraftCompletedEvent`. Uses `Literal` type discriminator on the `event` field. |
| **draft_picks** | Table storing the ordered history of all picks in a draft. PK: `(fantasy_league_id, pick_number)`. The count of rows determines whose turn it is (via snake order calculation). Source of truth for draft state — the draft can be fully reconstructed from this table + `draft_order`. |
| **Draft Lifecycle** | PRE_DRAFT → DRAFT (via `start_draft`, sets `current_week=0`) → ACTIVE (automatically after final pick, sets `current_week=1`). A league has exactly `6 × number_of_teams` picks. WebSocket connections are only accepted during DRAFT status and are closed by the server on completion. |
