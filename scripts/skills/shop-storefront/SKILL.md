---
name: shop-storefront
description: 以买家视角浏览 Shops Agent 店铺、咨询导购、下演示订单。当用户想看某店铺有哪些商品、要导购推荐、比价选品，或要走通下单/结账流程时使用。这些是公开能力，无需登录。依赖 shops-agent MCP 服务。
---

# Shops Agent — 门店选购

用 `shops-agent` MCP 工具走通买家侧链路（公开，无需 `login`）。

## 浏览选品
1. `list_stores` 看有哪些店铺（key/slug、品类、品牌）。
2. `get_products(store)` 列出某店铺商品（id、名称、价格等）。
3. 需要推荐就调 `chat_concierge(message, store, history)`——面向买家的导购助手，
   返回 `{"reply": ...}`；多轮对话把历史放进 `history`
   （`[{"role":"user"|"assistant","content":"..."}]`）。

## 下单 `place_order`
- `store`：店铺 key 或 slug。
- `items`：`[{"id": "<product_id>", "qty": 2}]`，`id` 必须来自 `get_products` 的真实商品。
- `customer` / `country` 可选。
- 返回 `{"order", "confirmation", "message"}`。

流程：先 `get_products` 拿到合法商品 id → 跟用户确认商品与数量 → `place_order` →
回报确认号。下单前务必确认，这是写入操作（即使是演示数据）。

## 注意
- 全程公开，不要为此调用 `login`。
- 数据为演示用；下单是 mock checkout，不产生真实交易。
