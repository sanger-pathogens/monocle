#!/usr/bin/env bash

# e2e tests require migration and loading of test data
python manage.py migrate
python manage.py loaddev

# start server
gunicorn -w 3 -b :80 juno.wsgi
