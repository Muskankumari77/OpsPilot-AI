# OpsPilot AI — Frontend (Phase 1)

Next.js (App Router) + TypeScript + Tailwind.

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit http://localhost:3000 — the page pings the backend's `/health`
endpoint and shows the connection status, confirming both servers talk to
each other.

Start the backend first (`cd ../backend && uvicorn app.main:app --reload`)
so the health check has something to reach.
