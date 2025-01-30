#!/bin/bash

# Cleanup function
cleanup() {
    echo "Cleaning up processes..."
    pkill -f redis
    pkill -f celery
    pkill -f gunicorn
    brew services stop nginx
    exit 0
}

trap cleanup SIGINT

# Clean up existing processes
echo "Cleaning up any existing processes..."
pkill -f redis
pkill -f celery
pkill -f gunicorn
brew services stop nginx
pkill -f "tail -f"  # Also clean up any existing log monitoring

# Set environment
export DJANGO_SETTINGS_MODULE=movies.settings.prod

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start services
echo "Starting Redis..."
redis-server &

echo "Starting Celery worker..."
celery -A movies worker --loglevel=info &

echo "Starting Celery beat..."
celery -A movies beat --loglevel=info &

echo "Starting Gunicorn..."

gunicorn movies.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 600 --max-requests 1000 --max-requests-jitter 50 &

until curl -s http://127.0.0.1:8000 > /dev/null; do
    sleep 1
done

sleep 2

echo "Restarting Nginx..."
brew services restart nginx

echo "All services started. Access the site at http://localhost:3000"

echo "Available memory:"
free -m

top -b -n 1 | grep gunicorn &

wait
