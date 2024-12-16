# app_telegram_bot/__init__.py
from core.celery import app as celery_app

__all__ = ('celery_app',)