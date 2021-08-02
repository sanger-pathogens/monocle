#!/usr/bin/env bash

PYTHONPATH='.'
coverage run -m unittest discover -v -s tests -p '*_test.py'
