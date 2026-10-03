# Vercel Deployment

Vercel serves the React frontend and FastAPI application from this repository. The root `server.py` re-exports the ASGI app for Vercel discovery; Python dependencies are read from the existing root `requirements.txt`.

1. Import the GitHub repository into Vercel and keep the project root set to `.`.
2. Use the FastAPI framework preset if Vercel does not detect it automatically.
3. Deploy. The frontend uses same-origin `/api` routes, so no API URL environment variable is needed.

For local development, the Vite server proxies `/api` requests to `http://localhost:8000`; leave `VITE_API_BASE_URL` unset.

The OCR and detection dependencies include PyTorch, EasyOCR, OpenCV, and Ultralytics. If the Vercel build reports a Python function bundle-size or runtime-limit error, keep the frontend on Vercel and deploy the Python API to a container host, then set `VITE_API_BASE_URL` to that API's origin.