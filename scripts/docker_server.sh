#!/bin/bash

cd docker-files || exit 1
docker compose -p fantasy_lol -f docker-compose.server.yml --env-file ../.env up -d --build
