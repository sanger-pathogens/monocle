#!/usr/bin/env bash

PYTHONPATH='.'
coverage run --source '.' --omit 'metadata/tests/*,./*noop*' -m unittest discover -v -s metadata/tests -p '*_test.py'
