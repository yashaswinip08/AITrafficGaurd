"""Red-light violation rule with ROI and stop-line logic."""

from __future__ import annotations

import logging
from typing import Any

import cv2
import numpy as np

from .base import Rule, Violation

logger = logging.getLogger(__name__)


class RedLightRule(Rule):
    """Check whether a vehicle crosses a stop line while the light is red."""

    def __init__(self, scene_cfg: dict[str, Any]) -> None:
        self.scene_cfg = scene_cfg or {}
        self.roi = scene_cfg.get("traffic_light", {}).get("roi", {"x1": 0, "y1": 0, "x2": 100, "y2": 100})
        self.stop_line = scene_cfg.get("stop_line", {}).get("points", [[0, 100], [100, 100]])
        self._track_state: dict[int, str] = {}
        self._dedup: dict[int, float] = {}

    def _light_state(self, frame: np.ndarray) -> tuple[str, float]:
        frame_array = np.asarray(frame)
        if frame_array.size == 0:
            return "UNKNOWN", 0.0
        if frame_array.ndim == 2:
            frame_array = cv2.cvtColor(frame_array, cv2.COLOR_GRAY2BGR)
        if frame_array.ndim != 3 or frame_array.shape[2] != 3:
            return "UNKNOWN", 0.0

        x1 = int(self.roi.get("x1", 0))
        y1 = int(self.roi.get("y1", 0))
        x2 = int(self.roi.get("x2", frame_array.shape[1]))
        y2 = int(self.roi.get("y2", frame_array.shape[0]))
        roi = frame_array[max(0, y1):max(0, y2), max(0, x1):max(0, x2)]
        if roi.size == 0:
            return "UNKNOWN", 0.0
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        red_mask1 = cv2.inRange(hsv, (0, 70, 50), (10, 255, 255))
        red_mask2 = cv2.inRange(hsv, (170, 70, 50), (180, 255, 255))
        red_pixels = cv2.countNonZero(red_mask1 | red_mask2)
        total = roi.shape[0] * roi.shape[1]
        red_fraction = red_pixels / float(total) if total else 0.0
        green_mask = cv2.inRange(hsv, (35, 50, 50), (90, 255, 255))
        green_pixels = cv2.countNonZero(green_mask)
        green_fraction = green_pixels / float(total) if total else 0.0
        if red_fraction > 0.08 and red_fraction > green_fraction:
            return "RED", red_fraction
        if green_fraction > 0.08 and green_fraction > red_fraction:
            return "GREEN", green_fraction
        return "UNKNOWN", max(red_fraction, green_fraction)

    def _crossed_stop_line(self, track) -> bool:
        if not hasattr(track, "bbox"):
            return False
        x1, y1, x2, y2 = track.bbox
        cx = (x1 + x2) / 2.0
        line = self.stop_line
        if len(line) < 2:
            return False
        x0, y0 = line[0]
        x1l, y1l = line[1]
        if abs(x1l - x0) < 1e-6:
            return False
        slope = (y1l - y0) / (x1l - x0)
        line_y = y0 + slope * (cx - x0)
        center_y = (y1 + y2) / 2.0
        return center_y > line_y

    def check(self, frame_ctx: dict[str, Any]) -> list[Violation]:
        frame = frame_ctx.get("frame")
        if frame is None:
            return []

        traffic_state, _ = self._light_state(frame)
        if traffic_state != "RED":
            return []

        violations: list[Violation] = []
        for track in frame_ctx.get("tracks", []):
            track_id = int(getattr(track, "track_id", 0))
            if not track_id:
                continue
            vehicle_class = getattr(track, "class_name", "vehicle")
            crossed = self._crossed_stop_line(track)
            state = self._track_state.get(track_id, "NOT_CROSSED")
            if crossed and state != "CROSSED":
                self._track_state[track_id] = "CROSSED"
                violations.append(
                    Violation(
                        violation_type="red_light",
                        vehicle_class=vehicle_class,
                        track_id=track_id,
                        timestamp=frame_ctx.get("timestamp", ""),
                        frame_number=frame_ctx.get("frame_index", 0),
                        camera_id=frame_ctx.get("camera_id", "cam_01"),
                        confidence=1.0,
                    )
                )
            elif not crossed:
                self._track_state[track_id] = "NOT_CROSSED"
        return violations
