#!/usr/bin/env bash

export PYTHONPATH="/app"

cd qc-data
coverage run --source . --omit 'tests/*' -m unittest discover -v -s ./tests -p '*_test.py'
