"""Location model (branch, office, site)."""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Location(Base):
    """Location (branch, office, site) belonging to a company."""
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)  # e.g. "BRANCH-A"
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)  # for "nearest location"
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")  # for schedule times
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    company: Mapped["Company"] = relationship("Company", back_populates="locations")
    workers: Mapped[list["WorkerLocationAssignment"]] = relationship(
        "WorkerLocationAssignment", back_populates="location", cascade="all, delete-orphan"
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="location", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_locations_company_name", "company_id", "name", unique=True),)
