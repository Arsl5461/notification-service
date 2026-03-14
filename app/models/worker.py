"""Worker model (employee using Worker App)."""
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Worker(Base):
    """Worker/employee who receives notifications at a selected location."""
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)  # from mobile app
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    fcm_token: Mapped[str | None] = mapped_column(String(512), nullable=True)  # for fallback; topic is primary
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    company: Mapped["Company"] = relationship("Company", back_populates="workers")
    location_assignments: Mapped[list["WorkerLocationAssignment"]] = relationship(
        "WorkerLocationAssignment", back_populates="worker", cascade="all, delete-orphan"
    )
