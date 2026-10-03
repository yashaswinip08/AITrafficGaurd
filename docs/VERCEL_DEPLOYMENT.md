# Vercel Deployment

Vercel deploys this project as one static JavaScript application. The React frontend runs OCR in the browser using worker, WebAssembly, and English language assets copied into the build. No Python function, API server, environment variable, or external OCR service is required.

1. Import the repository into Vercel and keep the project root set to `.`.
2. Deploy with the checked-in Vercel configuration. It installs the frontend lockfile, builds Vite, and serves `frontend/dist` as a static site.

For local development, run `npm --prefix frontend run dev`. Plate OCR runs locally in the browser; the existing Python pipeline is not part of the Vercel deployment. Image analysis accepts JPG, PNG, and WEBP files up to 15 MB.
