import os

import environ
from celery import Celery

from django.conf import settings

env = environ.Env()
env.read_env(f"{os.getcwd()}/.envir")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", env.str("DJANGO_SETTINGS_MODULE"))

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks(packages=settings.INSTALLED_APPS)
