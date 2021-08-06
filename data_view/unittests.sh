#!/usr/bin/env bash

export PYTHONPATH=$(pwd)'/../dash'

coverage run -m unittest discover -v -s ./tests -p '*_test.py'
