#!/usr/bin/env bash

export PYTHONPATH="$(pwd)/../dash-api:$(pwd)/../dash-api/dash:$(pwd)/../dash-api/dash/api/service"

coverage run --source . --omit 'tests/*' -m unittest discover -v -s ./tests -p '*_test.py'
