"""
Production deployment settings

Configure these environment variables:

  LOGLEVEL_DB          - Database loglevel (default: INFO) (e.g. DEBUG to log SQL queries)
  LOGLEVEL_DB          - Application loglevel (default: INFO)

  SECRET_KEY           - Django secret key (required)
  ALLOWED_HOSTS        - Comma-separated hostnames (required)
  DATABASE_URL         - dj-database-url connection string (required)
  CSRF_TRUSTED_ORIGINS - Comma-separated origins for CSRF (e.g. http://localhost:8080)
  EMAIL_HOST           - SMTP server hostname (required)
  EMAIL_PORT           - SMTP server port (default: 587)
  EMAIL_HOST_USER      - SMTP username (required)
  EMAIL_HOST_PASSWORD  - SMTP password (required)
  DEFAULT_FROM_EMAIL   - Sender address

  OBJECT_STORE_ENDPOINT  - MinIO S3 endpoint (e.g. minio:9000)
  OBJECT_STORE_ACCESS_KEY - MinIO access key (required)
  OBJECT_STORE_SECRET_KEY - MinIO secret key (required)
  OBJECT_STORE_BUCKET    - S3 bucket name (required)
"""

import os

import dj_database_url

from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

CSRF_TRUSTED_ORIGINS = os.environ['CSRF_TRUSTED_ORIGINS'].split(',')


# Database — configured via DATABASE_URL env var
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# https://github.com/jazzband/dj-database-url

DATABASES = {
    'default': dj_database_url.config()
}


# Storage backends
# https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-STORAGES

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": BASE_DIR / 'storage' / 'fileuploads',
            "base_url": "/media/",
        },
    },
    "objectstore": {
        "BACKEND": "minio_storage.storage.MinioMediaStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        "OPTIONS": {
            "location": BASE_DIR / 'staticfiles',
            "base_url": "/static/",
        },
    },
}

# MinIO S3-compatible object store (objectstore)
MINIO_STORAGE_ENDPOINT = os.environ['OBJECT_STORE_ENDPOINT']
MINIO_STORAGE_ACCESS_KEY = os.environ['OBJECT_STORE_ACCESS_KEY']
MINIO_STORAGE_SECRET_KEY = os.environ['OBJECT_STORE_SECRET_KEY']
MINIO_STORAGE_USE_HTTPS = False
MINIO_STORAGE_MEDIA_BUCKET_NAME = os.environ['OBJECT_STORE_BUCKET']
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = True
MINIO_STORAGE_MEDIA_USE_PRESIGNED = False


# Static files
# https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/

STATIC_URL = STORAGES["staticfiles"]["OPTIONS"]["base_url"]
STATIC_ROOT = STORAGES["staticfiles"]["OPTIONS"]["location"]


# File uploads
# https://docs.djangoproject.com/en/5.2/topics/files/

MEDIA_URL = STORAGES["default"]["OPTIONS"]["base_url"]
MEDIA_ROOT = STORAGES["default"]["OPTIONS"]["location"]


# Email
# https://docs.djangoproject.com/en/5.2/topics/email/

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ['EMAIL_HOST']
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = EMAIL_PORT == 587
DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']


# Redis
# https://redis.readthedocs.io/en/v7.3.0/
REDIS_URL = os.environ['REDIS_URL']


# Django Channels — Redis channel layer for production
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    },
}


# Background tasks
# https://docs.djangoproject.com/en/6.0/topics/tasks/

TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.DatabaseBackend",
        "QUEUES": ["default"]
    },
}


# Logging
# https://docs.djangoproject.com/en/5.2/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(otelTraceID)s %(levelname)s %(client_ip)s %(module)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "filters": {
        "request_context": {
            "()": "mysite.middleware.RequestContextFilter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "filters": ["request_context"],
        },
        "otel": {
            "class": "opentelemetry.sdk._logs.LoggingHandler",
        },
    },
    "root": {
        "handlers": ["console", "otel"],
        "level": "INFO",
    },
    'loggers': {
        # Enable Database logging
        'django.db.backends': {
            'level': os.environ.get('LOGLEVEL_DB', 'INFO'),
            'handlers': ['console'],
            'propagate': False,
        },
        # Enable Application logging
        'myapp': {
            'level': os.environ.get('LOGLEVEL_APP', 'INFO'),
            'handlers': ['console'],
            'propagate': False,
        },
    }
}
