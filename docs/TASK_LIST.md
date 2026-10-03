# AI Traffic Guard — Task List

## Phase 1 — Core Computer Vision Pipeline

| Task | Description | Dependency | Expected output | Verification method |
|---|---|---|---|---|
| 1. Project scaffolding | Create package directories, config folder, tests, docs skeleton, and Python packaging structure | None | Initial project structure | File inspection and import checks |
| 2. Configuration system | Implement YAML-driven configuration loading with defaults and validation | Task 1 | `config/default.yaml` and loader utilities | Unit tests for valid/invalid YAML |
| 3. Video I/O abstraction | Build `VideoSource` interface for file/webcam/RTSP input with graceful error handling | Task 1 | Video source classes and CLI input validation | Run with missing/corrupt video and verify error handling |
| 4. Vehicle detection | Integrate Ultralytics YOLO detection with automatic device selection | Tasks 1, 2 | `VehicleDetector` with device reporting | Import check and a sample inference smoke test |
| 5. Tracking abstraction | Build persistent tracker wrapper and track-state management | Task 4 | `Tracker` abstraction with stable IDs | Synthetic track tests and frame-to-frame ID persistence |
| 6. Plate detection abstraction | Define `PlateDetector` interface and model-selection strategy | Task 4 | Model-wrapper scaffolding and downloader hooks | Script inspection and import validation |
| 7. OCR abstraction | Implement `OcrEngine` interface and default EasyOCR integration | Task 6 | OCR engine wrapper and structured results | Unit tests with synthetic OCR output or mocked engine |
| 8. Plate normalization | Implement Indian plate cleaning and validation logic | Task 7 | `plate_text.py` and `PlateReading` dataclass | Plate-text unit tests |
| 9. Multi-frame plate voting | Aggregate multiple readings and select consensus plate text | Tasks 7, 8 | Deterministic voting logic | Unit tests with repeated observations |
| 10. Red-light rule | Implement configurable ROI and stop-line logic with state machine | Tasks 2, 5 | `RedLightRule` and synthetic rule tests | Unit tests for red/green/unknown/crossing sequences |
| 11. No-helmet rule | Implement detector interface and safe blocked behavior if model unavailable | Tasks 4, 5 | `NoHelmetRule` interface plus documentation | Unit tests for safe fallback and rule gating |
| 12. Violation state + deduplication | Implement per-track cooldown and violation-state management | Tasks 10, 11 | Duplicate prevention in pipeline | Deduplication unit tests |
| 13. Evidence writer | Save annotated frames, plate crops, and metadata to structured output folder | Tasks 9, 10, 11 | Evidence files and path management | Run pipeline on sample frames and verify output directory |
| 14. SQLite repository | Create models, repository layer, and record storage | Task 13 | DB schema and insert/query APIs | DB smoke test and record creation check |
| 15. End-to-end pipeline | Connect all phase components in a single pipeline | Tasks 3–14 | Demo pipeline execution | Smoke test with available sample data |

## Phase 2 — Dashboard and Alerts

| Task | Description | Dependency | Expected output | Verification method |
|---|---|---|---|---|
| 16. Dashboard shell | Build Streamlit app structure and database queries | Task 14 | App renders with empty/loaded tables | `streamlit run` smoke test |
| 17. Overview and metrics | Add total violations, counts, and latest records cards | Task 16 | Dashboard overview | UI inspection and data verification |
| 18. Violation table and filters | Add date, type, plate, and camera filters | Task 16 | Filterable violation table | Manual UI validation |
| 19. Evidence viewer | Select a violation and inspect images and metadata | Tasks 13, 16 | Annotated image and crop viewer | UI verification with sample records |
| 20. Charts and export | Add charts and CSV export | Task 16 | Violation charts and CSV export | Run export and verify file output |
| 21. Alert abstraction | Implement console + dashboard alert notifier and optional integrations | Task 16 | `Notifier` base and optional integrations | Config validation and import checks |

## Phase 3 — Experimental Extensions

| Task | Description | Dependency | Expected output | Verification method |
|---|---|---|---|---|
| 22. Wrong-lane detection | Create experimental rule stub with config model | Phase 1 stability | `WrongLaneRule` skeleton and docs | Unit test/feature gate |
| 23. Phone usage detector | Document interface and blocked model requirement | Phase 1 stability | Blocked feature stub and TODO | Documentation review |
| 24. No seat belt detector | Document interface and blocked model requirement | Phase 1 stability | Blocked feature stub and TODO | Documentation review |

## Testing

| Task | Description | Dependency | Expected output | Verification method |
|---|---|---|---|---|
| 25. Plate text tests | Validate valid/invalid formats and OCR confusion substitutions | Task 8 | `test_plate_text.py` | `pytest` pass |
| 26. Red-light tests | Validate rule outcomes with synthetic tracks | Task 10 | `test_red_light.py` | `pytest` pass |
| 27. No-helmet tests | Validate motorcycle/helmet/non-trigger behavior | Task 11 | `test_no_helmet.py` | `pytest` pass |
| 28. Deduplication tests | Ensure one record per violation within cooldown | Task 12 | `test_deduplication.py` | `pytest` pass |
| 29. Configuration tests | Validate YAML parsing and defaults | Task 2 | `test_config.py` | `pytest` pass |
| 30. End-to-end smoke tests | Run relevant pipeline checks on sample data | Tasks 3–14 | Reliability verification | Command output and exit codes |

## Documentation

| Task | Description | Dependency | Expected output | Verification method |
|---|---|---|---|---|
| 31. README | Write project overview, installation, configuration, limitations, roadmap | All major tasks | Professional project README | Manual review |
| 32. Demo script | Add a 3-minute hackathon walkthrough | Phase 1/2 completion | `docs/DEMO_SCRIPT.md` | Manual review |
| 33. Walkthrough artifact | Document implemented/tested/experimental/TODO status by phase | Each phase | `docs/WALKTHROUGH.md` | Real command/test output captured |
| 34. Model management docs | Describe legal-download and blocked-model status | Plate and helmet research | `scripts/download_models.py` and docs | Script review and model source validation |
| 35. Training instructions | Create `scripts/train_helmet.md` with training path | No-helmet rule planning | Training guidance document | Review the procedure for plausibility |
| 36. Evaluation docs | Add `scripts/evaluate.py` and metrics explanations | Results pipeline | Markdown evaluation output | Script run against synthetic or sample CSV |

## Git

| Task | Description | Dependency | Expected output | Verification method |
|---|---|---|---|---|
| 37. Git initialization | Initialize repo if needed and establish ignore rules | None | `.gitignore` and git metadata | `git status` check |
| 38. Commit sequence | Add sensible commits after phase completion | Phase completion | Commit history reflecting milestones | `git log` review |

## Scope gate for approval

This plan intentionally avoids implementation work until the user approves the phase to begin. The next action after approval is to implement only the requested phase, run relevant tests, fix issues, and update the walkthrough artifact before moving on.
