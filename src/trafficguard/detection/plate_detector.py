"""Dedicated plate detector interface.

This is intentionally safe: the pipeline accepts a configured model path, but if no
verified model is available it remains a no-op rather than inventing detections.
"""

from __future__ import annotations

from typing import Any


class PlateDetector:
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path
        self.enabled = bool(model_path)

    def detect(self, frame: Any) -> list[dict[str, Any]]:
        if not self.enabled:
            return []
        return []
