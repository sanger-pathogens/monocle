#!/usr/bin/env bash

PYTHONPATH='.'
coverage run -m unittest discover -v -s metadata/tests -p '*_test.py'
