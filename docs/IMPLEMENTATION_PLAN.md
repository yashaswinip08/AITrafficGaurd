# AI Traffic Guard — Implementation Plan

## 1. Verified environment

- OS: Windows 11 Home Single Language 10.0.26100
- Python: 3.12.10
- GPU/CUDA: No NVIDIA GPU detected in PATH; `nvidia-smi` unavailable; no `nvcc` in PATH
- Workspace status: empty directory; no existing source files, videos, datasets, or model artifacts found

## 2. Planning assumptions

- This project will be built as a fresh Python package under `src/trafficguard`.
- The environment is CPU-only by default, so all architecture choices must support CPU-first execution with automatic GPU selection when available.
- Model downloads and inference should be implemented in a way that can degrade gracefully when internet access, model licenses, or runtime dependencies are unavailable.
- Because there is no sample traffic video or ground-truth dataset in the repo yet, the first implementation phase will target a reproducible architecture and synthetic/fixture-based validation rather than claiming performance metrics.

## 3. Architecture

The system will follow the requested layered architecture:

VideoSource -> Detector -> Tracker -> PlateDetector -> OCR -> ViolationEngine -> EvidenceWriter -> SQLite Repository -> Dashboard / Alerts

Key design choices:

- `VideoSource`: handles file, webcam, and RTSP input abstraction with graceful validation.
- `Detector`: Ultralytics YOLO-based vehicle and traffic-light detection, configured with a COCO-capable model and device auto-selection.
- `Tracker`: ByteTrack-style persistent track IDs implemented behind a clean abstraction to allow replacement.
- `PlateDetector`: optional dedicated plate detector abstraction with a wrapper around a legally verified model if available.
- `OcrEngine`: interface with EasyOCR as the default implementation and a path for PaddleOCR comparisons later if performance is benchmarked.
- `ViolationEngine`: pluggable rule engine with `NoHelmetRule` and `RedLightRule` as the first production rules.
- `EvidenceWriter`: writes annotated frames, plate crops, and metadata to a structured output directory.
- `Repository`: SQLAlchemy + SQLite model layer for persistent violation records.
- `Dashboard`: Streamlit for overview, filters, evidence viewer, charts, and CSV export.

## 4. Implementation phases

### Phase 1 — Core Computer Vision Pipeline

Objectives:

- Create package skeleton and configuration loading.
- Build video input abstraction and CLI entrypoint.
- Implement YOLO vehicle detection with device auto-selection.
- Add track persistence and track-state management.
- Add plate processing pipeline with normalizer and OCR abstraction.
- Implement red-light and no-helmet rule interfaces and state deduplication.
- Save evidence and store records in SQLite.

Priority and constraints:

- Strictly implement only this phase after approval.
- Validate with synthetic tests and any available demo inputs.
- Do not claim helmet detection success without a verified model and runtime validation.

### Phase 2 — Dashboard and Alerts

Objectives:

- Build Streamlit dashboard with overview cards, filters, evidence viewer, charts, and CSV export.
- Add alert/notifier abstraction with console and optional integrations disabled by default.
- Connect dashboard to SQLite repository.

### Phase 3 — Experimental Extensions

Objectives:

- Add wrong-lane detection behind an explicit experimental flag.
- Add phone-usage and no-seat-belt interfaces with documented TODOs when models are missing.
- Keep these features clearly separate from production-grade rules.

## 5. Model strategy

### Vehicle detection

- Use Ultralytics YOLO.
- Prefer a compact, reliable COCO model from the Ultralytics family with CPU support.
- The selected model should balance accuracy, download size, speed, and hackathon reliability.
- Runtime fallback: CUDA if available, else CPU.

### Plate detection

- Use a dedicated `PlateDetector` abstraction.
- Evaluate only models that are legally downloadable and accessibly documented.
- Document a `download_models.py` script that can fetch only verified artifacts.
- If no suitable verified plate model is available, state this limitation explicitly and keep the pipeline abstracted.

### Helmet detection

- The project will implement the interface and training path immediately.
- Production detection will remain blocked unless a verified helmet model can be downloaded or trained and tested.
- No fake or simulated helmet detection will be reported.

### OCR

- Default to EasyOCR due reliability and straightforward deployment.
- Keep `OcrEngine` abstraction to permit future PaddleOCR benchmarking.

## 6. Data flow

1. Load YAML scene configuration.
2. Open video source and iterate frames.
3. Run YOLO detection to identify vehicles and traffic lights.
4. Track objects across frames using persistent IDs.
5. For each tracked vehicle, crop and evaluate plate detection and OCR as feasible.
6. Aggregate plate readings across frames using confidence-weighted voting.
7. Evaluate each rule plugin against current frame context.
8. Update track-level violation state, deduplication timers, and cooldowns.
9. Save evidence only for confirmed violations.
10. Persist records with SQLite and expose them via Streamlit.

## 7. Database design

- SQLite database using SQLAlchemy ORM.
- Model: `ViolationRecord` with required fields including violation type, plate text, confidence, timestamp, frame number, camera ID, images, and created datetime.
- Add indexes on violation type, timestamp, camera ID, plate text, and track ID.
- Repository pattern to isolate SQL queries from the business logic.

## 8. Testing strategy

Planned test categories:

- Plate normalization and validation
- Red-light rule logic with synthetic tracks
- No-helmet rule logic with expected safe fallback behavior
- Deduplication and cooldown enforcement
- YAML configuration validation and defaults

Testing approach:

- Start with deterministic unit tests for rules and text cleaning.
- Add integration tests only when sample data or stable fixtures are available.
- Use `pytest` for all checks.

## 9. Evaluation strategy

- Add `scripts/evaluate.py` for CSV-based evaluation.
- Evaluate violation precision, recall, F1, and plate accuracy using ground-truth comparison.
- Report results honestly in markdown without claiming targets as achieved unless measured.
- Distinguish target values from measured values in the README.

## 10. Risks and assumptions

### Risks

- No preexisting dataset or demo video in the workspace.
- No GPU/CUDA environment is available.
- Plate model availability and legal suitability may require external validation.
- Helmet/no-helmet model availability is likely blocked without a curated dataset.
- OCR accuracy can vary under motion blur, glare, night scenes, and low-resolution plates.

### Assumptions

- The initial implementation must remain CPU-safe and demo-ready.
- Red-light and plate-cleaning logic can be validated with configurable synthetic data and YAML fixtures.
- Helmet detection will be implemented as a safe capability stub unless a verified model is available.

## 11. Dependencies to confirm after approval

- Python 3.10+ environment
- `ultralytics`
- `opencv-python`
- `easyocr` or alternative OCR package
- `sqlalchemy`
- `streamlit`
- `pyyaml`
- `pytest`
- `numpy`
- Optional: `paddleocr` for benchmarking only

## 12. Risks to document in README and walkthrough

- Night scenes
- Glare and reflection
- Occlusion
- Motion blur
- Distant vehicles
- Low-resolution plates
- Unusual camera angles
- Crowded intersections

## 13. Immediate next step

After approval, proceed with the phase explicitly requested by the user and do not begin broad project implementation beyond that phase.
