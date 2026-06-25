---
name: shop-insights
description: 拉取 Shops Agent 某店铺的经营数据并生成业绩洞察报告（KPI、收入趋势、订单、客户分层）。当用户想看店铺表现、销售/收入情况、订单与客户分析、或要一份运营报告时使用。依赖 shops-agent MCP 服务。
---

# Shops Agent — 经营洞察

用 `shops-agent` MCP 工具汇总一个店铺的经营数据，产出结构化业绩报告。

## 前置
- 后端在运行（`docker compose up`，默认 http://localhost:8091）。
- 这些工具需要登录，先调用 `login`（默认 `admin` / `admin123`）。

## 步骤
1. 调用 `login`（除非本会话已登录）。
2. 确定店铺 `store`：key 用 `fur`/`pet`/`sport`，slug 用 `luxefur`/`pawmaison`/`cupid-sport`。
   不确定就先 `list_stores` 让用户选。
3. 并行拉取：
   - `get_dashboard(store)` → KPI、`revenue_series`(10 周)、近期订单。
   - `get_orders(store)` → 全量订单（状态、金额、国家分布）。
   - `get_customers(store)` → 客户与 RFM `tier`（可加 `tier` 过滤高价值客户）。
4. 综合输出一份简报：
   - **概览**：核心 KPI + 同比/环比口径（数据是 mock，注明）。
   - **收入趋势**：根据 `revenue_series` 描述走势（上升/回落/拐点）。
   - **订单**：总量、客单价、按国家/状态拆分。
   - **客户**：分层占比，点名高价值（如 `tier` 为高的）客户。
   - **建议**：2–3 条可执行运营动作。

## 注意
- 数据为演示用 mock，报告中需说明，不要当真实经营数字下结论。
- 报告用中文，简洁、要点优先；数字用表格或要点呈现。
