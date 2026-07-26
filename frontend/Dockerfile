# ── Build stage ──────────────────────────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm install
COPY . .
# VITE_API_BASE is empty by default so the app calls same-origin /api, which
# Nginx forwards to the backend (see nginx.conf). Override at build time if the
# API lives on a different origin.
ARG VITE_API_BASE=""
ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

# ── Serve stage ──────────────────────────────────────────────────────────────
FROM nginx:1.27-alpine AS serve
# API_UPSTREAM is templated into the nginx config at container start.
ENV API_UPSTREAM=http://api:8000
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
# nginx:alpine runs envsubst on /etc/nginx/templates/*.template automatically.
