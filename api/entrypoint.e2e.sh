#!/usr/bin/env bash

echo "Waiting for database to be available."
python manage.py waitfordb

echo "Applying any necessary database migrations."
python manage.py migrate

echo "Loading mock data."
python manage.py loaddev

echo "Starting server."
gunicorn -w 3 -b :80 juno.wsgi
