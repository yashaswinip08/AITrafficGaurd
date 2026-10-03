"""Base rule classes for violation detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class Violation:
    violation_type: str
    vehicle_class: str
    track_id: int
    plate_text: str = "UNKNOWN"
    plate_confidence: float = 0.0
    timestamp: str = ""
    frame_number: int = 0
    camera_id: str = "cam_01"
    confidence: float = 0.0
    evidence_path: str = ""
    plate_crop_path: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        return {
            "violation_type": self.violation_type,
            "vehicle_class": self.vehicle_class,
            "track_id": self.track_id,
            "plate_text": self.plate_text,
            "plate_confidence": self.plate_confidence,
            "timestamp": self.timestamp or datetime.now(UTC).isoformat(),
            "frame_number": self.frame_number,
            "camera_id": self.camera_id,
            "evidence_image_path": self.evidence_path,
            "plate_crop_path": self.plate_crop_path,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class Rule:
    """Base class for violation rules."""

    def check(self, frame_ctx: dict[str, Any]) -> list[Violation]:
        raise NotImplementedError
