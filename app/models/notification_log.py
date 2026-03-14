"""Log of sent notifications for auditing and debugging."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class NotificationLog(Base):
    """Log entry when we send a scheduled notification to a location (FCM topic)."""
    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id", ondelete="SET NULL"), nullable=True, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(128), nullable=False)  # e.g. "location-42"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String(1024), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    success: Mapped[bool] = mapped_column(default=True)
    error_message: Mapped[str | None] = mapped_column(String(512), nullable=True)
