# Week 3 · Exercise 2, Part 2 — Josep Coll
"""
Price the two things the browser road pays for, in tokens, on this machine.

Sends the browser agent's FIRST request three ways — with the registry, without
it, and with one page snapshot appended — and prints the difference. Those two
numbers are what you multiply if you want to know what the same run would cost
against the official ~20-tool Playwright MCP, or against a real page.

    uv run python registry_cost.py
"""
import asyncio
import json
import os
import sys

from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import browser_agent as ba

client = OpenAI(base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:4000/v1"),
                api_key=os.environ.get("OPENAI_API_KEY", "sk-anything"), timeout=1800)
MODEL = os.environ.get("MODEL", "qwen2.5:7b")
SERVER = StdioServerParameters(command=sys.executable, args=["playwright_mcp_server.py"])
TASK = ("Open http://localhost:6673/thread/1 and post the comment "
        "'hello from my browser agent' in the comment form on that page.")


def cost(messages, tools=None):
    kw = {"tools": tools} if tools else {}
    r = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=1, **kw)
    return r.usage.prompt_tokens


async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            tools = [ba.to_openai_tool(t) for t in listing.tools]
            res = await session.call_tool("browser_navigate",
                                          {"url": "http://localhost:6673/thread/1"})
            snap = "".join(getattr(c, "text", "") for c in res.content)

    base = [{"role": "system", "content": ba.SYSTEM}, {"role": "user", "content": TASK}]
    no_tools = cost(base)
    with_tools = cost(base, tools)
    plus_snap = cost(base + [{"role": "user", "content": snap}], tools)

    print(f"tools advertised          : {len(tools)}  ({len(json.dumps(tools))} chars on the wire)")
    print(f"prompt, no tools          : {no_tools}")
    print(f"prompt, with the registry : {with_tools}")
    print(f"  -> THE REGISTRY COSTS   : {with_tools - no_tools} tokens, in EVERY request")
    print(f"snapshot of my forum page : {len(snap)} chars")
    print(f"  -> ONE SNAPSHOT COSTS   : {plus_snap - with_tools} tokens, and it stays in the context")


asyncio.run(main())
