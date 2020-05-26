#!/usr/bin/env bash

# Run the end-to-end tests.

docker-compose -f docker-compose.e2e.yml build
docker-compose -f docker-compose.e2e.yml up --exit-code-from cypress