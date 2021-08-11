#!/usr/bin/env bash

PYTHONPATH='.'
python3 -m unittest discover -v -s metadata/tests -p '*_test.py'
