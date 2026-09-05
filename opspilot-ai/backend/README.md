# OpsPilot AI — Backend (Phase 1)

FastAPI backend. No Docker, no Postgres, no Redis — SQLite + in-process
background tasks, by design (see project root README for why).

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Visit:
- http://localhost:8000/ — root message
- http://localhost:8000/docs — interactive API docs (Swagger)
- http://localhost:8000/api/v1/health — health check (confirms DB connection)

The SQLite database file is created automatically at `backend/data/opspilot.db`
on first run — nothing to install or configure.

## Groq API key

The AI Copilot (built in Phase 8) uses Groq's OpenAI-compatible API. Get a
free key at https://console.groq.com/keys and put it in `.env` as
`GROQ_API_KEY`. Not required for Phases 1-7.

## Project layout

See `/ARCHITECTURE.md` at the project root for the full folder-by-folder
explanation. In short: `api/` = HTTP routes, `services/` = business logic,
`models/` = database tables, `schemas/` = request/response validation,
`ai/` = LLM + tool-calling, `ml/` = forecasting/churn/anomaly models.
