#!/usr/bin/env bash

# Create a key pair for communication between cypress and api,
# needed for seeding the database between tests.
ssh-keygen -t rsa -b 4096 -C "root@monocle.com" -f e2e/ssh/id_rsa -q -N ""
chmod 400 e2e/ssh/id_rsa
chmod 400 e2e/ssh/id_rsa.pub

# Run the end-to-end tests.
docker-compose -f docker-compose.e2e.yml build
docker-compose -f docker-compose.e2e.yml up --exit-code-from cypress