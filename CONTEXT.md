# Context

## Glossary

| Term | Definition |
|------|-----------|
| **db-migrate** | A one-shot Docker container that runs Alembic migrations to completion before app services start. It is the sole owner of DDL execution. |
| **DatabaseConnectionProvider** | Provides a SQLAlchemy engine and scoped session factory. Does not perform schema management. |
| **Migration** | An Alembic version file that describes a schema change (tables, enums, views). Migrations are the single source of truth for database DDL in Docker and production contexts. |
