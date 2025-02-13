#!/bin/bash

export PYTHONPATH="/app:${PYTHONPATH}"


case "$1" in
    "web")
        python movies/manage.py runserver 0.0.0.0:8000
        ;;
    "celery_worker")
        cd movies && celery -A movies worker -l INFO
        ;;
    "celery_beat")
        cd movies && celery -A movies beat -l INFO
        ;;
    *)
        exec "$@"
        ;;
esac