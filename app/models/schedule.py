"""Scheduled alert (notification sent at specific times to a location)."""
from datetime import datetime, time
from sqlalchemy import String, Boolean, Time, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Schedule(Base):
    """Schedule: at what time(s) to send an alert to a location (broadcast to all workers there)."""
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g. "Morning check-in"
    message_title: Mapped[str] = mapped_column(String(255), nullable=False)
    message_body: Mapped[str] = mapped_column(String(1024), nullable=False)
    # Time in location's timezone (e.g. 09:00 = 9 AM at that location)
    send_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    location: Mapped["Location"] = relationship("Location", back_populates="schedules")
