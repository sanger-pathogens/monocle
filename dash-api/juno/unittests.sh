#!/usr/bin/env bash

PYTHONPATH='.:./dash/api/service'
python3 -m unittest discover -v -s dash/tests -p '*_test.py'
