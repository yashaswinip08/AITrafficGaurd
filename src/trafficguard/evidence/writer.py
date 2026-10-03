"""Evidence writer for annotated frames and plate crops."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import cv2
import numpy as np


class EvidenceWriter:
    def __init__(self, base_dir: str | Path = "data/outputs") -> None:
        self.base_dir = Path(base_dir)

    def save_evidence(self, frame: np.ndarray, violation_type: str, track_id: int, plate_text: str = "UNKNOWN") -> tuple[str, str]:
        today = dt.date.today().isoformat()
        evidence_dir = self.base_dir / "evidence" / today / violation_type
        plate_dir = self.base_dir / "plates"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        plate_dir.mkdir(parents=True, exist_ok=True)

        annotated = frame.copy()
        cv2.putText(annotated, f"Track {track_id}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(annotated, violation_type.replace("_", " ").upper(), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(annotated, plate_text, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        evidence_path = evidence_dir / f"{violation_type}_{track_id}_{int(dt.datetime.utcnow().timestamp())}.png"
        cv2.imwrite(str(evidence_path), annotated)

        plate_crop_path = plate_dir / f"plate_{track_id}_{int(dt.datetime.utcnow().timestamp())}.png"
        cv2.imwrite(str(plate_crop_path), frame)
        return str(evidence_path), str(plate_crop_path)
