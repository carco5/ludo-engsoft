# Week 3 · Exercise 2, Part 1 — Josep Coll
"""
Control run: the same question, the same model, NO tools field at all.

The exercise's baseline is the plain loop — but that loop already carries two
hand-written tool schemas (wget, execute_sql) and a system prompt, so the
difference "baseline vs MCP" mixes two registries together. This run gives the
floor: what the question alone costs. With it, the MCP registry can be priced
exactly instead of "roughly".

    uv run python control_no_tools.py "what is the capital of France?"
"""
import os
import sys

from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.environ.get("OPENAI_API_KEY", "ollama"),
    timeout=900,
)
MODEL = os.environ.get("MODEL", "qwen3:1.7b")

prompt = " ".join(sys.argv[1:]) or "what is the capital of France?"
resp = client.chat.completions.create(
    model=MODEL, messages=[{"role": "user", "content": prompt}], max_tokens=16)
print(f"prompt_tokens: {resp.usage.prompt_tokens}")
print(f"0 control (no tools at all)         : {resp.usage.prompt_tokens}")
