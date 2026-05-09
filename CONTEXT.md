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
