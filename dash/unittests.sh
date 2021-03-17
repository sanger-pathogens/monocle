#!/usr/bin/env bash

PYTHONPATH='.'
python3 -m unittest discover -s DataSources/tests -p '*_test.py'
