"""Company model."""
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Company(Base):
    """Company/organization that owns locations and workers."""
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    users: Mapped[list["User"]] = relationship("User", back_populates="company", cascade="all, delete-orphan")
    locations: Mapped[list["Location"]] = relationship("Location", back_populates="company", cascade="all, delete-orphan")
    workers: Mapped[list["Worker"]] = relationship("Worker", back_populates="company", cascade="all, delete-orphan")
