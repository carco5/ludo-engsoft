# Week 3 · Exercise 2, Part 2 — Josep Coll
"""
Road two — the browser. The course's MCP agent loop, with the Playwright MCP
server of this folder mounted.

This is `week-03/demos/03-mcp-server-minimal/agent_with_mcp.py` with three
changes, all of them about measuring rather than about the loop:
  * a system prompt that tells the agent it drives a browser (the official
    Playwright MCP ships one too);
  * a turn budget, so a small model that starts going in circles stops instead
    of burning the meter forever;
  * a per-call and total token report, so the run is auditable next to the
    LiteLLM log.

The loop itself is unchanged. That is the lesson: only where the tools come
from changed.

    uv run python browser_agent.py "post 'hello from my browser agent' to thread 1"
"""
import asyncio
import json
import os
import sys

from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
    timeout=1800,
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")
MAX_TURNS = int(os.environ.get("MAX_TURNS", "12"))
SERVER = StdioServerParameters(command=sys.executable, args=["playwright_mcp_server.py"])

SYSTEM = (
    "You drive a web browser through tools. Work one step at a time: navigate, "
    "read the snapshot, act on an element by its [ref=eN] handle, then read the "
    "new snapshot to check. To fill a form: browser_type into the textbox, then "
    "browser_click the submit button. When the task is done, answer in plain "
    "text without calling any more tools."
)


def to_openai_tool(t):
    """An MCP tool's registry entry IS an OpenAI tool schema, almost verbatim."""
    return {"type": "function", "function": {
        "name": t.name, "description": t.description or "", "parameters": t.inputSchema}}


async def main(user_prompt):
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            listing = await session.list_tools()
            tools = [to_openai_tool(t) for t in listing.tools]
            print("── the MCP registry the model receives ──")
            for t in tools:
                print(f"  tool: {t['function']['name']}  —  {t['function']['description'][:80]}...")
            print(f"  registry size on the wire: {len(json.dumps(tools))} chars\n")

            messages = [{"role": "system", "content": SYSTEM},
                        {"role": "user", "content": user_prompt}]
            total_prompt = total_completion = 0
            for turn in range(1, MAX_TURNS + 1):
                resp = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
                u = resp.usage
                total_prompt += u.prompt_tokens
                total_completion += u.completion_tokens
                print(f"── call #{turn}: prompt_tokens={u.prompt_tokens} "
                      f"completion_tokens={u.completion_tokens}", flush=True)
                msg = resp.choices[0].message
                messages.append(msg.model_dump(exclude_none=True))
                if not msg.tool_calls:
                    print(f"✅ {msg.content}")
                    break
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    print(f"  → MCP call: {tc.function.name}({args})", flush=True)
                    result = await session.call_tool(tc.function.name, args)
                    text = "".join(getattr(c, "text", "") for c in result.content)
                    print(f"  ← MCP result: {len(text)} chars")
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})
            else:
                print(f"⛔ stopped: hit the {MAX_TURNS}-turn budget")

            print(f"\nTOTAL prompt_tokens={total_prompt} completion_tokens={total_completion} "
                  f"total={total_prompt + total_completion}")


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or (
        "Open http://localhost:6673/thread/1 and post the comment "
        "'hello from my browser agent' in the comment form on that page.")
    asyncio.run(main(prompt))
