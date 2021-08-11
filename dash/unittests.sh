#!/usr/bin/env bash

PYTHONPATH='.'
coverage run --source DataSources,MonocleDash --omit MonocleDash/components.py -m unittest discover -v -s tests -p '*_test.py'
