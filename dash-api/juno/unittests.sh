#!/usr/bin/env bash

# TODO This needs tidying up (along with package structure) - for the moment the dash backend modules/tests are hacked in while changes are still ongoing
export PYTHONPATH=".:./dash/api/service"
coverage run --source '.' --omit 'dash/tests/*' -m unittest discover -v -s . -p '*_test.py'
