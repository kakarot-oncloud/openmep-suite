# 🚀 OpenMEP Deployment Guide

Everything here is written so a **non-technical person can follow it** — copy, paste, done.
Pick the option that matches what you want:

| I want to… | Go to |
|---|---|
| Just run it on my own computer, easiest way | [Docker on your computer](#docker-on-your-computer) |
| Put it online for free without managing a server | [Render](#render) · [Railway](#railway) · [Fly.io](#flyio) |
| Host only the website (fastest, free) | [Vercel / Netlify](#vercel--netlify) |
| Host the simple Streamlit interface for free | [Streamlit Community Cloud](#streamlit-community-cloud) |
| Run a real production site with my own domain + HTTPS | [VPS](#vps) |
| Try it with zero install | [Google Colab](#google-colab) |
| Run from source code (developers) | [Local from source](#local-from-source) |

> **New to all this?** Read [Before you start](#before-you-start) once — it explains the two or three words you'll see everywhere (terminal, Docker, repository).

---

## Before you start

Three words used throughout:

- **Terminal** — the text window where you paste commands. On Windows it's *PowerShell*; on Mac/Linux it's *Terminal*. Search your computer for it.
- **Repository (repo)** — this project's code on GitHub: `https://github.com/kakarot-oncloud/openmep-suite`.
- **Docker** — a free tool that runs the whole app in "containers" so you don't have to install Python, Node, etc. yourself. This is the easiest path.

You'll also see **`git clone`** — that just downloads the code to your computer. No Git? Install it from [git-scm.com](https://git-scm.com/downloads) (click through with defaults).

---

## Docker on your computer

**The easiest way. ~5 minutes.**

**Step 1 — Install Docker Desktop** (free): download from [docker.com](https://www.docker.com/products/docker-desktop/), run the installer, then **open Docker Desktop** and wait until it says *Running*.

**Step 2 — Open a terminal and paste these three lines** (one at a time, Enter after each):

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep-suite
docker compose up -d
```

The first run downloads and builds everything — give it **1–3 minutes**.

**Step 3 — Open your browser** to **http://localhost:3000** 🎉

| Address | What it is |
|---|---|
| http://localhost:3000 | The web app (start here) |
| http://localhost:8000/docs | API explorer |
| http://localhost:8501 | Streamlit UI |

**Useful commands:**
```bash
docker compose down      # stop everything
docker compose up -d     # start again
docker compose logs -f   # see what's happening
```

> 💡 The default database password is `openmep_local_dev` (fine on your own machine). For a public/production deploy, set a strong one — see [Environment variables](#environment-variables).

---

## Render

**Free cloud hosting, click-based. No server to manage.** Gives you a public web address.

1. Create a free account at [render.com](https://render.com) and connect your GitHub.
2. **Fork** this repo to your own GitHub account (button top-right of the repo page).
3. In Render, click **New → Web Service**, pick your fork.
4. Create **two** services:

   **A) The API**
   - Environment: **Docker**, Dockerfile path: `Dockerfile`
   - Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Click **Create Web Service**. When live, copy its URL (e.g. `https://openmep-api.onrender.com`).

   **B) The web app**
   - Environment: **Docker**, Dockerfile path: `frontend/Dockerfile`
   - Add an **Environment Variable**: `VITE_API_BASE` = the API URL from step A.
   - Click **Create Web Service**.

5. Open the web app's URL — you're live. 🎉

> Free instances "sleep" when idle and take ~30s to wake — normal for the free tier.

---

## Railway

**One-click-ish from GitHub. Free trial credit.**

1. Sign up at [railway.app](https://railway.app) with GitHub.
2. **New Project → Deploy from GitHub repo →** select your fork.
3. Railway detects the `Dockerfile`. Add a second service for the frontend using `frontend/Dockerfile`.
4. On the frontend service, add variable `VITE_API_BASE` = your API service's public URL.
5. Click **Deploy**. Railway gives each service a public URL.

---

## Fly.io

**Global edge hosting. Generous free allowance.** Needs the `flyctl` command-line tool (one small install).

1. Install flyctl: [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl/), then `fly auth signup`.
2. Deploy the API from the repo root:
   ```bash
   fly launch --dockerfile Dockerfile        # accept defaults, skip adding a DB
   fly deploy
   ```
   Note the app URL it prints.
3. Deploy the web app:
   ```bash
   cd frontend
   fly launch --dockerfile Dockerfile
   fly secrets set VITE_API_BASE=https://YOUR-api-app.fly.dev
   fly deploy
   ```

---

## Vercel / Netlify

**Host just the website (the React app) — fastest and free.** You point it at an API hosted elsewhere (e.g. [Render](#render)).

**Vercel:**
1. Sign in at [vercel.com](https://vercel.com) with GitHub, **Import** your fork.
2. Set **Root Directory** = `frontend`.
3. Framework preset: **Vite** (build `npm run build`, output `dist`).
4. Add environment variable `VITE_API_BASE` = your API URL.
5. **Deploy.**

**Netlify:** same idea — [app.netlify.com](https://app.netlify.com) → *Add new site* → pick the repo → **Base directory** `frontend`, **Build** `npm run build`, **Publish** `frontend/dist`, add `VITE_API_BASE`.

> The web app is a static site, so these hosts serve it free, worldwide, with HTTPS automatically.

---

## Streamlit Community Cloud

**Free hosting for the simpler Streamlit interface.**

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. **New app** → pick your fork → **Main file path:** `streamlit_app/app.py`.
3. Under **Advanced → Secrets**, add `API_BASE = "https://your-api-url"` (an API you host via [Render](#render), etc.).
4. **Deploy.**

---

## VPS

**A real production site on your own server (DigitalOcean, Hetzner, AWS Lightsail…), with your domain and automatic HTTPS.** ~15 minutes, copy-paste.

**Step 1 — Get a server.** Create the cheapest Ubuntu 22.04 server (1–2 GB RAM is enough). You'll get an **IP address** and log in with SSH:
```bash
ssh root@YOUR_SERVER_IP
```

**Step 2 — Install Docker** (paste on the server):
```bash
curl -fsSL https://get.docker.com | sh
```

**Step 3 — Get the app and set a database password:**
```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep-suite
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" > .env
docker compose up -d
```
The app is now running on the server (ports 3000 / 8000 / 8501).

**Step 4 — Point your domain at the server.** In your domain registrar (GoDaddy, Namecheap, Cloudflare…), add an **A record**: `app.yourdomain.com` → `YOUR_SERVER_IP`.

**Step 5 — Add automatic HTTPS with Caddy** (one tiny file + one command), on the server:
```bash
cat > Caddyfile <<'EOF'
app.yourdomain.com {
    reverse_proxy localhost:3000
}
EOF

docker run -d --name caddy --network host \
  -v $PWD/Caddyfile:/etc/caddy/Caddyfile \
  -v caddy_data:/data caddy:2
```
Replace `app.yourdomain.com` with your domain. Caddy fetches a free HTTPS certificate automatically.

**Done.** Open **https://app.yourdomain.com** 🎉

> Want the API on its own subdomain? Add a second block to the `Caddyfile`:
> ```
> api.yourdomain.com {
>     reverse_proxy localhost:8000
> }
> ```

**Updating later:**
```bash
cd openmep-suite && git pull && docker compose up -d --build
```

---

## Google Colab

Zero install — runs in your browser. Good for a quick one-off calculation.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kakarot-oncloud/openmep-suite/blob/main/colab_launcher.ipynb)

Click the badge, then **Runtime → Run all**.

---

## Local from source

For developers who want to run without Docker.

```bash
git clone https://github.com/kakarot-oncloud/openmep-suite.git
cd openmep-suite

# 1) Calculation API (Python 3.11+)
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000        # http://localhost:8000/docs

# 2) Web app (Node 20+), in a second terminal
cd frontend
npm install
npm run dev                                          # http://localhost:5173

# 3) (optional) Streamlit UI, in a third terminal
streamlit run streamlit_app/app.py                   # http://localhost:8501

# 4) (optional) Node project API
cd src && npm install && npm run dev                 # http://localhost:8080
```

The web app's dev server automatically forwards `/api` calls to `http://localhost:8000`.

---

## Environment variables

Set these in a `.env` file (copy [`.env.example`](../.env.example)) or in your host's dashboard.

| Variable | Default | What it does |
|---|---|---|
| `POSTGRES_PASSWORD` | `openmep_local_dev` | Database password — **set a strong value in production** |
| `API_KEY` | *(unset)* | If set, every calculation request must send header `X-API-Key: <value>` |
| `ALLOWED_ORIGINS` | localhost | Comma-separated list of websites allowed to call the API |
| `VITE_API_BASE` | same-origin | The API address the web app calls (set at **build time** for the frontend) |
| `OPENMEP_DB_PATH` | `openmep_data.db` | Where the project store (SQLite) is saved |
| `PORT` | `8080` | Node project API port |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `docker: command not found` | Docker Desktop isn't installed or not open. Install it and wait for "Running". |
| Web app loads but calculations fail | The web app can't reach the API. Check `http://localhost:8000/health` works and that `VITE_API_BASE` points at it. |
| Port already in use | Something else uses 3000/8000. Stop it, or change the port mapping in `docker-compose.yml`. |
| Free cloud app slow to load first time | Free tiers "sleep" when idle and wake in ~30s. Normal. |
| HTTPS not working on VPS | Make sure the domain's **A record** points to the server IP and ports 80/443 are open in the firewall. |
| Changes not showing after `git pull` | Rebuild: `docker compose up -d --build`. |

Still stuck? Open an issue: [github.com/kakarot-oncloud/openmep-suite/issues](https://github.com/kakarot-oncloud/openmep-suite/issues).
