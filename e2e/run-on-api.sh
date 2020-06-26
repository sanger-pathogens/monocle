#!/usr/bin/env bash

docker-compose -f ../docker-compose.e2e.yml exec -T api "$@"
