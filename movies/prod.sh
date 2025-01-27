echo "Cleaning up any existing processes..."
pkill -f redis
pkill -f celery
pkill -f gunicorn

export DJANGO_SETTINGS_MODULE=movies.settings.prod
echo "Starting Redis..."
redis-server &

echo "Starting Celery worker..."
celery -A movies worker --loglevel=info &

echo "Starting Celery beat..."
celery -A movies beat --loglevel=info &

echo "Starting Gunicorn..."
gunicorn movies.wsgi:application --bind 127.0.0.1:8000 --workers 3 &

echo "Starting Nginx..."
brew services start nginx

echo "All services started. Access the site at http://localhost:8080"

wait


