# Architecture

## Layers (backend)

```
api/        HTTP routes only — parse request, call a service, return response
services/   Business logic lives here, not in routes or models
models/     SQLAlchemy tables
schemas/    Pydantic request/response validation
ai/         LLM client, tool-calling schemas, orchestrator
ml/         Forecasting, churn, segmentation, anomaly models
rag/        Chunking, embedding storage, retrieval
db/         Engine/session setup, Base metadata
core/       Config, security (JWT/hashing), logging, exceptions
```

Rule of thumb: a route handler should be short — validate input, call one
service method, return the result. If a route starts doing calculations or
touching the database directly, that logic belongs in `services/`.

## Data flow (typical request)

```
Frontend (Next.js)
      │  fetch() with JWT in Authorization header
      ▼
FastAPI route (api/v1/*.py)
      │  depends on get_current_user, get_db
      ▼
Service (services/*.py)
      │  business logic, organization_id filtering
      ▼
SQLAlchemy model → SQLite
```

## AI Copilot flow (Phase 8+)

```
User question
      ▼
Copilot service (ai/copilot_service.py)
      ▼
LLM (Groq, via ai/llm_client.py) decides which tool to call
      ▼
Tool function (ai/tools/*.py) — thin wrapper around a real service call,
      always scoped to the user's organization_id
      ▼
Real data returned to the LLM
      ▼
LLM composes a final answer grounded in that real data
      ▼
Response shown to user
```

The LLM never has direct database access and never invents numbers — every
figure it states came back from a tool call first. This is enforced in code
(the tool layer only exposes specific, organization-scoped functions), not
just requested via prompt.

## Auth & RBAC (Phase 2)

- **Tokens:** JWT access token only (`sub` = user id), no refresh-token
  rotation — documented below as a future improvement.
- **Organization context:** the frontend sends `X-Organization-Id` on every
  request once a user is in more than one org; if omitted, the backend
  falls back to the user's first organization (`get_default_membership`).
- **Roles:** `admin`, `manager`, `viewer`, stored per-user-per-organization
  on `OrganizationMember` (a user can hold different roles in different
  organizations).
- **Enforcement:** `require_role(...)` in `api/deps.py` is a dependency
  factory — routes declare which roles they accept and FastAPI rejects
  everyone else with a 403 before the route body ever runs. This is not a
  prompt-level or UI-level check; it's enforced in the request pipeline.
- **Frontend token storage:** a non-httpOnly cookie (`lib/auth.ts`), read by
  both client code (for the Authorization header) and `middleware.ts` (to
  gate `/dashboard` and `/admin` routes). This is the lean-build tradeoff —
  see "Future improvements" below.

## Database

SQLite for now — a single file at `backend/data/opspilot.db`. Every
organization-owned table includes an `organization_id` foreign key, and
every service method that queries those tables filters by it. That's the
multi-tenancy boundary; it's enforced in `services/`, not left to chance in
route handlers.

### Domain tables (Phase 3)

`Product`, `Customer`, `Inventory`, `Expense` are straightforward one-row-
per-entity tables. `Sale` is a **denormalized fact table** — one row per
line item sold, with `category` and `region` copied from Product/Customer
at write time. This intentionally collapses what the original spec lists as
three separate tables (`orders`, `order_items`, `sales`) into one, because
OpsPilot is an analytics platform, not an order-management system: every
Sales Intelligence query in Phase 5 becomes a single-table scan instead of
a three-way join. `order_number` still groups line items from the same
checkout, so "number of orders" and "average order value" are computable
by grouping, not lost.

## Data ingestion pipeline (Phase 3)

```
Upload (multipart file + dataset_type)
      │
      ▼
Dataset row created, status = "processing"
      │  (response returned to the client immediately)
      ▼
FastAPI BackgroundTask: process_dataset()
      │
      ├─ VALIDATE   — required columns present for this dataset_type?
      ├─ PROFILE    — data_quality_service: missing values, duplicates,
      │               IQR outliers on numeric columns → quality_report
      ├─ CLEAN      — drop exact duplicates, drop rows missing required fields
      ├─ TRANSFORM  — coerce types, resolve product_sku/customer_email
      │               references to real Product/Customer rows
      └─ IMPORT     — insert into Product/Customer/Sale/Inventory/Expense,
                       scoped to organization_id
      │
      ▼
Dataset row updated: status = "completed" | "failed", quality_report, row_count
```

The frontend polls `GET /datasets` every 2s while any dataset is
`processing` (see `components/data/DatasetList.tsx`) — no websockets
needed at this scale.

### Demo data (Phase 3)

`backend/scripts/generate_demo_data.py` seeds an "OpsPilot Demo Co."
organization directly via the ORM (bypassing the upload pipeline, since
it's generating data rather than importing it) with intentional patterns:
a revenue decline concentrated in one category, a churn-shaped customer
gap, understocked inventory, a marketing expense spike, and basic
seasonality. These exist so Phases 6-8's ML and AI features have real
signal to detect and explain, not synthetic noise.

## Domain CRUD (Phase 4)

All five domain routers (`products`, `customers`, `sales`, `inventory`,
`expenses`) follow the same shape:

```
route (api/v1/*.py)       → thin: parse query params, call service, return
service (services/*.py)   → org-scoped query building, validation, writes
schema (schemas/*.py)     → *Create / *Update / *Out, request & response shapes
```

**Pagination** is shared via `utils/pagination.py` (`PageParams` dependency
+ `paginate()` helper) and `schemas/common.py` (`Page[T]` generic response),
so every list endpoint returns the same `{items, total, page, page_size,
total_pages}` shape and accepts the same `?page=&page_size=` params —
implemented once, reused five times.

**RBAC per action:** read is open to any organization member (including
Viewer); create/update require Admin or Manager; delete requires Admin.
This is enforced the same way as Phase 2's org rename — `require_role(...)`
on the route — not re-invented per domain.

**Sales is the one non-trivial service.** A `Sale` row stores denormalized
`region`/`category` and computed `total_amount`/`profit` (see the Database
section above). `sales_service.create_sale()` is the single place that
resolves a manually-entered sale (customer + product + quantity) into that
denormalized shape — the same logic the Phase 3 CSV importer
(`data_ingestion_service.py`) uses for bulk sales uploads, so a sale looks
identical whether it arrived via the API or a spreadsheet.

## Dashboards & aggregation (Phase 5)

Each domain service gained a `get_*_summary()` (and `sales_service` also
`get_sales_trends()`) that runs SQL aggregation — `func.sum`, `func.count`,
`GROUP BY`, `strftime()` date-truncation for time-series grouping — rather
than pulling rows into Python and summing in memory. These endpoints are
read-only and separate from the Phase 4 CRUD list endpoints, since a
paginated list of rows and a "revenue by category" rollup are different
queries with different shapes.

**Period comparisons** ("+12% vs previous period") are computed the same
way everywhere via `utils/dates.py`: `resolve_period()` takes an optional
explicit date range and returns both that range and the equal-length range
immediately before it, so `percent_change(current, previous)` means the
same thing on every dashboard.

**Business Health Score** (`dashboard_service.py`) is a documented
heuristic: four sub-scores — revenue growth, inventory health (% of
products not at Critical/High risk), expense control (penalizes spend
spikes, not savings), and customer growth — each normalized to 0-100, then
averaged. This is intentionally simple and explainable rather than a
trained model; a natural future improvement is replacing it with a model
trained against real business outcomes once there's enough historical data
to validate against. It's a different thing from the ML-driven risk scores
(churn probability, stock-out probability) built in Phase 6 — this score
summarizes the whole business at a glance, those predict specific outcomes.

**Frontend layout:** with five dashboard pages now, a shared
`app/dashboard/layout.tsx` wraps them all with a `Sidebar` (page nav) and
`Topbar` (organization switcher, moved out of the Phase 2 dashboard page
now that it needs to be available from every page, plus logout). Each
domain's summary + list data is fetched via a small hook
(`hooks/useSales.ts`, `useInventory.ts`, etc.) using plain
`useState`/`useEffect` — consistent with `AuthProvider`'s pattern rather
than introducing TanStack Query (already a listed dependency) partway
through; wiring up `providers/QueryProvider.tsx` for caching/refetching is
a reasonable future improvement once the number of dashboard requests
grows enough to matter.

## ML models (Phase 6)

Every model here is **trained fresh on each request**, not persisted or
scheduled — at this data scale (hundreds to low thousands of rows) training
takes well under a second, so a model registry with scheduled retraining
(mentioned in the original spec) would be premature infrastructure for a
lean build. This is called out explicitly as a future improvement once
retraining cost or data volume actually justifies it.

- **Forecasting** (`ml/forecasting/`): a linear-trend baseline and an
  XGBoost lag-feature model are both backtested on a holdout of the last 3
  months; `forecast_service.py` picks whichever has the lower MAPE for the
  actual future forecast. Confidence bounds are ± the holdout residual
  std — a simple, honest interval, not a statistically rigorous prediction
  interval, and documented as such in code.
- **Churn** (`ml/churn/`): a RandomForestClassifier trained on 5 features
  per customer (recency, average purchase interval, total spend, order
  count, average order value). Since there's no ground-truth "did they
  actually churn" label in this data, training uses a bootstrap heuristic
  label (gap since last purchase > 2x their own average interval) — the
  model's output probability is more nuanced than the binary heuristic used
  to teach it, and is genuinely learned, not just the heuristic repeated.
- **Segmentation** (`ml/segmentation/`): RFM (recency/frequency/monetary)
  computed directly from Sale history, clustered via K-Means (k=4), with
  cluster centroids ranked by a combined RFM score to assign human labels
  (VIP/Loyal/New/At Risk) — not an arbitrary cluster index. Triggered
  on-demand via `POST /customers/segment`, writing results onto
  `Customer.segment`.
- **Anomaly detection** (`ml/anomaly/`): z-score on monthly revenue and
  per-category monthly expenses (catches "this month was unusual"), plus
  Isolation Forest on individual recent transactions (catches "this single
  order was unusual" — a multivariate signal a per-column threshold would
  miss). Computed on-demand, not persisted.

## Explainable AI (Phase 7)

`ml/explainability/feature_importance.py` uses the churn model's
`feature_importances_` (global — which features matter most across all
predictions) rather than SHAP, per the lean-build decision in this file's
"Future improvements" section. Worth naming plainly: SHAP computes exact
per-prediction (local) attribution via Shapley values; `feature_importances_`
alone is global only. To still explain individual predictions, each
customer's top factors are computed by combining global importance with how
unusual THIS customer's values are relative to the population — a feature
only surfaces as a top factor if the model considers it generally important
AND this customer is unusual on it. This is a real, honest technique
(comparable to attribution methods that predate SHAP), not SHAP itself, and
the code says so.

## AI Copilot (Phase 8)

```
User message
      │
      ▼
copilot_service.chat() — adds system prompt + history, calls Groq with tools
      │
      ▼
LLM decides: answer directly, OR request one or more tool calls
      │
      ▼ (if tool calls requested)
_execute_tool() — organization_id is bound from the AUTHENTICATED REQUEST,
      never from anything the LLM supplied — this is what makes cross-tenant
      data access structurally impossible, not just prompt-discouraged
      │
      ▼
Tool dispatches to the real service (sales_service, inventory_service, etc.)
      │
      ▼
Real data returned to the LLM as a tool result message
      │
      ▼
LLM composes a final answer grounded in that real data (loop continues up
      to MAX_TOOL_ROUNDS if it needs to call more tools)
```

Five tool files (`ai/tools/*.py`) wrap the existing Phase 4-6 services —
sales, inventory, customers (churn + segments), finance, forecasts — each
exposing an OpenAI-compatible function schema. `llm_client.py` (from Phase
1) already wraps Groq's OpenAI-compatible API, so no new provider-specific
code was needed here — only the tool layer and the loop in
`copilot_service.py`. The system prompt (`ai/prompts/copilot.py`) states the
anti-hallucination rule in plain language as a second layer on top of the
structural one (the LLM literally has no other way to reach the database).

If `GROQ_API_KEY` isn't set, `POST /copilot/chat` returns a clear 503 with
setup instructions rather than a confusing failure — checked before any LLM
call is attempted.

## RAG knowledge base (Phase 9)

```
Upload (.txt/.md) → chunk_text() → embed_text() (HashingVectorizer)
    → stored as DocumentChunk rows (embedding as a JSON float array —
      SQLite's answer to pgvector)
    → search_knowledge_base tool: embeds the query the same way, computes
      cosine similarity against every chunk in the org, returns top matches
    → the Copilot's main LLM call composes the final answer + citation
```

`embed_text()` uses `HashingVectorizer` rather than a neural embedding
model — a real, honest simplification (see the root README's comparison
table): it captures lexical/keyword overlap, not deep semantic similarity,
and needs no fitting/training step, so documents can be embedded
independently as they're uploaded rather than requiring the whole corpus
up front (unlike TF-IDF). Swapping in real embeddings later means changing
only this one function.

## Orchestrator (Phase 10)

`ai/orchestrator.py` sits directly on top of `copilot_service.py`'s
existing tool-calling loop (Phase 8) and adds exactly one thing: mapping
each tool that was actually called back to a business domain (Sales,
Inventory, Customers, Finance, Forecast, Knowledge Base), returned to the
frontend as `domains_involved` and shown as small badges under each Copilot
response. This is the lean-build's answer to the spec's 7-agent Supervisor
architecture — see the root README's comparison table for why: the LLM
already decides which tool(s) a question needs, which is the same "route to
the right specialist" behavior a Supervisor agent would provide, without
seven classes that would all ultimately call the same underlying services.
The "controlled and observable" requirement from the spec is satisfied
directly by the domain badges, not by architectural ceremony.

## Actions, Alerts, Reports (Phase 11)

- **Recommendations** (`recommendation_service.py`) are deliberately
  rule-based, not another ML model — they're derived from outputs that are
  already ML-backed (inventory risk levels from Phase 6, churn
  probabilities from Phase 6/7, anomalies from Phase 6). The intelligence
  lives in those upstream models; this layer turns "Product X is at
  Critical risk" into a concrete "Reorder ~N units" recommendation with a
  priority and confidence score.
- **Actions** (`models/action.py`, `action_service.py`) are a standard task
  CRUD (title, priority, status, owner, due date) that a recommendation can
  be converted into — the API supports this (`POST /actions`); a one-click
  "Create action from this recommendation" button in the UI is a natural
  next addition once recommendations are surfaced more prominently in the
  dashboard.
- **Alerts** (`models/alert.py`, `alert_service.py`) are *synced*, not
  pushed — `sync_alerts()` runs on every `GET /alerts` call, translating
  current anomalies/risk into Alert rows, deduplicated by
  `(organization_id, title)` so repeated syncs don't create duplicates. No
  websockets or notification infrastructure — consistent with the lean-build
  "no Celery/cron" decision from Phase 3 onward.
- **Insights** (`insight_service.py`) are the dashboard's "AI Insight
  cards" (Revenue Alert, Inventory Alert, Customer Alert) — a presentation
  layer over the same anomaly/risk/churn data, not new analytics.
- **Reports** (`report_service.py`) compile the same summary endpoints
  already built in Phase 5-6 into structured sections. Real PDF generation
  would need an extra dependency (e.g. `weasyprint`); instead, the frontend
  exports the report as a downloadable Markdown file via a client-side Blob
  — zero new dependencies, and the user still gets a shareable file. PDF is
  a documented future improvement, not a missing feature pretending to be
  finished.

## Testing (Phase 12)

`backend/tests/unit/` contains pure-logic tests — no database, no running
server, no network — covering the pieces most worth protecting against
silent regressions: password hashing and JWT round-tripping
(`test_security.py`), the period-comparison math every dashboard's "vs
previous period" figure depends on (`test_dates.py`), and the inventory
risk-level heuristic plus the forecasting baseline's trend extrapolation
(`test_ml_logic.py`). Run with `pytest tests/unit -v` from `backend/`. This
is intentionally not exhaustive coverage — consistent with the project's
stated priority of testing the riskiest logic rather than chasing a
coverage percentage.

## Future improvements (documented, not built)

These are legitimate upgrades if this ever needs to scale past a portfolio
project — deliberately deferred, not overlooked:

- **PostgreSQL** — swap `DATABASE_URL`, add `pgvector` for embeddings
- **Docker Compose** — containerize once the app itself is stable
- **Redis + Celery** — needed once background jobs get heavy enough to
  outgrow FastAPI's `BackgroundTasks`
- **Refresh-token rotation + email verification** — needed for a real
  production auth flow
- **httpOnly session cookie** — the current non-httpOnly cookie is readable
  by JS (needed so client code can attach the Authorization header without
  a backend session store); a production version would exchange it for a
  server-set httpOnly cookie plus a same-site API proxy
- **SHAP** — richer explanations than `feature_importances_` if the model
  choice ever demands it
- **CI/CD (GitHub Actions)** — once there's a test suite worth automating
- **Neural embeddings** (sentence-transformers or an embeddings API) —
  richer semantic search than HashingVectorizer once the knowledge base
  grows beyond a handful of short documents
- **PDF report export** (e.g. `weasyprint`) — Markdown export covers the
  "get a shareable file" need today without the dependency
- **Multi-agent framework** — the orchestrator's domain-labeling approach
  covers observability today; a true Supervisor + specialist-agent
  architecture would matter if specialists ever needed genuinely different
  reasoning strategies rather than just different tool access
- **Scheduled model retraining** — every ML model (forecast, churn,
  segmentation, anomaly) currently trains fresh per request; a model
  registry with scheduled retraining matters once data volume makes
  per-request training too slow
- **Broader test coverage** — `tests/unit/` covers the riskiest pure logic;
  API-level integration tests (with a test database) and frontend
  component tests are the natural next layer
