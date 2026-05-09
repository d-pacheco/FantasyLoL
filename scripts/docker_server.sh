#!/bin/bash
set -e

COMPOSE="docker compose -p fantasy_lol -f docker-files/docker-compose.server.yml --env-file .env"

case "${1:-up}" in
  up)
    $COMPOSE up -d --build
    ;;
  down)
    $COMPOSE down
    ;;
  restart)
    $COMPOSE down
    $COMPOSE up -d --build
    ;;
  *)
    echo "Usage: $0 {up|down|restart}"
    exit 1
    ;;
esac
