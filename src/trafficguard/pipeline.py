"""End-to-end traffic violation processing pipeline."""

from __future__ import annotations

import datetime as dt
import logging
from pathlib import Path
from typing import Any

from .evidence.writer import EvidenceWriter
from .rules.base import Violation
from .storage.repository import ViolationRepository
from .tracking.tracker import Tracker

logger = logging.getLogger(__name__)


class TrafficGuardPipeline:
    def __init__(
        self,
        detector: Any,
        tracker: Tracker,
        rules: list[Any],
        repository: ViolationRepository,
        evidence_writer: EvidenceWriter,
        camera_id: str = "cam_01",
    ) -> None:
        self.detector = detector
        self.tracker = tracker
        self.rules = rules
        self.repository = repository
        self.evidence_writer = evidence_writer
        self.camera_id = camera_id
        self._seen_violation_keys: set[tuple[str, int, str]] = set()

    def _dedup_key(self, violation: Violation) -> tuple[str, int, str]:
        return (violation.violation_type, int(violation.track_id), violation.plate_text or "UNKNOWN")

    def process_frame(self, frame: Any, frame_index: int, timestamp: str) -> list[Violation]:
        detections = self.detector.detect(frame)
        tracked = self.tracker.update([
            {"bbox": d.bbox, "class_name": d.class_name, "confidence": d.confidence}
            for d in detections
        ], frame_index)

        ctx = {
            "frame": frame,
            "frame_index": frame_index,
            "timestamp": timestamp,
            "camera_id": self.camera_id,
            "tracks": tracked,
        }

        violations: list[Violation] = []
        for rule in self.rules:
            try:
                rule_violations = rule.check(ctx)
            except Exception as exc:  # pragma: no cover - rule safety
                logger.warning("Rule failed: %s", exc)
                continue
            for violation in rule_violations:
                violation.camera_id = self.camera_id
                violation.timestamp = timestamp
                violation.frame_number = frame_index
                if violation.violation_type and violation.track_id:
                    key = self._dedup_key(violation)
                    if key in self._seen_violation_keys:
                        continue
                    self._seen_violation_keys.add(key)
                evidence_path, plate_crop_path = self.evidence_writer.save_evidence(frame, violation.violation_type, violation.track_id, violation.plate_text)
                violation.evidence_path = evidence_path
                violation.plate_crop_path = plate_crop_path
                violations.append(violation)
                self.repository.save(violation.to_record())
                logger.info("Violation detected: %s | plate=%s | track=%s", violation.violation_type, violation.plate_text, violation.track_id)
        return violations

    def run(self, video_source: Any) -> list[Violation]:
        all_violations: list[Violation] = []
        frame_index = 0
        for frame in video_source:
            timestamp = dt.datetime.utcnow().isoformat()
            violations = self.process_frame(frame, frame_index, timestamp)
            all_violations.extend(violations)
            frame_index += 1
        return all_violations
