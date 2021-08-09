#!/usr/bin/env bash

export PYTHONPATH=$(pwd)'/../dash'

coverage run --source . -m unittest discover -v -s ./tests -p '*_test.py'
