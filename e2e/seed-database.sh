#!/usr/bin/env bash

# run a command on the api and collect output
ssh apiroot "ls -l /app" > on-client.txt
