# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **static marketing/demo site** for "Shops Agent" — an AI-driven DTC cross-border e-commerce platform pitched at the 2026 皮草产业展 (fur expo). There is **no build step, no framework, no package.json, no tests**. Every page is hand-written HTML + vanilla CSS + a small vanilla JS file, served as-is by Vercel.

The two PDFs at the repo root are the **product spec / source of truth** for content and visual mockups:
- `ShopsAgent_产品介绍和案例展示.pdf` — full product intro, the Admin Dashboard mockup, and the three Live Demo store designs.
- `ShopsAgent_全栈DTC平台_皮草展.pdf` — the fur-expo pitch deck.

To read a PDF's text: `python3 -c "import pdfplumber; [print(p.extract_text()) for p in pdfplumber.open('FILE.pdf').pages]" 2>/dev/null` (suppress the harmless FontBBox warnings on stderr). When asked to build something "按照文档" (per the docs), the spec lives in these PDFs.

## Commands

Local preview (no tooling required):
```bash
python3 -m http.server 8099    # then open http://localhost:8099/<page>/
```

Screenshot a page to verify rendering (macOS, headless Chrome):
```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --hide-scrollbars --window-size=1440,1900 \
  --screenshot="/tmp/shot.png" "http://localhost:8099/admin/"
```
Note: section/page switching in `/admin` is JS-click driven, not hash-routed — a `#stores` URL will not pre-activate a section. To screenshot a non-default admin section, temporarily swap the `is-active` class onto the target `.page` in a throwaway copy.

Deploy: Vercel (static), project `shopagentv2` (URL `shopagentv2.vercel.app`). `vercel.json` sets `cleanUrls: true`, so `/admin` resolves to `admin/index.html`, `/home` → `home/index.html`, etc. Root `/` redirects to `/home` (the 官网); `/fur-expo` redirects to `/home` for backward compat. There is no project-level `installCommand`/`buildCommand`. SSO/deployment protection is disabled so the demo is publicly reachable.

## Architecture

Each top-level directory is **one self-contained page** with its own `assets/{css,js}`:

- `home/` — `/home`, the **Shops Agent 官网** (platform marketing landing) and the site homepage (root `/` redirects here). Its `#demos` section is the demo-stores hub; each card links to a store landing page. (Formerly `fur-expo/`.)
- `luxefur/`, `pawmaison/`, `cupid-sport/` — the three **demo store landing pages** (Kith / Wild One / Ten Thousand-inspired). Each is self-contained with its own brand `style.css`, a mobile nav, and a floating bottom-right AI chatbot widget. Built per the Live Demo designs in the product PDF.
- `admin/` — `/admin`, a TailAdmin-style **single-page admin console**. The sidebar's 11 modules (Dashboard, 店铺 Stores, Orders, Customers, AI Content, AI Images, Chatbot, Platforms, Payments, ERP, Settings) map to PDF modules; the 店铺 Stores section is the front-end-preview hub (each tile's "前端预览" → a store page). Top-right has a 🌐 官网 link and a store switcher; an always-on floating Copilot widget sits bottom-right. All data is hardcoded mock content.

Key conventions to preserve when editing or adding pages:

- **No shared CSS bundle.** Every page directory has its own `assets/css/style.css` (admin: `admin.css`). The platform pages (`home/`, `admin/`) share design tokens: primary `#0f172a`, accent gold `#c9a86c`, sidebar `#0b1120`. The three demo stores each define their own distinct brand palette — do not force them onto the platform tokens.
- **Admin section switching** (`admin/assets/js/admin.js`): any element with `data-target="<x>"` shows `#page-<x>` and toggles the matching `.nav-item`. Every `data-target` must have a corresponding `#page-*` section. The store switcher (`#storeSelect`) drives per-store mock KPIs/chart from the `STORES` object and re-renders the CSS-bar revenue chart.
- **All links — cross-page and asset — are absolute, clean-URL paths** (`/home`, `/admin/assets/css/admin.css`), relying on `cleanUrls`. Do NOT use relative asset paths (`assets/...`): with `cleanUrls` the canonical page URL has no trailing slash (e.g. `/admin`), so a relative `assets/...` resolves to `/assets/...` (404) instead of `/admin/assets/...`.
- **Front-end preview wiring**: the admin "店铺 Stores" section is the preview hub — each store tile's "前端预览" button links to that store's public landing page (`/luxefur`, `/pawmaison`, `/cupid-sport`). The 官网 `home/#demos` cards also link out to the same three pages. All three stores are live.
