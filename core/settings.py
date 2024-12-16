"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

import environ
from celery.schedules import crontab
from django.conf import settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(".envir")



SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=['ads.zamonsher.icu'])
print(100*"-_")
print(f"DEBUG: {DEBUG}")
print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")

INSTALLED_DEFAULT_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

INSTALLED_THIRDPARTS_APPS = [
    'django_celery_results',
    'django_celery_beat',
    'phonenumber_field',
]

INSTALLED_LOCAL_APPS = [
    'app_telegram_bot',
    'app_telegram_client',
]

INSTALLED_APPS = INSTALLED_DEFAULT_APPS + INSTALLED_THIRDPARTS_APPS + INSTALLED_LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = (BASE_DIR / "staticfiles",)

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# celery

CELERY_DEFAULT_QUEUE = 'ads_manager_queue'
BROKER_URL = "redis://localhost:6379"
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Tashkent"

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_BEAT_SCHEDULE = {
    'send-message-task': {
        'task': 'app_telegram_bot.tasks.send_message_task',
        # every 10 seconds
        'schedule': timedelta(seconds=90),
    },
    'delete-message-task': {
        'task': 'app_telegram_bot.tasks.delete_message_task',
        'schedule': crontab(minute=0, hour=0),
    },

}
CELERY_QUEUES = {
    'ads_manager_queue': {
        'exchange': 'ads_manager_queue',
        'routing_key': 'ads_manager_queue.*',
    },
}
