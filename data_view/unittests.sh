#!/usr/bin/env bash

export PYTHONPATH=$(pwd)'/../dash'

python3 -m unittest discover -v -s ./tests -p '*_test.py'
