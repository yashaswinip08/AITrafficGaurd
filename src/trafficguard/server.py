"""Minimal API for OCR and violation analysis on uploaded images."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analysis import analyze_vehicle_input

app = FastAPI(title="AI Traffic Guard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    image_bytes = await file.read()
    result = analyze_vehicle_input(image_bytes, violation_type=violation_type, plate_hint=plate_hint)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("trafficguard.server:app", host="0.0.0.0", port=8000, reload=False)
