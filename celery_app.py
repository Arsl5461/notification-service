"""Celery app and tasks for scheduled notifications."""
import logging
from celery import Celery
from celery.signals import after_setup_logger

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
    worker_hijack_root_logger=False,
    worker_redirect_stdouts=False,
)


@after_setup_logger.connect
def setup_loggers(*args, **kwargs):
    """Configure Celery worker logging to stdout with a clear format and tracebacks."""
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)
    # Ensure task failures are logged with full traceback
    logging.getLogger("celery.worker").setLevel(logging.INFO)
    logging.getLogger("app.tasks").setLevel(logging.DEBUG)

# Run scheduled alerts check every minute
app.conf.beat_schedule = {
    "send-scheduled-alerts": {
        "task": "app.tasks.scheduled_alerts.send_scheduled_alerts",
        "schedule": 60.0,  # every 60 seconds
    },
}
