#!/usr/bin/env bash

PYTHONPATH='.'
python3 -m unittest discover -v -s DataSources/tests -p '*_test.py'
