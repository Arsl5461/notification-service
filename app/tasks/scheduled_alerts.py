"""
Celery tasks: run at scheduled times and send FCM notifications to location topics.
Celery Beat will trigger these; we use a periodic task that runs every minute and
dispatches sends for any schedule whose send_time matches (in location timezone).
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session

from celery_app import app as celery_app
from app.config import get_settings
from app.models.schedule import Schedule
from app.models.location import Location
from app.models.notification_log import NotificationLog
from app.services.fcm_service import send_to_topic

logger = logging.getLogger(__name__)


def get_sync_session() -> Session:
    settings = get_settings()
    engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


@celery_app.task(name="app.tasks.scheduled_alerts.send_scheduled_alerts")
def send_scheduled_alerts():
    """
    Run every minute. For each active schedule, check if current time in location's
    timezone matches send_time; if so, send one FCM message to topic location-{id}.
    """
    session = get_sync_session()
    try:
        result = session.execute(
            select(Schedule, Location).join(Location, Schedule.location_id == Location.id).where(
                Schedule.is_active == True,
                Location.is_active == True,
            )
        )
        for schedule, location in result.all():
            try:
                tz = ZoneInfo(location.timezone) if location.timezone else ZoneInfo("UTC")
                now = datetime.now(tz).time()
                # Match if within same minute (cron runs every minute)
                if (now.hour, now.minute) != (schedule.send_time.hour, schedule.send_time.minute):
                    continue
                topic = f"location-{schedule.location_id}"
                success, err = send_to_topic(
                    topic, schedule.message_title, schedule.message_body
                )
                log = NotificationLog(
                    schedule_id=schedule.id,
                    location_id=schedule.location_id,
                    topic=topic,
                    title=schedule.message_title,
                    body=schedule.message_body,
                    success=success,
                    error_message=err,
                )
                session.add(log)
                session.commit()
                if success:
                    logger.info("Sent alert to topic %s: %s", topic, schedule.message_title)
                else:
                    logger.warning("Failed to send to %s: %s", topic, err)
            except Exception as e:
                logger.exception("Error processing schedule %s: %s", schedule.id, e)
                session.rollback()
    finally:
        session.close()


