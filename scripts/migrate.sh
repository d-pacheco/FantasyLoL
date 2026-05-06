#!/bin/bash
# Database migration helper script
# Usage:
#   ./scripts/migrate.sh upgrade        - upgrade to latest
#   ./scripts/migrate.sh downgrade <rev> - downgrade to specific revision (or -1, -2, etc.)
#   ./scripts/migrate.sh history        - show migration history
#   ./scripts/migrate.sh current        - show current revision
#   ./scripts/migrate.sh generate "msg" - autogenerate a new migration

set -e

export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/fantasy_lol}"

case "${1}" in
  upgrade)
    alembic upgrade "${2:-head}"
    ;;
  downgrade)
    if [ -z "$2" ]; then
      echo "Usage: ./scripts/migrate.sh downgrade <revision|-N>"
      exit 1
    fi
    alembic downgrade "$2"
    ;;
  history)
    alembic history --verbose
    ;;
  current)
    alembic current
    ;;
  generate)
    if [ -z "$2" ]; then
      echo "Usage: ./scripts/migrate.sh generate \"description\""
      exit 1
    fi
    alembic revision --autogenerate -m "$2"
    ;;
  *)
    echo "Usage: ./scripts/migrate.sh {upgrade|downgrade|history|current|generate}"
    echo ""
    echo "Commands:"
    echo "  upgrade [rev]       Upgrade to rev (default: head)"
    echo "  downgrade <rev>     Downgrade to rev (e.g., 001 or -1)"
    echo "  history             Show all migrations"
    echo "  current             Show current database revision"
    echo "  generate \"msg\"      Autogenerate a new migration"
    exit 1
    ;;
esac
