"""Minimal API for OCR and violation analysis on uploaded images."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from .analysis import analyze_vehicle_input

app = FastAPI(title="AI Traffic Guard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_directory = Path(__file__).resolve().parents[2] / "frontend" / "dist"
max_upload_bytes = 4 * 1024 * 1024
frontend_mount = getattr(app, "frontend", None)
if callable(frontend_mount):
    frontend_mount("/", directory=str(frontend_directory))
elif frontend_directory.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_directory), html=True), name="frontend")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "AI Traffic Guard API"}


@app.post("/api/analyze")
async def analyze(
    file: Annotated[UploadFile | None, File()] = None,
    violation_type: Annotated[str, Form()] = "red_light",
    plate_hint: Annotated[str | None, Form()] = None,
) -> dict[str, Any]:
    if file is None:
        return {"status": "error", "message": "No image uploaded for analysis."}

    image_bytes = await file.read(max_upload_bytes + 1)
    if len(image_bytes) > max_upload_bytes:
        raise HTTPException(status_code=413, detail="Image must be 4 MB or smaller.")
    return await run_in_threadpool(
        analyze_vehicle_input,
        image_bytes,
        violation_type,
        plate_hint=plate_hint,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("trafficguard.server:app", host="0.0.0.0", port=8000, reload=False)
