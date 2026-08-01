# Week 3 · Exercise 2, Part 2 — Josep Coll
"""
Smoke test for the Playwright MCP server — no LLM involved.

Connects over stdio, prints the registry the model would receive (and its size
on the wire), then navigates to the forum thread and prints the snapshot. Use it
to check the server before spending model time on it, and to see with your own
eyes what the browser road pays for on every single step.

    uv run python smoke_browser.py
"""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=["playwright_mcp_server.py"])
URL = "http://localhost:6673/thread/1"


async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            tools = [{"type": "function", "function": {
                "name": t.name, "description": t.description or "",
                "parameters": t.inputSchema}} for t in listing.tools]
            print("registry chars:", len(json.dumps(tools)),
                  "tools:", [t.name for t in listing.tools])
            res = await session.call_tool("browser_navigate", {"url": URL})
            snap = "".join(getattr(c, "text", "") for c in res.content)
            print(f"--- snapshot ({len(snap)} chars) ---")
            print(snap)


asyncio.run(main())
