#!/usr/bin/env bash

export PYTHONPATH="/app"

cd /app/qc-data
coverage run --source . --omit 'tests/*' -m unittest discover -v -s ./tests -p '*_test.py'
