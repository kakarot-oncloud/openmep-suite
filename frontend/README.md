# OpenMEP Web

Modern React + TypeScript front-end for the OpenMEP calculation API — a
responsive, light/dark, production-grade website that replaces the Streamlit UI
over time. Built with Vite, React 18, Tailwind CSS and React Router.

## Stack

- **Vite** + **React 18** + **TypeScript** (strict)
- **Tailwind CSS** design system with CSS-variable light/dark tokens
- **React Router** for client-side routing
- Talks to the FastAPI backend over `/api` (typed client in `src/lib/api.ts`)

## Develop

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173  (proxies /api → http://localhost:8000)
```

Point the dev proxy at a different backend with `VITE_API_BASE`:

```bash
VITE_API_BASE=http://localhost:8000 npm run dev
```

## Build & preview

```bash
npm run build        # type-check + production build to dist/
npm run preview      # serve the built app locally
npm run lint         # eslint (zero warnings enforced)
```

## Configure the API base

- **Dev:** the Vite proxy forwards `/api` to `VITE_API_BASE` (default `http://localhost:8000`).
- **Production:** set `VITE_API_BASE` at build time to your backend origin, **or**
  leave it empty and put a reverse proxy in front that serves the static `dist/`
  and forwards `/api` to the backend (this repo's Docker image does exactly that).

## Deploy

The app is a static SPA — the `dist/` folder deploys to any static host
(Nginx, Netlify, Vercel, S3, a VPS). See `Dockerfile` for a self-contained
Nginx image that builds the app and proxies `/api` to the backend service.

```bash
docker build -t openmep-web ./frontend
docker run -p 8080:80 -e API_UPSTREAM=http://api:8000 openmep-web
```

## Scope

Live in the web app today: **Cable Sizing**, **Cooling Load**, the **Modules**
catalog, and the landing site. The remaining calculators are available in the
API and are being ported page-by-page against this foundation.
