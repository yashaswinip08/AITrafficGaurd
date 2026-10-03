# Vercel Deployment

Vercel serves the React frontend and FastAPI application from this repository. The root `server.py` re-exports the ASGI app for Vercel discovery; Python dependencies are read from the existing root `requirements.txt`.

1. Import the GitHub repository into Vercel and keep the project root set to `.`.
2. Use the FastAPI framework preset if Vercel does not detect it automatically.
3. New Vercel projects enable Large Functions by default. For an existing project, add `VERCEL_SUPPORT_LARGE_FUNCTIONS=1` to its Production and Preview environment variables, then redeploy. PyTorch, EasyOCR, and Ultralytics exceed the standard Python function bundle limit.
4. Deploy. The frontend uses same-origin `/api` routes, so no API URL environment variable is needed.

For local development and tests, install `requirements-dev.txt`. The Vite server proxies `/api` requests to `http://localhost:8000`; leave `VITE_API_BASE_URL` unset. Image uploads are limited to 4 MB to stay below Vercel's 4.5 MB function request limit.
