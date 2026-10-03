"""CLI entrypoint for AI Traffic Guard."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .detection.vehicle_detector import VehicleDetector
from .evidence.writer import EvidenceWriter
from .io.video_source import VideoSource
from .pipeline import TrafficGuardPipeline
from .rules.no_helmet import NoHelmetRule
from .rules.red_light import RedLightRule
from .storage.repository import ViolationRepository
from .tracking.tracker import Tracker
from .utils.config import load_yaml
from .utils.device import select_device

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Traffic Guard")
    parser.add_argument("--video", type=str, default="", help="Path to an mp4/video file")
    parser.add_argument("--webcam", type=str, default="", help="Webcam device index, e.g. 0")
    parser.add_argument("--rtsp", type=str, default="", help="RTSP stream URL")
    parser.add_argument("--scene", type=str, default="config/scene_demo.yaml", help="Scene YAML configuration path")
    parser.add_argument("--show", action="store_true", help="Display processed frames while running")
    parser.add_argument("--output", type=str, default="data/outputs", help="Output directory for evidence")
    parser.add_argument("--device", type=str, default="auto", help="Inference device: auto, cpu, cuda")
    return parser


def resolve_source(args: argparse.Namespace) -> str:
    if args.video:
        return args.video
    if args.webcam:
        return f"webcam:{args.webcam}"
    if args.rtsp:
        return args.rtsp
    raise ValueError("No input source supplied: use --video, --webcam, or --rtsp")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_yaml(args.scene)
        device = select_device() if args.device == "auto" else args.device
        detector = VehicleDetector(device=device)
        tracker = Tracker()
        repository = ViolationRepository(db_path=config.get("database", {}).get("path", "data/trafficguard.db"))
        writer = EvidenceWriter(base_dir=args.output)
        rules = [
            NoHelmetRule(detector=None),
            RedLightRule(config.get("scene", {})),
        ]
        source = resolve_source(args)
        video_source = VideoSource(source, camera_id=config.get("camera", {}).get("id", "cam_01"))
        pipeline = TrafficGuardPipeline(detector, tracker, rules, repository, writer, camera_id=config.get("camera", {}).get("id", "cam_01"))
        print(f"Device: {device}")
        pipeline.run(video_source)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
