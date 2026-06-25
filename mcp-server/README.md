# Shops Agent — MCP server

An [MCP](https://modelcontextprotocol.io) server that exposes the Shops Agent
platform as agent-callable **tools**. It's a thin HTTP client of the FastAPI
backend (every tool → `/api/...`), so it runs anywhere it can reach the backend
and needs no DB/Redis of its own.

## Tools (核心 skill)

| Tool | Auth | Purpose |
|---|---|---|
| `health` | public | backend health + active AI provider |
| `login` / `whoami` | public | open an admin session (default `admin`/`admin123`), check current user |
| `list_stores` | public | list demo stores |
| `get_products` | public | product catalog (optional `store`) |
| `chat_concierge` | public | shopper-facing store concierge |
| `place_order` | public | demo checkout |
| `get_dashboard` | **login** | KPIs, revenue series, recent orders |
| `get_customers` | **login** | customers (filter by `store` / RFM `tier`) |
| `get_orders` | **login** | order list |
| `chat_copilot` | **login** | admin operator Copilot |
| `generate_content` | **login** | marketing copy (`product_desc`/`seo_blog`/`social`/`edm`) |
| `generate_image` | **login** | image op (`bg_remove`/`scene_swap`/`upscale`/`video`) |

The login cookie persists for the server process, so call `login` once and the
login-required tools unlock. `store` accepts the admin key (`fur`/`pet`/`sport`)
or the public slug (`luxefur`/`pawmaison`/`cupid-sport`).

## Setup

```bash
cd mcp-server
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

The backend must be reachable. Start it (from the repo root):

```bash
docker compose up --build        # backend on http://localhost:8091
```

## Run

```bash
SHOPAGENT_API=http://localhost:8091 python server.py   # stdio transport
```

| Env | Default | Meaning |
|---|---|---|
| `SHOPAGENT_API` | `http://localhost:8091` | backend origin (server appends `/api/...`); use `:8090` for the nginx front, or a remote URL |
| `SHOPAGENT_TIMEOUT` | `60` | per-request timeout (seconds) |

## Register with Claude Code

From the repo root:

```bash
claude mcp add shops-agent \
  -e SHOPAGENT_API=http://localhost:8091 \
  -- python3 /Users/lei26/Downloads/shopagent/mcp-server/server.py
```

Or commit a project-scoped `.mcp.json` at the repo root (see `mcp.example.json`
in this folder).

## Smoke test

```bash
python smoke_test.py        # lists tools + exercises a public + a login tool
```
