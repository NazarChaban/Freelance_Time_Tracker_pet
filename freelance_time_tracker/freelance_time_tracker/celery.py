from celery import Celery
import os

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'freelance_time_tracker.settings'
)

app = Celery('freelance_time_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
