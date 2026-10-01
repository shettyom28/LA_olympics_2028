"""
Development settings — used by default with manage.py runserver.
"""

import os

from .common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7hp2fft-qwmeb4s=dx463o!vw-biw!mnq448@amuuxl^e_!gob'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Trust the Vite dev server origin for CSRF checks
CSRF_TRUSTED_ORIGINS = ['http://localhost:5173']


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": BASE_DIR / 'storage' / 'objectstore',
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "OPTIONS": {
            "location": BASE_DIR / 'staticfiles',
            "base_url": "/static/",
        },
    },
}


# Static files
# https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/

STATIC_URL = STORAGES["staticfiles"]["OPTIONS"]["base_url"]
STATIC_ROOT = STORAGES["staticfiles"]["OPTIONS"]["location"]


# File uploads
# https://docs.djangoproject.com/en/5.2/topics/files/

MEDIA_URL = STORAGES["default"]["OPTIONS"]["base_url"]
MEDIA_ROOT = STORAGES["default"]["OPTIONS"]["location"]


# Email
# https://docs.djangoproject.com/en/5.2/ref/settings/#email-backend

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'myapp@localhost'


# Redis (optional)
# https://redis.readthedocs.io/en/v7.3.0/
REDIS_URL = os.environ.get('REDIS_URL', None)


# Django Channels — in-memory layer for local development (no Redis needed)
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# Background tasks
# https://docs.djangoproject.com/en/6.0/topics/tasks/

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
        "QUEUES": ["default"],
    },
}


# Logging
# https://docs.djangoproject.com/en/5.2/topics/logging/

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "dev": {
            "format": "%(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "dev",
        },
    },
    "root": {
        "handlers": ["console"],
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