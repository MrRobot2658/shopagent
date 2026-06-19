# Shops Agent — Backend (FastAPI)

Real backend for the demo: AI chat (store concierge + admin Copilot), data APIs
(stores / products / orders / customers / dashboard), AI content & image
generation, a checkout flow, and **admin login**. Data is in **PostgreSQL**,
login **sessions in Redis**. AI is **mock by default** (no API key) and swappable
for real Claude later.

## Run (Docker — four services)

```bash
docker compose up --build        # from the repo root
```

| Service | What | Host URL / port |
|---|---|---|
| `frontend` | nginx — static site + reverse-proxy `/api/` → backend | **http://localhost:8090** |
| `backend`  | FastAPI/uvicorn — API only | **http://localhost:8091** |
| `db`       | PostgreSQL 16 (volume `pgdata`) | localhost:5433 |
| `redis`    | Redis 7 (sessions) | localhost:6380 |

Open **http://localhost:8090** — the full site talking to a live backend through
nginx. The admin page (`/admin`) shows a **login overlay**; sign in with the seed
account **`admin` / `admin123`**. After login the Copilot streams replies and the
dashboard/orders/customers load from Postgres.

Host ports are 8090/8091/5433/6380 because 8000/5432/6379 are occupied locally.
`backend/app` and the static site hot-reload via mounted volumes; `db` persists
in the `pgdata` volume; `frontend/nginx.conf` is baked into the image (rebuild to
change). Tables are created + seeded on first boot (idempotent).

## Auth (Redis sessions)

`POST /api/auth/login {username,password}` → verifies against the `users` table,
creates a session in Redis (`sess:<token>`, TTL `SESSION_TTL`), sets an httponly
cookie `sa_session`. `POST /api/auth/logout` clears it; `GET /api/auth/me` returns
the current user. Passwords are PBKDF2-HMAC-SHA256 (stdlib).

**Public:** store chat (`surface:store`), `/api/products`, `/api/checkout`.
**Login-required (401):** `/api/dashboard`, `/api/customers`, `/api/orders`,
Copilot chat (`surface:copilot`), `/api/ai/content`, `/api/ai/image`.

## Run (without Docker)

Needs local Postgres + Redis reachable via env (otherwise just use `docker compose`):

```bash
cd backend && pip install -r requirements.txt
export DATABASE_URL="postgresql+asyncpg://shopagent:shopagent@localhost:5433/shopagent"
export REDIS_URL="redis://localhost:6380/0"
STATIC_ROOT=.. uvicorn app.main:app --reload --port 8091
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/api/health` | health + active AI provider |
| POST | `/api/auth/login` · `/logout` · GET `/me` | login (sets `sa_session` cookie) / logout / current user |
| POST | `/api/chat` | chat; `surface` = `store` (public) \| `copilot` (login); SSE stream unless `stream:false` |
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
  main.py            # app, CORS, routers, lifespan (init_db), static-site serving
  config.py          # env-driven settings (DATABASE_URL, REDIS_URL, ADMIN_*, AI_*)
  data.py            # seed constants + sync accessors (used by the mock AI flavor text)
  schemas.py         # pydantic request models
  auth.py            # PBKDF2 hashing + Redis sessions + FastAPI deps
  db/{models,session,seed}.py   # SQLAlchemy 2.0 async ORM, engine, startup seed
  ai/{base,mock,claude}.py      # pluggable AI provider
  routers/{auth,chat,catalog,orders,ai_gen}.py
```

> Data APIs read/write **PostgreSQL**; the mock AI's canned summaries read the
> seed constants in `data.py` (it's mock text). Run without Docker only if you
> have local Postgres+Redis — set `DATABASE_URL` / `REDIS_URL` accordingly;
> otherwise use `docker compose`.

The frontend talks to the backend via the shared `/shared/chat.js` client and
`fetch('/api/...')` calls in `admin.js`. All calls **degrade gracefully** when
the backend is offline, so the static Vercel deploy keeps working unchanged.
Point the static site at a remote backend by setting `window.SHOPAGENT_API`.
