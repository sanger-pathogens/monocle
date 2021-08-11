#!/usr/bin/env bash

PYTHONPATH='.'
python3 -m unittest discover -v -s tests -p '*_test.py'
