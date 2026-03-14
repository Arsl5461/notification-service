"""Celery app and tasks for scheduled notifications."""
from celery import Celery
from celery.schedules import crontab
import os

# Use same env as FastAPI
from app.config import get_settings

settings = get_settings()

app = Celery(
    "notification_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.scheduled_alerts"],
)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Run scheduled alerts check every minute
app.conf.beat_schedule = {
    "send-scheduled-alerts": {
        "task": "app.tasks.scheduled_alerts.send_scheduled_alerts",
        "schedule": 60.0,  # every 60 seconds
    },
}
