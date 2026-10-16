# SkillForge

SkillForge is a practical coding and industry-readiness platform for learners who want to practice the work software teams actually do: repairing APIs, validating data, optimizing SQL, debugging state, and writing maintainable code.

## What is included

- **React, TypeScript, Vite and Monaco**: landing/auth screens, a responsive learning dashboard, tracks, a multi-language editor, challenge briefs, test cases, hints, an assessment console, and simulated Git feedback.
- **FastAPI and SQLAlchemy**: PostgreSQL-compatible persistence, input validation, role-aware accounts, signed HTTP-only sessions, a seeded challenge catalog, progress metrics, and submission history.
- **Shared TypeScript contracts** in `shared/`.
- **Deployment configuration** for Render, Neon, Vercel, GitHub Actions, and a one-command Cloudflare quick tunnel.

The editor's assessment is deliberately a **static mock rubric**, not a code runner. Submitted source is inspected for syntax and challenge-specific patterns, never executed. The console reports mock checks and explicitly says so. Do not describe these results as real runtime test results or enable arbitrary execution in the API process. A production execution service requires a separately isolated sandbox with resource, network, filesystem, and time limits.

## Requirements

- Node.js 22 or newer and npm
- Python 3.12
- Optional: a PostgreSQL database (local development defaults to SQLite)
- Optional: `cloudflared` for a public development tunnel

## Run locally

From the repository root:

```powershell
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env.local
```

Set `SECRET_KEY` in `backend\.env` to a unique random value before using non-test accounts. For example, generate one with Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Install backend packages and start both services:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
npm install
npm run dev
```

If PowerShell blocks virtual-environment activation, start a new shell with your allowed execution policy or install the backend requirements into the Python interpreter available on `PATH`. `npm run dev` starts FastAPI on `http://localhost:8000` and Vite on `http://localhost:5173`; the frontend proxies `/api` to FastAPI so session cookies remain same-origin.

The API creates its tables and seeds five sample challenges at startup. To rerun the idempotent catalog seed:

```powershell
python -m backend.seed
```

Open `http://localhost:5173`. Create a student account from the sign-in page. Public registration only creates student accounts; to provision an instructor, set both `SEED_INSTRUCTOR_EMAIL` and `SEED_INSTRUCTOR_PASSWORD` (at least 10 characters) in `backend\.env` before starting the API. The app creates that instructor account once if the email is unused. Never use a shared or default production password.

Useful endpoints:

- `GET /api/health` — service health check
- `GET /docs` — interactive API documentation
- `GET /api/tracks` and `GET /api/exercises` — learning catalog
- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- `POST /api/submissions`, `GET /api/submissions/mine`, `GET /api/progress/me`
- `POST /api/assistant/hint`

## Environment

`backend/.env.example` documents API/database settings. The API accepts a PostgreSQL `DATABASE_URL` (including the common `postgres://` and `postgresql://` forms) and normalizes it to the psycopg driver. SQLite is the local default. Configure `APP_ENV=production`, a randomly generated `SECRET_KEY` of at least 32 characters, and the exact frontend origin(s) in `FRONTEND_ORIGINS` for production. Production startup fails if the signing key or frontend origins are missing.

`frontend/.env.example` documents `VITE_API_URL`. Leave it blank when using the included same-origin Vite/Vercel proxy. Do not put server-side secrets in `VITE_*` variables; those values are embedded in the browser bundle.

## Expose a local preview

Start the app locally, install Cloudflare Tunnel (`cloudflared`), then run this in another terminal:

```powershell
npm run preview:public
```

Cloudflare prints a temporary public `trycloudflare.com` URL for the Vite application. The Vite `/api` proxy forwards API traffic to the local FastAPI service, including session-cookie responses. Treat this URL as public while it is active; use test data, and stop the tunnel when finished. For a stable URL, configure a named Cloudflare Tunnel and your own domain instead.

## Public deployment

### 1. Database on Neon

1. Create a PostgreSQL project in [Neon](https://neon.tech/).
2. Copy its pooled or direct connection string and keep it private. The API uses synchronous psycopg connections.
3. Add the URL as the Render service's `DATABASE_URL`. Render SQLite files are not durable across deploys and are not appropriate for a public deployment.

### 2. API on Render

1. Connect the GitHub repository to Render and create a Blueprint from `render.yaml`.
2. The `skillforge-api` Docker service builds from `backend/Dockerfile`, exposes `/api/health`, and generates a unique `SECRET_KEY`.
3. In the Render service settings, set `DATABASE_URL` to the Neon connection string and `FRONTEND_ORIGINS` to the exact deployed frontend origin, e.g. `https://your-project.vercel.app` (no trailing slash).
4. Deploy and verify `https://skillforge-api.onrender.com/api/health` returns `{"status":"ok"}`.

The included Render blueprint selects the free web-service tier to make initial evaluation inexpensive. Free instances can spin down when idle and have limited availability; use a paid always-on service and a managed database plan for dependable production traffic.

### 3. Frontend on Vercel

1. Import the repository into Vercel with the **repository root** as the project root. `vercel.json` builds the npm workspace and publishes `frontend/dist`.
2. The Vercel rewrite sends `/api/*` to `https://skillforge-api.onrender.com/api/*`. If you rename the Render service, update this destination in `vercel.json`.
3. Deploy once and note the exact production origin. Add it to the Render `FRONTEND_ORIGINS` setting, then redeploy the API.
4. The rewrite keeps API calls and the HTTP-only session cookie on the frontend origin; do not replace it with a browser-side cross-origin API URL unless cookie/CORS policy is deliberately reconfigured.

### 4. GitHub continuous deployment

Connect/sync the Render Blueprint so Render automatically deploys backend commits. For Vercel's GitHub Actions workflow, add these repository Actions secrets:

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

The workflow at `.github/workflows/ci-cd.yml` runs the API tests and frontend production build on pull requests and pushes to `main`. Successful pushes to `main` deploy the frontend to Vercel when all three Vercel secrets are configured; otherwise, deployment is skipped with a warning while validation still succeeds. Pull requests run validation only.

## Data model and implementation notes

The SQLAlchemy schema contains `User`, `Track`, `Exercise`, and `Submission` records. `User.role` is `student` or `instructor`; elevated instructor accounts are provisioned through server-side environment configuration rather than self-selected public registration. Tracks include five realistic challenges across API engineering, input validation, SQL aggregation, webhook deduplication, and immutable frontend state.

Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes. Sessions use signed, expiring, HTTP-only cookies with `SameSite=Lax`; the `Secure` flag is enabled in production. CORS uses explicit configured origins and credentialed requests. Never commit `.env` files, secrets, database URLs, or real learner submissions.

The mock assessment checks the submitted text and Python syntax only. The provided test-case examples are curriculum/feedback data and are **not executed**. `execution_time_ms` is the time spent on the mock assessment, not learner program runtime. Instructor reporting, real Git operations, and real sandbox execution are not enabled in this MVP.

## Validate

```powershell
python -m pip install -r backend\requirements.txt
python -m unittest discover -s backend\tests -v
npm install
npm run build
```

The Python test suite covers catalog seeding, account/session behavior, duplicate registration, a complete mock assessment and progress persistence. It uses a local SQLite test database. The frontend build performs TypeScript checking before bundling.
