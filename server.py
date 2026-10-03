"""Vercel-discoverable FastAPI entrypoint."""

from src.trafficguard.server import app

__all__ = ["app"]