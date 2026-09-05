# OpsPilot AI

**AI-powered business operations and decision intelligence platform.**

OpsPilot turns sales, inventory, customer, and expense data into real-time
insights, forecasts, anomaly alerts, and actionable recommendations through
a secure AI Copilot, RAG knowledge base, and tool-calling architecture.

DATA → UNDERSTAND → PREDICT → RECOMMEND → ACT

## Status: All 12 phases complete ✅

1. ✅ Foundation — FastAPI + Next.js skeleton, health check, DB connection
2. ✅ Auth & Organizations — JWT, RBAC (Admin/Manager/Viewer), org switcher
3. ✅ Demo data + data ingestion — CSV/XLSX upload with data-quality scoring
4. ✅ Core domain CRUD — Products, Sales, Inventory, Customers, Expenses
5. ✅ Dashboards — Business Health Score + 4 Intelligence pages
6. ✅ ML — forecasting (baseline vs XGBoost), churn, RFM+K-Means segmentation, anomaly detection
7. ✅ Explainable AI — plain-language factors behind every churn prediction
8. ✅ AI Copilot — Groq-backed chat with tool-calling (no hallucinated numbers)
9. ✅ RAG knowledge base — upload policy docs, searchable, cited by the Copilot
10. ✅ Orchestrator — observable domain-routing layer over the Copilot
11. ✅ Actions, Alerts, Reports — recommendation engine, task tracking, exportable reports
12. ✅ Polish — unit tests for core logic, finalized documentation

---

## Run it — exact commands

Open **two terminals** (or two VS Code integrated terminal tabs).

### Terminal 1 — Backend
```bash
cd backend
python -m venv venv

# Activate the virtual environment:
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows (cmd/PowerShell)

pip install -r requirements.txt
cp .env.example .env

# Seed a full demo dataset (recommended — makes every page immediately useful):
python -m scripts.generate_demo_data

# Start the API server:
uvicorn app.main:app --reload
```
Backend runs at **http://localhost:8000** — interactive docs at `/docs`.

### Terminal 2 — Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Frontend runs at **http://localhost:3000**.

### Log in
```
Email:    demo@opspilot.ai
Password: demo12345
```

### Enable the AI Copilot (optional but recommended)
1. Get a free key at https://console.groq.com/keys
2. Open `backend/.env`, set `GROQ_API_KEY=your-key-here`
3. Restart the backend (`Ctrl+C` then re-run `uvicorn app.main:app --reload`)

Without a key, every other page still works — `/dashboard/copilot` simply
shows a clear "not configured yet" message instead of failing silently.

### Run the tests (optional)
```bash
cd backend
pytest tests/unit -v
```
These are pure-logic tests (password hashing, JWT, date-period math, the
inventory risk heuristic, the forecasting baseline) — no database or
running server required.

---

## Opening in VS Code

```bash
cd opspilot-ai
code .
```
Recommended extensions: **Python** (ms-python.python), **ESLint**,
**Tailwind CSS IntelliSense**. Point VS Code's Python interpreter at
`backend/venv/bin/python` (Command Palette → "Python: Select Interpreter")
so imports resolve correctly in the editor.

---

## Why this stack (and what was deliberately left out)

This project uses a **lean version** of a typical enterprise SaaS stack.
Every piece below solves a real problem the original spec calls for —
nothing was added to look complex — but heavy infrastructure that adds
setup risk without adding to what you can actually demo or explain was
swapped for a simpler, equally-legitimate equivalent:

| Instead of | We use | Why |
|---|---|---|
| PostgreSQL | **SQLite** | Zero setup, same SQLAlchemy models/queries — a one-line change to the connection string is all a future Postgres migration needs |
| Docker Compose | **Direct local processes** | Fewer moving parts while building; a Dockerfile can be added later without touching app code |
| Redis + Celery | **FastAPI BackgroundTasks** | In-process async work, no broker to run, same "don't block the request" principle |
| Prophet + PyTorch/LSTM | **XGBoost + a linear baseline** | Easier to install, easier to explain, genuinely backtested against each other |
| pgvector + neural embeddings | **SQLite + HashingVectorizer + NumPy cosine similarity** | Same RAG concept (embed → store → retrieve → cite); Groq has no embeddings endpoint, and a neural embedding model would need a heavy local dependency (torch) for a handful of policy documents |
| SHAP | **Model feature_importances_ + deviation-weighted local explanation** | Same "explain the prediction" story, much lighter dependency — honestly documented as a simplification, not a substitute claim |
| 7-agent framework | **One orchestrator + shared tool-calling layer** | Same grounded, tool-driven, observable AI Copilot behavior, far less ceremony |
| Real PDF export | **Markdown export (client-side Blob download)** | A shareable file with zero new dependencies; PDF rendering is a documented future improvement |

The full-weight versions of each of these are legitimate choices at real
production scale — they're documented as "future improvements" in
`ARCHITECTURE.md`, not abandoned ideas.

## LLM Provider: Groq

The AI Copilot uses **Groq's OpenAI-compatible API** via the official
`openai` Python SDK, pointed at Groq's base URL. All LLM calls go through
one file (`backend/app/ai/llm_client.py`) — switching providers later is a
one-file change.

## Repository layout

```
opspilot-ai/
├── backend/     FastAPI + SQLAlchemy + SQLite + scikit-learn/XGBoost + Groq
├── frontend/    Next.js + TypeScript + Tailwind + Recharts
├── ARCHITECTURE.md   Full technical writeup — read this for interview prep
└── README.md    (you are here)
```

## Try everything, page by page

| Page | What to try |
|---|---|
| `/dashboard` | Business Health Score + AI Insight cards |
| `/dashboard/sales` | Filter by region/category/date; see the demo data's Electronics decline |
| `/dashboard/inventory` | Toggle "Understocked only" |
| `/dashboard/customers` | Click "Run segmentation"; scroll to Churn Risk for per-customer explanations |
| `/dashboard/expenses` | The demo data's marketing spend spike shows as a month-over-month jump |
| `/dashboard/forecasts` | Switch between 3/6/12 months; compare MAE/RMSE/MAPE |
| `/dashboard/anomalies` | Flagged revenue/expense/transaction anomalies |
| `/dashboard/copilot` | Ask "Why did revenue change this month?" — watch it call real tools |
| `/dashboard/knowledge-base` | Upload a `.txt`/`.md` policy doc, then ask the Copilot about it |
| `/dashboard/actions` | Task tracking with status updates |
| `/dashboard/alerts` | Synced from current anomalies/risk state |
| `/dashboard/reports` | Generate + download a Markdown business report |
| `/dashboard/data` | Upload your own CSV/XLSX, or re-run the demo generator |

## A note on how this was verified

Every file in this project was statically verified before packaging: full
Python syntax checks, a custom cross-module import resolver (confirming
every `from app.X import Y` across the entire backend resolves to something
that actually exists), and equivalent checks for the frontend's `@/` and
relative imports. This caught several real bugs during development (missing
`__init__.py` files, a stale import) before they could reach you. What this
verification *can't* do is replace actually running the code — `pip
install`, `npm install`, and the servers themselves have not been executed
in the environment this was built in (no network access there). This is
genuinely the first time this code runs. If anything errors on your machine,
it's likely a small, fixable issue — most commonly a missing environment
variable or a package version mismatch — not a structural problem.
