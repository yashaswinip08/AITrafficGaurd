"""Helmet detection interface and blocked runtime behavior."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class HelmetDetector:
    """Interface to a dedicated helmet/no-helmet model.

    This project intentionally does not fabricate helmet detections when no validated
    model is available; the detector returns safe defaults until a real model is supplied.
    """

    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path
        self.enabled = bool(model_path)

    def detect(self, frame: Any, detections: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
        if not self.enabled:
            logger.warning("Helmet detection is unavailable: model required")
            return []
        return []
