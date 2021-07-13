#!/usr/bin/env bash

# TODO This needs tidying up - for the moment the dash backend modules/tests are hacked in while changes are still ongoing
PYTHONPATH='/app:/app/dash/api/service:/app/dash/tests/service'
cd dash
python3 -m unittest discover -v -s tests -p '*_test.py'
