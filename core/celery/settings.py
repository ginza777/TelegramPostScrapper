from datetime import timedelta

from celery.schedules import crontab

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
    'delete_message_task': {
        'task': 'app_telegram_bot.tasks.delete_message',
        'schedule': crontab(minute=0, hour=0),
    },

}
CELERY_QUEUES = {
    'ads_manager_queue': {
        'exchange': 'ads_manager_queue',
        'routing_key': 'ads_manager_queue.*',
    },
}
