"""
Build-time settings. Used during Docker image build for collectstatic.
"""

from .common import *

# Storage backends
# https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-STORAGES

STORAGES = {
    "objectstore": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        "OPTIONS": {
            "location": BASE_DIR / 'staticfiles',
            "base_url": "/static/",
        },
    },
}

STATIC_URL = STORAGES["staticfiles"]["OPTIONS"]["base_url"]
STATIC_ROOT = STORAGES["staticfiles"]["OPTIONS"]["location"]


# Email
# https://docs.djangoproject.com/en/5.2/ref/settings/#email-backend

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'


# Redis disabled at build time
REDIS_URL = None


# Background tasks
# https://docs.djangoproject.com/en/6.0/topics/tasks/

TASKS = {
    "default": {
        "BACKEND": "django_tasks.backends.immediate.ImmediateBackend",
        "QUEUES": ["default"],
    },
}
