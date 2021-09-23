#!/usr/bin/env bash

export PYTHONPATH="$(pwd)/../dash-api/juno:$(pwd)/../dash-api/juno/dash/api:$(pwd)/../dash-api/juno/dash/api/service"

coverage run --source . --omit 'tests/*' -m unittest discover -v -s ./tests -p '*_test.py'
