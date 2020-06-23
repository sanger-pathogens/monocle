#!/usr/bin/env bash

# Create a key pair for communication between cypress and api,
# needed for seeding the database between tests.
mkdir e2e-ssh
ssh-keygen -t rsa -b 4096 -C "root@monocle.com" -f e2e-ssh/id_rsa -q -N ""

# Create directories to mount
mkdir e2e-ssh/cypress
mkdir e2e-ssh/api

# Move and rename keys
cp e2e/cypress-ssh-config e2e-ssh/cypress/config
mv e2e-ssh/id_rsa e2e-ssh/cypress/id_rsa
cp e2e-ssh/id_rsa.pub e2e-ssh/cypress/id_rsa.pub
mv e2e-ssh/id_rsa.pub e2e-ssh/api/authorized_keys

# Set permissions
chmod 644 e2e-ssh/cypress/config
chmod 600 e2e-ssh/cypress/id_rsa
chmod 644 e2e-ssh/cypress/id_rsa.pub
chmod 600 e2e-ssh/api/authorized_keys
chmod 700 e2e-ssh/cypress
chmod 700 e2e-ssh/api

# debug
whoami
ls -l e2e-ssh

# Run the end-to-end tests.
docker-compose -f docker-compose.e2e.yml build
docker-compose -f docker-compose.e2e.yml up --exit-code-from cypress

# clean up (for local usage)
# rm -rf e2e-ssh
