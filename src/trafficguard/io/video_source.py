"""Video source abstractions for file/webcam/RTSP inputs."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class VideoSource:
    """Open and stream video frames from supported sources."""

    def __init__(self, source: str, camera_id: str = "cam_01") -> None:
        self.source = source
        self.camera_id = camera_id
        self._cap = None

    def open(self) -> None:
        source = self.source
        if source.startswith("rtsp://") or source.startswith("http://") or source.startswith("https://"):
            self._cap = cv2.VideoCapture(source)
        elif source.isdigit() or source.startswith("webcam:"):
            index = int(source.replace("webcam:", "")) if source.startswith("webcam:") else int(source)
            self._cap = cv2.VideoCapture(index)
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Video file not found: {source}")
            self._cap = cv2.VideoCapture(str(path))

        if not self._cap.isOpened():
            raise RuntimeError(f"Unable to open source: {source}")
        logger.info("Video opened: %s", source)

    def __iter__(self) -> Iterator[np.ndarray]:
        if self._cap is None:
            self.open()
        while True:
            ok, frame = self._cap.read()
            if not ok or frame is None:
                break
            yield frame
        self.close()

    def read(self) -> tuple[bool, np.ndarray | None]:
        if self._cap is None:
            self.open()
        ok, frame = self._cap.read()
        if not ok or frame is None:
            return False, None
        return True, frame

    def close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def fps(self) -> float:
        if self._cap is None:
            return 0.0
        return float(self._cap.get(cv2.CAP_PROP_FPS) or 0.0)

    @property
    def frame_count(self) -> int:
        if self._cap is None:
            return 0
        return int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
