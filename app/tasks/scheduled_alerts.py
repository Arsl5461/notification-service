"""
Celery tasks: run at scheduled times and send FCM notifications to location topics.
Celery Beat will trigger these; we use a periodic task that runs every minute and
dispatches sends for any schedule whose send_time matches (in location timezone).
"""
import logging
import traceback
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


@celery_app.task(name="app.tasks.scheduled_alerts.send_scheduled_alerts", bind=True)
def send_scheduled_alerts(self):
    """
    Run every minute. For each active schedule, check if current time in location's
    timezone matches send_time; if so, send one FCM message to topic location-{id}.
    """
    logger.info("send_scheduled_alerts: task started")
    session = get_sync_session()
    try:
        result = session.execute(
            select(Schedule, Location).join(Location, Schedule.location_id == Location.id).where(
                Schedule.is_active == True,
                Location.is_active == True,
            )
        )
        rows = result.all()
        logger.info("send_scheduled_alerts: found %d active schedule(s)", len(rows))
        for schedule, location in rows:
            try:
                tz_name = location.timezone or "UTC"
                try:
                    tz = ZoneInfo(tz_name)
                except Exception as tz_err:
                    logger.error(
                        "Invalid timezone %r for location id=%s: %s",
                        tz_name,
                        location.id,
                        tz_err,
                        exc_info=True,
                    )
                    session.rollback()
                    continue
                now = datetime.now(tz).time()
                schedule_minute = (schedule.send_time.hour, schedule.send_time.minute)
                current_minute = (now.hour, now.minute)
                logger.debug(
                    "Schedule id=%s location=%s tz=%s now=%s send_time=%s match=%s",
                    schedule.id,
                    location.name,
                    tz_name,
                    now.isoformat(),
                    schedule.send_time.isoformat(),
                    schedule_minute == current_minute,
                )
                if schedule_minute != current_minute:
                    continue
                topic = f"location-{schedule.location_id}"
                logger.info("Sending alert to topic=%s title=%r", topic, schedule.message_title)
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
                if success:
                    schedule.is_active = False
                    logger.info("Sent alert to topic %s: %s; schedule id=%s set inactive", topic, schedule.message_title, schedule.id)
                else:
                    logger.warning("Failed to send to %s: %s", topic, err)
                session.commit()
            except Exception as e:
                logger.exception(
                    "Error processing schedule id=%s (location_id=%s): %s\n%s",
                    schedule.id,
                    schedule.location_id,
                    e,
                    traceback.format_exc(),
                )
                session.rollback()
        logger.info("send_scheduled_alerts: task finished")
    except Exception as e:
        logger.exception(
            "send_scheduled_alerts failed: %s\n%s",
            e,
            traceback.format_exc(),
        )
        raise
    finally:
        session.close()


