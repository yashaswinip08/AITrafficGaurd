# Vercel Deployment

Vercel builds the React application from the repository root using `vercel.json`. The Python OCR API must be hosted separately; Vercel's static frontend cannot reach a service running on a developer's `localhost`.

1. Import the GitHub repository into Vercel and keep the project root set to `.`.
2. Deploy the Python API to a host that supports the project's CPU and memory requirements.
3. In Vercel project settings, add `VITE_API_BASE_URL` with the deployed API's origin, for example `https://traffic-api.example.com` (no trailing slash).
4. Redeploy the frontend after adding the environment variable.

For local development, the Vite server proxies `/api` requests to `http://localhost:8000`; leave `VITE_API_BASE_URL` unset.