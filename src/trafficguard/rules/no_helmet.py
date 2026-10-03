"""No-helmet violation rule with safe fallback behavior."""

from __future__ import annotations

import logging
from typing import Any

from .base import Rule, Violation

logger = logging.getLogger(__name__)


class NoHelmetRule(Rule):
    """Check motorcycles for the absence of a helmet when a detector is available."""

    def __init__(self, detector: Any | None = None) -> None:
        self.detector = detector

    def check(self, frame_ctx: dict[str, Any]) -> list[Violation]:
        if self.detector is None:
            logger.warning("No helmet detection unavailable: detector not configured")
            return []

        violations: list[Violation] = []
        for track in frame_ctx.get("tracks", []):
            if not hasattr(track, "class_name"):
                continue
            if getattr(track, "class_name", "").lower() not in {"motorcycle", "bike", "two-wheeler"}:
                continue
            result = self.detector.detect(frame_ctx.get("frame"), [track.__dict__])
            if not result:
                continue
            for item in result:
                if item.get("no_helmet"):
                    violations.append(
                        Violation(
                            violation_type="no_helmet",
                            vehicle_class=getattr(track, "class_name", "motorcycle"),
                            track_id=int(getattr(track, "track_id", 0)),
                            timestamp=frame_ctx.get("timestamp", ""),
                            frame_number=frame_ctx.get("frame_index", 0),
                            camera_id=frame_ctx.get("camera_id", "cam_01"),
                            confidence=float(item.get("confidence", 0.0)),
                            metadata={"source": "helmet_detector"},
                        )
                    )
        return violations
