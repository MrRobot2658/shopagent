"""Deterministic, context-aware mock AI provider.

No external calls, no API key. Responses are routed by simple keyword intent
detection and filled with real data from the seeded store/product context, so
the demo feels alive. Output is streamed word-by-word to mimic a live model.
"""
from __future__ import annotations

import asyncio
import re
from typing import AsyncIterator

from .. import config, data


def _last_user(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return (m.get("content") or "").strip()
    return ""


def _has(text: str, *words: str) -> bool:
    t = text.lower()
    return any(w in t for w in words)


class MockProvider:
    # ------------------------------------------------------------- chat ----
    async def stream_chat(self, surface, store, messages) -> AsyncIterator[str]:
        text = self._reply(surface, store, messages)
        # Stream in word-sized chunks, keeping whitespace, to look like typing.
        for chunk in re.findall(r"\S+\s*", text):
            yield chunk
            if config.STREAM_DELAY:
                await asyncio.sleep(config.STREAM_DELAY)

    def _reply(self, surface, store, messages) -> str:
        q = _last_user(messages)
        if surface == "copilot":
            return self._copilot_reply(store, q)
        return self._store_reply(store, q)

    # -- shopper-facing concierge ------------------------------------------
    def _store_reply(self, store, q: str) -> str:
        name = (store or {}).get("name", "our store")
        prods = data.list_products((store or {}).get("key")) if store else []
        if not q:
            return f"Welcome to {name}! How can I help — sizing, shipping, care tips, or a product recommendation?"

        if _has(q, "ship", "delivery", "deliver", "国际", "运费", "物流"):
            return (
                f"Yes — {name} ships worldwide. Standard delivery is 3–8 business days "
                f"with full tracking, covering US / EU / JP and the Middle East. "
                f"Orders over $500 ship free, and duties are calculated at checkout."
            )
        if _has(q, "size", "fit", "尺码", "尺寸", "size chart"):
            return (
                "Our pieces run true to size. Tell me your usual size and height and I'll "
                "recommend the best fit — or share your measurements and I'll map them to our size chart."
            )
        if _has(q, "care", "clean", "wash", "保养", "清洗", "store", "存储"):
            kb = (store or {}).get("knowledge_base", "our care guide")
            return (
                f"Great question. Based on our {kb}: keep items away from direct heat, use a "
                "breathable garment bag for storage, and avoid compressing them. Want the full care sheet emailed to you?"
            )
        if _has(q, "return", "refund", "exchange", "退货", "退款", "换货"):
            return (
                "Returns are easy: 30-day window, free return label, refund within 5 business days of receipt. "
                "Would you like me to start a return for a recent order?"
            )
        if _has(q, "recommend", "suggest", "best", "popular", "推荐", "热卖") or _has(q, "price", "cost", "多少钱"):
            if prods:
                top = prods[:3]
                lines = "\n".join(f"• {p['emoji']} {p['name']} — ${p['price']:,} ({p['desc']})" for p in top)
                return f"Here are a few favorites at {name}:\n{lines}\nWant details or styling tips on any of these?"
            return "I'd love to recommend something — what occasion or budget are you shopping for?"

        return (
            f"Thanks for reaching out to {name}! I can help with product recommendations, sizing, "
            "shipping, care, and returns. What would you like to know?"
        )

    # -- admin operator copilot --------------------------------------------
    def _copilot_reply(self, store, q: str) -> str:
        s = store or (data.list_stores()[0])
        k = s.get("kpis", {})
        name = s.get("name", "店铺")
        if not q:
            return "我是你的运营副驾。可以问我：GMV/转化汇总、客户分层圈选、AI 文案/修图、订单与物流。"

        if _has(q, "gmv", "revenue", "营收", "转化", "cvr", "汇总", "今天", "销售"):
            return (
                f"【{name} · 今日概览】\n"
                f"• 访客：{k.get('visitors','—')}　• 订单：{k.get('orders','—')}\n"
                f"• GMV：{k.get('revenue','—')}　• 转化率：{k.get('cvr','—')}\n"
                "环比上周 +8.4%，主要由付费社媒带量。建议把预算向 ROAS>3 的广告组倾斜。"
            )
        if _has(q, "客户", "customer", "圈", "分层", "沉睡", "高价值", "segment", "rfm"):
            sleepers = [c for c in data.list_customers(s["key"]) if c["tier"] in ("沉睡", "高价值")]
            names = "、".join(c["name"] for c in sleepers) or "暂无"
            return (
                f"已按 RFM 圈出 {len(sleepers)} 位「高价值/沉睡」客户：{names}。\n"
                "可一键导出到 Meta / Google 做再营销受众，或触发挽回 EDM。需要我现在生成受众包吗？"
            )
        if _has(q, "文案", "content", "描述", "博文", "seo", "邮件", "social", "edm"):
            return (
                "AI 内容已就绪：产品描述（8 国语言）、SEO 博文、社媒文案、EDM 模板都能一键生成。\n"
                "告诉我品类与卖点，我直接产出英文 SEO 描述，并给出 Instagram/TikTok 配套文案。"
            )
        if _has(q, "图", "image", "修图", "场景", "去背景", "视频"):
            return (
                f"修图流水线在线：去背景 → 场景替换（本店默认「{s.get('scene','雪天')}」）→ 4K 增强 → 短视频。\n"
                "上传一张手机图，我就能批量产出电商级主图与 TikTok 素材，成本约 $0.02–0.10/张。"
            )
        if _has(q, "订单", "order", "物流", "发货", "退款"):
            orders = data.list_orders(s["key"])[:3]
            lines = "\n".join(f"• {o['id']} · {o['customer']} · ${o['total']:,} · {o['status']}" for o in orders)
            return f"【{name} · 最新订单】\n{lines}\n需要我筛选待处理/异常订单，或导出对账单吗？"

        return (
            f"收到：「{q}」。我可以汇总经营数据、圈选客户、生成内容/修图、处理订单。"
            "试试「汇总今天的 GMV 和转化」或「圈出沉睡的高价值客户」。"
        )

    # --------------------------------------------------------- content ----
    async def generate_content(self, kind, store, language, params) -> str:
        name = (store or {}).get("name", "the brand")
        cat = params.get("category") or params.get("品类") or "Premium Product"
        mat = params.get("material") or params.get("材质") or "premium materials"
        kw = params.get("keywords") or cat
        await asyncio.sleep(0.2)
        if kind == "seo_blog":
            return (
                f"# {kw}: The 2026 Buyer's Guide\n\n"
                f"Looking for the perfect {cat}? At {name}, craftsmanship meets value. "
                f"In this guide we cover how to choose, style, and care for your {cat} made from {mat}…\n\n"
                "## Why it matters\n…\n## How to choose\n…\n## Care & longevity\n…"
            )
        if kind == "social":
            cat_tag = re.sub(r"\s+", "", cat)
            name_tag = name.replace(" ", "")
            return (
                f"✨ New drop alert ✨ Meet the {cat} from {name} — crafted in {mat}. "
                f"Tap to shop 🛍️\n#{cat_tag} #{name_tag} #NewArrival #ShopNow"
            )
        if kind == "edm":
            return (
                f"Subject: Your {cat} is waiting 🎁\n\nHi there,\n\nWe noticed you loved our {cat}. "
                f"Made from {mat}, it's a {name} favorite — and it's almost gone. "
                "Complete your order in the next 24h for free shipping.\n\n— The "
                f"{name} Team"
            )
        # product_desc (default)
        return (
            f"{cat} — {name}\n\n"
            f"Elevate your wardrobe with this {cat}, expertly crafted from {mat}. "
            "Designed for everyday luxury with a tailored silhouette, durable construction, "
            f"and timeless style. ({language})\n\n"
            "• Material: " + mat + "\n• Free worldwide shipping over $500\n• 30-day easy returns"
        )

    # ----------------------------------------------------------- image ----
    async def generate_image(self, store, operation, scene, source) -> dict:
        await asyncio.sleep(0.4)
        labels = {
            "bg_remove": "背景去除",
            "scene_swap": f"场景替换 → {scene}",
            "upscale": "4K 画质增强",
            "video": "3 秒动态视频",
        }
        return {
            "operation": operation,
            "label": labels.get(operation, operation),
            "scene": scene,
            "source": source or "phone-photo.jpg",
            # In mock mode we return a deterministic placeholder, not a real asset.
            "result_url": f"https://placehold.co/800x800/0f172a/c9a86c?text={scene}",
            "cost_usd": round(0.06, 2),
            "status": "done",
            "note": "Mock 生成结果（占位图）。接入真实模型后此处返回生成图 URL。",
        }
