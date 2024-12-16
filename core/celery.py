import os

import environ
from celery import Celery
import os
from celery import Celery

from django.conf import settings

env = environ.Env()
env.read_env(f"{os.getcwd()}/.envir")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'core.settings')

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
