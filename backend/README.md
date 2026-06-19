# Shops Agent — Backend (FastAPI)

Real backend for the demo: AI chat (store concierge + admin Copilot), data APIs
(stores / products / orders / customers / dashboard), AI content & image
generation, and a checkout flow. AI is **mock by default** (no API key) and
swappable for real Claude later.

## Run (Docker — two services)

```bash
docker compose up --build        # from the repo root
```

Two containers come up:

| Service | What | URL |
|---|---|---|
| `frontend` | nginx — serves the static site + reverse-proxies `/api/` to the backend | **http://localhost:8090** |
| `backend`  | FastAPI/uvicorn — API only | **http://localhost:8091** (direct API access) |

Open **http://localhost:8090** — the full site (官网 / admin / demo stores) talking
to a live backend through nginx. The chatbots and Copilot stream real responses;
the admin dashboard hydrates KPIs from `/api/dashboard`.

Ports are 8090/8091 because host 8000 is occupied by an unrelated local app.
`backend/app` (API code) and the static site hot-reload via mounted volumes;
`frontend/nginx.conf` is **baked into the image** — rebuild (`docker compose up
--build`) after changing it.

## Run (without Docker)

```bash
cd backend && pip install -r requirements.txt
STATIC_ROOT=.. uvicorn app.main:app --reload --port 8090
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/api/health` | health + active AI provider |
| POST | `/api/chat` | chat; `surface` = `store` \| `copilot`; SSE stream unless `stream:false` |
| GET  | `/api/stores` · `/api/stores/{key}` | store list / detail (+products) |
| GET  | `/api/products?store=` | product catalog |
| GET  | `/api/customers?store=&tier=` | customers (RFM tiers) |
| GET  | `/api/dashboard?store=` | KPIs, revenue series, recent orders |
| GET  | `/api/orders?store=` | order list |
| POST | `/api/checkout` | place an order `{store, customer, items:[{id,qty}]}` |
| POST | `/api/ai/content` | generate copy (`product_desc`/`seo_blog`/`social`/`edm`) |
| POST | `/api/ai/image` | image op (`bg_remove`/`scene_swap`/`upscale`/`video`) |

`store` accepts either the admin key (`fur`/`pet`/`sport`) or the public slug
(`luxefur`/`pawmaison`/`cupid-sport`).

## Switching mock → real Claude

1. Uncomment `anthropic` in `requirements.txt`.
2. Set env: `AI_PROVIDER=claude`, `ANTHROPIC_API_KEY=...` (optionally
   `ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL` for the Vercel AI Gateway).
3. Rebuild. The factory in `app/ai/base.py` auto-selects the provider and falls
   back to mock if the key/SDK is missing. Only chat is wired to the live model;
   content/image still use the mock templates.

## Layout

```
backend/app/
  main.py            # app, CORS, routers, static-site serving (cleanUrls)
  config.py          # env-driven settings
  data.py            # in-memory seed data + accessors (resets on restart)
  schemas.py         # pydantic request models
  ai/{base,mock,claude}.py   # pluggable AI provider
  routers/{chat,catalog,orders,ai_gen}.py
```

The frontend talks to the backend via the shared `/shared/chat.js` client and
`fetch('/api/...')` calls in `admin.js`. All calls **degrade gracefully** when
the backend is offline, so the static Vercel deploy keeps working unchanged.
Point the static site at a remote backend by setting `window.SHOPAGENT_API`.
