# OpenMEP Deployment Guide

**Version 0.2.1** · Last updated: 2026-04-10

---

## Architecture Overview

OpenMEP is made of three runtime services. Every deployment method runs all three unless noted.

| Service | Technology | Default Port | Responsibility |
|---------|-----------|-------------|----------------|
| **FastAPI** | Python / uvicorn | 8000 | All 26 calculation endpoints (electrical, HVAC, plumbing, fire, BOQ, reports) |
| **Node.js API** | TypeScript / Express | 8080 | 7 Platform Features — project workspaces, version history, submission packager, company branding |
| **Streamlit UI** | Streamlit | 8501 | Web interface — connects to both APIs |
| **PostgreSQL** | postgres:16 | 5432 | Session & project persistence (optional, used in Docker/VPS) |

---

## Deployment Methods

| Method | Best For | Skill Level | Platform Features |
|--------|----------|-------------|-------------------|
| [1. Local Development](#1-local-development) | Development, evaluation | Beginner | ✅ Full |
| [2. Docker Compose](#2-docker-compose) | Teams, self-hosted server | Beginner | ✅ Full |
| [3. VPS without Docker](#3-vps-without-docker-systemd) | Ubuntu/Debian VPS, no Docker | Intermediate | ✅ Full |
| [4. Streamlit Cloud](#4-streamlit-cloud) | Quick public Streamlit demo | Beginner | ⚠️ Calculations only (Node.js hosted separately) |
| [5. Google Colab](#5-google-colab) | Zero-install, one-off calculations | Beginner | ✅ Full |
| [6. React Web App](#6-react-web-app) | Production web frontend | Intermediate | ✅ Full |
| [7. Expo Mobile App](#7-expo-mobile-app-ios--android) | iOS + Android native app | Advanced | ✅ Full |
| [8. Termux (Android)](#8-termux-android) | Full install on Android phone | Beginner | ✅ Full |

---

## 1. Local Development

Run all three services on your own machine for development or single-user evaluation.

### Prerequisites

- Python 3.11+
- Node.js 20+
- pip and npm

### Install

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep

# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
cd src && npm install && cd ..
```

### Start (three terminals)

```bash
# Terminal 1 — FastAPI calculation engine (26 modules)
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Terminal 2 — Node.js Project Management API (Platform Features)
cd src && npm run dev
```

```bash
# Terminal 3 — Streamlit UI
streamlit run streamlit_app/app.py
```

### Verify

```bash
curl http://localhost:8000/health   # {"status":"healthy"}
curl http://localhost:8080/health   # {"status":"healthy","service":"openmep-node-api"}
# Open http://localhost:8501 in browser
```

| URL | What |
|-----|------|
| http://localhost:8501 | Streamlit web UI |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:8080 | Node.js API status |

---

## 2. Docker Compose

One command starts all four services (db, api, node-api, streamlit) in isolated containers.

### Prerequisites

- Docker Engine 24+
- Docker Compose v2

```bash
docker --version          # Docker version 24+
docker compose version    # Docker Compose v2+
```

### Install and start

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep

# Copy and configure the environment file
cp .env.example .env
nano .env   # at minimum, set POSTGRES_PASSWORD

# Build images and start all four services
docker-compose up -d

# Watch startup (wait for all to show "healthy" — takes ~60 seconds)
docker-compose ps
```

### Services and ports

| Container | Port | URL |
|-----------|------|-----|
| db (PostgreSQL) | 5432 | internal only |
| api (FastAPI) | 8000 | http://localhost:8000/docs |
| node-api (Node.js) | 8080 | http://localhost:8080 |
| streamlit | 8501 | http://localhost:8501 |

### Minimum .env

```ini
POSTGRES_PASSWORD=your_strong_password_here
POSTGRES_DB=openmep
POSTGRES_USER=openmep
DATABASE_URL=postgresql://openmep:your_strong_password_here@db:5432/openmep
API_BASE=http://api:8000
NODE_API_BASE=http://node-api:8080
```

### Useful commands

```bash
docker-compose logs -f api        # FastAPI logs
docker-compose logs -f node-api   # Node.js logs
docker-compose logs -f streamlit  # Streamlit logs
docker-compose ps                 # status of all services

docker-compose down               # stop all containers
docker-compose down -v            # stop and delete volumes (data loss!)
docker-compose up -d --build      # rebuild images after code changes
docker-compose restart node-api   # restart one service only
```

### Production — nginx + HTTPS

**Install nginx and Certbot:**

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
sudo certbot --nginx -d openmep.example.com
```

**nginx config** — `/etc/nginx/sites-available/openmep`:

```nginx
server {
    listen 80;
    server_name openmep.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name openmep.example.com;

    ssl_certificate     /etc/letsencrypt/live/openmep.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/openmep.example.com/privkey.pem;

    # Streamlit UI — WebSocket support required
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 86400;
    }

    # FastAPI — calculation endpoints
    location ~ ^/(api/(electrical|mechanical|plumbing|fire|boq|compliance|reports)|docs|redoc|openapi\.json|health) {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Node.js — Platform Features endpoints
    location ~ ^/api/(projects|submission|bim|optimize) {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/openmep /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 3. VPS without Docker (systemd)

Deploy all three services as systemd units on Ubuntu 22.04 / Debian 12.

### Prerequisites

```bash
# System packages
sudo apt update && sudo apt install -y python3.11 python3.11-pip git curl nginx

# Node.js 20 via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
python3.11 --version   # Python 3.11.x
node --version         # v20.x.x
npm --version
```

### Create user and install

```bash
sudo useradd -m -s /bin/bash openmep
sudo su - openmep

git clone https://github.com/kakarot-oncloud/openmep-suite.git ~/openmep
cd ~/openmep

# Python deps
pip3.11 install --user -r requirements.txt

# Node.js deps
cd src && npm install && cd ..

# Create data directory for project files
mkdir -p ~/openmep/data/projects

# Copy env file
cp .env.example .env
nano .env   # set POSTGRES_PASSWORD and any overrides

exit
```

### systemd — FastAPI service

```bash
sudo tee /etc/systemd/system/openmep-api.service > /dev/null << 'EOF'
[Unit]
Description=OpenMEP FastAPI Calculation Engine
After=network.target

[Service]
User=openmep
WorkingDirectory=/home/openmep/openmep
EnvironmentFile=/home/openmep/openmep/.env
ExecStart=/home/openmep/.local/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### systemd — Node.js API service

```bash
sudo tee /etc/systemd/system/openmep-node.service > /dev/null << 'EOF'
[Unit]
Description=OpenMEP Node.js Project Management API
After=network.target

[Service]
User=openmep
WorkingDirectory=/home/openmep/openmep/src
Environment=PORT=8080
Environment=PROJECTS_DIR=/home/openmep/openmep/data/projects
Environment=LOG_LEVEL=info
Environment=NODE_ENV=production
ExecStart=/usr/bin/node --import tsx/esm index.ts
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### systemd — Streamlit UI service

```bash
sudo tee /etc/systemd/system/openmep-ui.service > /dev/null << 'EOF'
[Unit]
Description=OpenMEP Streamlit UI
After=openmep-api.service openmep-node.service

[Service]
User=openmep
WorkingDirectory=/home/openmep/openmep
Environment=API_BASE=http://localhost:8000
Environment=NODE_API_BASE=http://localhost:8080
ExecStart=/home/openmep/.local/bin/streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl enable openmep-api openmep-node openmep-ui
sudo systemctl start openmep-api openmep-node openmep-ui

# Verify all three are active
sudo systemctl status openmep-api openmep-node openmep-ui
```

### Check logs

```bash
sudo journalctl -u openmep-api  -n 50 -f
sudo journalctl -u openmep-node -n 50 -f
sudo journalctl -u openmep-ui   -n 50 -f
```

### Updates

```bash
sudo su - openmep
cd ~/openmep
git pull
pip3.11 install --user -r requirements.txt
cd src && npm install && cd ..
exit
sudo systemctl restart openmep-api openmep-node openmep-ui
```

### nginx + HTTPS

Use the same nginx config shown in the Docker section — it proxies localhost:8000 (FastAPI), localhost:8080 (Node.js), and localhost:8501 (Streamlit). Run:

```bash
sudo certbot --nginx -d yourdomain.com
```

---

## 4. Streamlit Cloud

Streamlit Community Cloud hosts the Streamlit UI for free from your GitHub fork.

> ⚠️ **Limitation:** Streamlit Cloud runs only the Python Streamlit app. The FastAPI backend and Node.js API must be hosted separately. All 26 calculation modules work via `API_BASE`; Platform Features (projects, versioning, branding) additionally need `NODE_API_BASE` pointing to a separately hosted Node.js service.

### Step 1 — Host the backends (Render.com — free tier)

**FastAPI backend on Render:**

1. Create a [Render](https://render.com) account → **New → Web Service**
2. Connect your GitHub fork of OpenMEP
3. Runtime settings:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Copy the Render URL, e.g. `https://openmep-api.onrender.com`

**Node.js API on Render:**

1. **New → Web Service** → same repo
2. Settings:
   - **Root directory:** `src`
   - **Build command:** `npm install`
   - **Start command:** `node --import tsx/esm index.ts`
   - **Environment variables:** `PORT=10000`, `PROJECTS_DIR=/tmp/projects`
3. Copy the Render URL, e.g. `https://openmep-node.onrender.com`

> ⚠️ Free Render services sleep after 15 minutes of inactivity — first request after idle takes 30–60 s to wake up.

### Step 2 — Deploy Streamlit Cloud

1. **Fork** the OpenMEP repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Connect GitHub and set:
   - Repository: `your-username/openmep`
   - Branch: `main`
   - Main file path: `streamlit_app/app.py`
4. Click **Advanced settings → Secrets** and add:
   ```toml
   API_BASE = "https://openmep-api.onrender.com"
   NODE_API_BASE = "https://openmep-node.onrender.com"
   ```
5. Click **Deploy** — Streamlit installs `requirements.txt` automatically

---

## 5. Google Colab

Zero-install. Runs the full OpenMEP stack (FastAPI + Node.js + Streamlit) in a Google Colab VM. A public URL is generated automatically.

### Quick start

Click the badge in the README or go to [colab.research.google.com](https://colab.research.google.com) → **File → Open notebook → GitHub** → paste `kakarot-oncloud/openmep-suite` → select `colab_launcher.ipynb`.

Then press **Runtime → Run all** (`Ctrl+F9`). Wait ~90 seconds. A public URL is printed at the end.

### What the notebook does

| Step | Action |
|------|--------|
| 1 | Clone repo from GitHub |
| 2 | Install Python deps (`requirements.txt`) |
| 3 | Install Node.js 20 + npm deps (`src/package.json`) |
| 4 | Start FastAPI on port 8000 (background) |
| 5 | Start Node.js API on port 8080 (background) |
| 6 | Verify both services respond on `/health` |
| 7 | Launch Streamlit with a public tunnel URL |

### Limitations

- Google free tier sessions run up to 12 hours — data is lost when the session ends
- For persistent project data: mount Google Drive and set `PROJECTS_DIR=/content/drive/MyDrive/openmep-projects`

---

## 6. React Web App

Deploy a Vite + React frontend that connects to the OpenMEP FastAPI and Node.js backends.

> The React app code lives in `web/` (v0.3.0 milestone). These instructions cover the deployment pattern for when that directory ships. The app connects to the same APIs as all other frontends.

### Local development

```bash
cd web
npm install

# Create local env file
cat > .env.local << 'ENVEOF'
VITE_API_BASE=http://localhost:8000
VITE_NODE_API_BASE=http://localhost:8080
ENVEOF

npm run dev
# Open http://localhost:5173
```

### Production build

```bash
cd web

cat > .env.production << 'ENVEOF'
VITE_API_BASE=https://api.openmep.example.com
VITE_NODE_API_BASE=https://node.openmep.example.com
ENVEOF

npm run build
# Output in web/dist/
```

### Deploy to Netlify (free tier)

```bash
npm install -g netlify-cli
cd web && npm run build
netlify deploy --prod --dir=dist
```

Via dashboard: New site → Import from Git → set base directory `web`, build command `npm run build`, publish directory `web/dist`. Add env vars `VITE_API_BASE` and `VITE_NODE_API_BASE`.

### Deploy to Vercel (free tier)

```bash
npm install -g vercel
cd web && vercel --prod
```

Create `web/vercel.json`:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

Set env vars in Vercel dashboard under **Settings → Environment Variables**.

### Self-hosted with nginx

```bash
cd web && npm run build
sudo cp -r dist /var/www/openmep-web
```

```nginx
server {
    listen 443 ssl;
    server_name app.openmep.example.com;

    ssl_certificate /etc/letsencrypt/live/app.openmep.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.openmep.example.com/privkey.pem;

    root /var/www/openmep-web;
    index index.html;

    # React Router — serve index.html for all client-side routes
    location / { try_files $uri $uri/ /index.html; }
}
```

### CORS configuration

Add the React app's origin to the FastAPI `.env`:

```ini
ALLOWED_ORIGINS=https://app.openmep.example.com,http://localhost:5173
```

---

## 7. Expo Mobile App (iOS + Android)

Deploy a React Native / Expo app that connects to the OpenMEP backends.

> The Expo app code lives in `mobile/` (v0.4.0 milestone). These instructions cover the deployment pattern. The app connects to the same FastAPI and Node.js APIs as all other frontends.

### Prerequisites

```bash
npm install -g @expo/cli eas-cli
node --version   # must be 20+
```

### Local development (Expo Go — fastest)

```bash
cd mobile
npm install

# Use your machine's LAN IP — the phone cannot reach "localhost"
# Find it: ipconfig (Windows) or ifconfig / ip addr (Mac/Linux)
# Example: 192.168.1.100

cat > .env.local << 'ENVEOF'
EXPO_PUBLIC_API_BASE=http://192.168.1.100:8000
EXPO_PUBLIC_NODE_API_BASE=http://192.168.1.100:8080
ENVEOF

npx expo start
```

- Scan the QR code with **Expo Go** on your physical device
- Press `a` for Android emulator (Android Studio required)
- Press `i` for iOS simulator (Xcode on macOS required)

> ⚠️ Always use your LAN IP address, not `localhost`. A physical phone cannot reach your computer's loopback interface.

### Production environment config

In `mobile/app.config.ts`:

```typescript
export default {
  expo: {
    name: "OpenMEP",
    slug: "openmep",
    version: "0.2.1",
    extra: {
      apiBase: process.env.EXPO_PUBLIC_API_BASE ?? "https://api.openmep.example.com",
      nodeApiBase: process.env.EXPO_PUBLIC_NODE_API_BASE ?? "https://node.openmep.example.com",
    },
  },
};
```

In your API calls:

```typescript
import Constants from "expo-constants";
const API_BASE = Constants.expoConfig?.extra?.apiBase ?? "https://api.openmep.example.com";
const NODE_API_BASE = Constants.expoConfig?.extra?.nodeApiBase ?? "https://node.openmep.example.com";
```

### Cloud builds with EAS (recommended)

```bash
# Log in to Expo account
eas login

# Set up EAS for this project (generates eas.json)
eas build:configure

# Build for both platforms (cloud build — no local toolchain needed)
eas build --platform all

# Build Android only
eas build --platform android --profile production

# Build iOS only (requires Apple Developer account — $99/year)
eas build --platform ios --profile production
```

### Submit to stores

```bash
# Google Play Console ($25 one-time)
eas submit --platform android

# Apple App Store ($99/year Apple Developer Program)
eas submit --platform ios
```

### Local builds (no EAS cloud)

```bash
# Android (requires Android Studio + Android SDK)
npx expo run:android

# iOS (requires macOS with Xcode 15+)
npx expo run:ios
```

### Backend requirements for mobile production

- FastAPI and Node.js APIs must be **publicly accessible over HTTPS** — iOS App Transport Security (ATS) and Android Network Security Configuration block plain HTTP in production builds
- Set `ALLOWED_ORIGINS=*` in `.env` for mobile clients (or restrict to specific origins)
- Recommended backend: Docker Compose + nginx + Let's Encrypt on a VPS (see [Section 2](#2-docker-compose))

---

## 8. Termux (Android)

Run the complete OpenMEP stack natively on an Android phone — no cloud or PC required.

### Step 1 — Install Termux

Install from [F-Droid](https://f-droid.org/packages/com.termux/) — **do not use the Google Play version** (it is abandoned and broken).

### Step 2 — Install system packages

```bash
pkg update && pkg upgrade -y
pkg install -y python git nodejs curl
pip install --upgrade pip
```

### Step 3 — Clone and install dependencies

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git ~/openmep
cd ~/openmep

# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
cd src && npm install && cd ..
```

### Step 4 — Run all three services

**Option A — Three Termux sessions (recommended — all Platform Features)**

Session 1 — FastAPI:

```bash
cd ~/openmep
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Session 2 — swipe left → **New Session** — Node.js API:

```bash
cd ~/openmep/src
PORT=8080 node --import tsx/esm index.ts
```

Session 3 — swipe left → **New Session** — Streamlit UI:

```bash
cd ~/openmep
API_BASE=http://127.0.0.1:8000 NODE_API_BASE=http://127.0.0.1:8080 \
  python -m streamlit run streamlit_app/app.py --server.address 127.0.0.1
```

**Option B — All in background (single session)**

```bash
cd ~/openmep
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
PORT=8080 node --import tsx/esm src/index.ts &
API_BASE=http://127.0.0.1:8000 NODE_API_BASE=http://127.0.0.1:8080 \
  python -m streamlit run streamlit_app/app.py --server.address 127.0.0.1
```

### Step 5 — Open in browser

Open Chrome or Firefox on your Android phone:

| URL | What |
|-----|------|
| http://localhost:8501 | Streamlit web UI |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:8080 | Node.js API |

### Step 6 — Verify

```bash
curl http://localhost:8000/health   # {"status":"healthy"}
curl http://localhost:8080/health   # {"status":"healthy","service":"openmep-node-api"}
```

### Keep running in the background

```bash
# Install Termux:Boot from F-Droid (runs Termux on phone reboot)
termux-wake-lock   # prevents Android from killing the processes
```

### Update

```bash
cd ~/openmep && git pull
pip install -r requirements.txt
cd src && npm install && cd ..
# Restart all three services
```

---

## Environment Variables Reference

| Variable | Default | Used By | Description |
|----------|---------|---------|-------------|
| `API_BASE` | `http://localhost:8000` | Streamlit | URL for Streamlit → FastAPI |
| `NODE_API_BASE` | `http://localhost:8080` | Streamlit | URL for Streamlit → Node.js API |
| `PORT` | `8080` | Node.js | Express server port |
| `PROJECTS_DIR` | `./data/projects` | Node.js | Where project JSON files are stored |
| `LOG_LEVEL` | `info` | Node.js | Verbosity: `silent` / `info` / `warn` / `error` |
| `POSTGRES_PASSWORD` | *(required in Docker)* | db | PostgreSQL database password |
| `DATABASE_URL` | *(auto)* | FastAPI | Full PostgreSQL connection string |
| `ALLOWED_ORIGINS` | `http://localhost:8501` | FastAPI | CORS whitelist — comma-separated origins |
| `API_KEY` | *(unset = open)* | FastAPI | Require `X-API-Key` header when set |
| `API_WORKERS` | `2` | FastAPI | Uvicorn worker processes |
| `DEBUG` | `false` | FastAPI | Show exception details in 500 responses |

---

## Troubleshooting

### FastAPI not starting

```bash
python3 --version              # must be 3.11+
lsof -i :8000                  # port already in use?
pip install -r requirements.txt
journalctl -u openmep-api -n 50   # systemd logs
```

### Node.js API not starting

```bash
node --version                 # must be 20+
lsof -i :8080                  # port in use?
cd src && npm install          # re-install deps
journalctl -u openmep-node -n 50   # systemd logs
# tsx must be in dependencies, not devDependencies
```

### Streamlit showing "API Offline"

- FastAPI is not running → start it on port 8000
- Check `API_BASE` env var:
  - Local / VPS: `http://localhost:8000`
  - Docker: `http://api:8000`
  - Streamlit Cloud: `https://your-render-url.onrender.com`

### Docker — container stays "unhealthy"

```bash
docker-compose logs api       # Python import errors?
docker-compose logs node-api  # Node.js startup errors?
docker-compose logs db        # Postgres auth issues?
docker-compose up -d --build  # rebuild after code changes
```

### Mobile — "Network request failed" in Expo Go

- Use your LAN IP (e.g. `192.168.1.100:8000`) instead of `localhost`
- Ensure phone and computer are on the same Wi-Fi network
- In production builds, the backend must be HTTPS — iOS blocks plain HTTP

### Streamlit Cloud — "Module not found"

All packages in `requirements.txt` are installed automatically. Add any missing package there and redeploy.

### Termux — `streamlit` or `uvicorn` command not found

```bash
pip install streamlit uvicorn
pip show streamlit   # confirm install location
```

### VPS — `tsx` not found in systemd unit

```bash
# tsx must be in src/package.json "dependencies" (not devDependencies)
grep tsx /home/openmep/openmep/src/package.json   # confirm it's there
cd /home/openmep/openmep/src && npm install
which node   # confirm node path; update ExecStart if /usr/bin/node is wrong
```
