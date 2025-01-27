echo "Cleaning up any existing processes..."
pkill -f redis
pkill -f celery
pkill -f "python manage.py runserver"


export DJANGO_SETTINGS_MODULE=movies.settings.local
redis-server &
celery -A movies worker --loglevel=info &
celery -A movies beat --loglevel=info &
python manage.py runserver