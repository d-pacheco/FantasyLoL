#!/bin/bash

docker build -f docker-files/Dockerfile-scraper -t lol_scraper .

cd docker-files || exit 1
docker-compose -p fantasy_lol -f docker-compose.local.yml down
docker-compose -p fantasy_lol -f docker-compose.local.yml up -d --build
