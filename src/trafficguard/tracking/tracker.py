"""Persistent object tracker abstraction."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrackedVehicle:
    track_id: int
    class_name: str
    bbox: tuple[int, int, int, int]
    confidence: float
    last_seen: int = 0
    state: str = "ACTIVE"
    metadata: dict[str, Any] = field(default_factory=dict)


class Tracker:
    """Simple centroid-based tracker with persistent IDs across frames."""

    def __init__(self) -> None:
        self._tracks: dict[int, TrackedVehicle] = {}
        self._next_id = 1

    def update(self, detections: list[dict[str, Any]], frame_index: int) -> list[TrackedVehicle]:
        observed: list[TrackedVehicle] = []
        if not detections:
            return observed

        current_boxes: list[tuple[int, int, int, int, str, float]] = []
        for detection in detections:
            bbox = detection.get("bbox")
            if not bbox:
                continue
            x1, y1, x2, y2 = bbox
            class_name = detection.get("class_name", "unknown")
            confidence = float(detection.get("confidence", 0.0))
            current_boxes.append((x1, y1, x2, y2, class_name, confidence))

        for x1, y1, x2, y2, class_name, confidence in current_boxes:
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            match_id = None
            match_distance = None

            for track_id, track in self._tracks.items():
                tx1, ty1, tx2, ty2 = track.bbox
                tcx = (tx1 + tx2) / 2.0
                tcy = (ty1 + ty2) / 2.0
                distance = math.hypot(cx - tcx, cy - tcy)
                if match_distance is None or distance < match_distance:
                    match_id = track_id
                    match_distance = distance

            if match_id is None:
                track_id = self._next_id
                self._next_id += 1
            else:
                track_id = match_id

            track = TrackedVehicle(
                track_id=track_id,
                class_name=class_name,
                bbox=(x1, y1, x2, y2),
                confidence=confidence,
                last_seen=frame_index,
            )
            self._tracks[track_id] = track
            observed.append(track)

        return observed

    def get_active_tracks(self) -> list[TrackedVehicle]:
        return list(self._tracks.values())
