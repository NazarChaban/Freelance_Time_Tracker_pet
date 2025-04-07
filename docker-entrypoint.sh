#!/bin/bash
set -e

# Add PYTHONPATH
export PYTHONPATH="/app/freelance_time_tracker"

# Set DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE="freelance_time_tracker.settings"

# Migrations
echo "Running migrations"
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist and CREATE_SUPERUSER is True
echo "Checking for existing superuser"
python ../scripts/create_superuser.py

# Start debug server if DJANGO_DEBUG is True, otherwise start gunicorn
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
    echo "Running development server"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting server"
    exec gunicorn freelance_time_tracker.wsgi:application --bind 0.0.0.0:8000
fi
