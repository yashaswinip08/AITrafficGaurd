"""SQLAlchemy models for violation persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ViolationRecord(Base):
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(primary_key=True)
    violation_type: Mapped[str] = mapped_column(String(64), index=True)
    vehicle_class: Mapped[str] = mapped_column(String(64), default="unknown")
    track_id: Mapped[int] = mapped_column(Integer, index=True)
    plate_text: Mapped[str] = mapped_column(String(128), default="UNKNOWN")
    plate_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    timestamp: Mapped[str] = mapped_column(String(32), index=True)
    frame_number: Mapped[int] = mapped_column(Integer, default=0)
    camera_id: Mapped[str] = mapped_column(String(64), index=True)
    evidence_image_path: Mapped[str] = mapped_column(String(512), default="")
    plate_crop_path: Mapped[str] = mapped_column(String(512), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def build_engine(db_path: str) -> object:
    return create_engine(f"sqlite:///{db_path}")
