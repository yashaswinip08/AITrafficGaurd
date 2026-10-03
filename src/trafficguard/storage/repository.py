"""Repository layer for SQLite-driven violation storage."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Base, ViolationRecord, build_engine


class ViolationRepository:
    def __init__(self, db_path: str = "data/trafficguard.db") -> None:
        self.engine = build_engine(db_path)
        Base.metadata.create_all(self.engine)

    def save(self, record: dict[str, Any]) -> int:
        with Session(self.engine) as session:
            violation = ViolationRecord(**record)
            session.add(violation)
            session.commit()
            session.refresh(violation)
            return int(violation.id)

    def list_all(self) -> list[ViolationRecord]:
        with Session(self.engine) as session:
            return list(session.scalars(select(ViolationRecord)).all())

    def count_by_type(self, violation_type: str) -> int:
        with Session(self.engine) as session:
            return int(session.query(ViolationRecord).filter(ViolationRecord.violation_type == violation_type).count())
