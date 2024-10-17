#!/bin/bash

cd docker || exit 1
docker-compose -p fantasy_lol -f docker-compose.local.yml down
docker-compose -p fantasy_lol -f docker-compose.local.yml up -d --build