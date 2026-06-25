"""Smoke test — exercises the tools directly against a running backend.

    python smoke_test.py          # needs the backend up (docker compose up)

Calls the underlying tool coroutines (FastMCP's @tool decorator returns the
function unchanged), so no MCP transport is needed.
"""
import asyncio

import server


async def main() -> None:
    tools = await server.mcp.list_tools()
    print(f"registered tools ({len(tools)}): " + ", ".join(t.name for t in tools))

    print("\nhealth:", await server.health())
    stores = await server.list_stores()
    print("stores:", [s.get("key") for s in stores.get("stores", [])])

    print("\nlogin:", await server.login())          # admin / admin123
    dash = await server.get_dashboard("fur")
    print("dashboard kpis:", dash.get("kpis"))

    chat = await server.chat_concierge("有什么推荐的冬季款？", store="luxefur")
    print("concierge reply:", str(chat.get("reply"))[:120], "...")

    await server._client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
