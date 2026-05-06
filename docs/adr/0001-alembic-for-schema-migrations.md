# ADR-0001: Use Alembic for schema migrations

## Status

Accepted

## Context

Multiple services share a single PostgreSQL database and all call `Base.metadata.create_all()` on startup. When services start concurrently (as in `docker-compose.local.yml`), PostgreSQL enum type creation races cause `UniqueViolation` errors, crashing one or more services.

We needed a schema management approach that:
- Eliminates the race condition
- Versions schema changes
- Works for both Docker and local PyCharm development

## Decision

Adopt Alembic as the schema migration tool. A dedicated `db-migrate` container runs `alembic upgrade head` before app services start. App services no longer perform any DDL.

## Alternatives considered

- **Retry on conflict**: Catch `UniqueViolation` and retry `create_all`. Masks the real problem; not production-standard.
- **Stagger service startup via depends_on**: Requires healthchecks on app services; couples schema ownership to one arbitrary service.
- **Each app runs `alembic upgrade head` on startup**: Safe (Alembic serializes via row lock), but blurs the line between app startup and schema management.

## Consequences

- Schema changes require generating a migration file (`alembic revision --autogenerate`).
- Developers must run `alembic upgrade head` before launching apps locally.
- The test suite continues using `create_all`/`drop_all` independently of Alembic.
- One-time `docker volume rm` required to adopt on existing dev environments.
