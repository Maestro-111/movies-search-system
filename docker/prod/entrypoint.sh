#!/bin/bash

export PYTHONPATH="/app:${PYTHONPATH}"

case "$1" in
    "web")
        # Wait for database
        while ! nc -z db 5432; do
            sleep 1
        done

        python movies/manage.py collectstatic --noinput

        gunicorn movies.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 600
        ;;
    "celery_worker")
        celery -A movies worker -l INFO
        ;;
    "celery_beat")
        celery -A movies beat -l INFO
        ;;
    *)
        exec "$@"
        ;;
esac