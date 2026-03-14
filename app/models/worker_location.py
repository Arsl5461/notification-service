"""Worker's current location assignment (which location they're at today)."""
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class WorkerLocationAssignment(Base):
    """Current location selected by worker (one active per worker; they can switch)."""
    __tablename__ = "worker_location_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    worker: Mapped["Worker"] = relationship("Worker", back_populates="location_assignments")
    location: Mapped["Location"] = relationship("Location", back_populates="workers")
