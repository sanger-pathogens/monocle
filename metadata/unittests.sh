#!/usr/bin/env bash

PYTHONPATH='.'
python3 -m unittest discover -v -s juno/metadata/tests -p '*_test.py'
