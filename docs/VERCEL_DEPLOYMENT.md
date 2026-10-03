# Vercel Deployment

The root `vercel.json` deploys two services on one project and domain: the FastAPI app receives `/api/*`, and the Vite frontend receives all other paths. The frontend's plate OCR runs in the browser with its worker and English model bundled into the frontend build.

Import the repository into Vercel with the project root set to `.`. The `app` service uses the root `requirements.txt`; the `frontend` service installs `frontend/package-lock.json`. Both services are public through the top-level rewrites. Neither service currently calls the other server-side, so no service binding is needed.

For local testing of both services and their routing, use `vercel dev -L` with a current Vercel CLI. The `vite.config.js` no longer points at a hardcoded local API host.

The API includes PyTorch, EasyOCR, OpenCV, and Ultralytics. New Vercel projects enable Large Functions by default; for an existing project, set `VERCEL_SUPPORT_LARGE_FUNCTIONS=1` in the Production and Preview environments before deploying.
