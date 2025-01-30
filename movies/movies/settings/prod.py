from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*',"127.0.0.1","localhost"]
INTERNAL_IPS = ["127.0.0.1"]

CSRF_TRUSTED_ORIGINS = ['http://localhost:3000']

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'

DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
MEDIA_MAX_SIZE = 5242880  # 5MB

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 300,
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True