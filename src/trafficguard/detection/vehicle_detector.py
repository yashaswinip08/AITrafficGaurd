"""YOLO-based vehicle detector wrapper."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]


class VehicleDetector:
    """Image detector built on Ultralytics YOLO models."""

    def __init__(self, model_name: str = "yolov8n.pt", device: str = "cpu") -> None:
        self.model_name = model_name
        self.device = device
        self.model = self._load_model()

    def _load_model(self) -> Any:
        try:
            from ultralytics import YOLO
        except Exception as exc:  # pragma: no cover - import guard
            raise RuntimeError("Ultralytics is required for vehicle detection") from exc

        model = YOLO(self.model_name)
        logger.info("Model loaded: %s on %s", self.model_name, self.device)
        return model

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.25) -> list[Detection]:
        if frame is None or frame.size == 0:
            return []

        results = self.model(frame, conf=conf_threshold, verbose=False, device=self.device)
        detections: list[Detection] = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                names = self.model.names if hasattr(self.model, "names") else {}
                class_name = names.get(cls_id, str(cls_id))
                if class_name in {"person", "bicycle", "car", "motorcycle", "bus", "truck", "traffic light"}:
                    detections.append(
                        Detection(
                            class_id=cls_id,
                            class_name=class_name,
                            confidence=conf,
                            bbox=(x1, y1, x2, y2),
                        )
                    )
        return detections
