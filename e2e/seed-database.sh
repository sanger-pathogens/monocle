#!/usr/bin/env bash

# run a command on the api and collect output
ssh -o "StrictHostKeyChecking=no" api "ls -l /app" > on-client.txt
