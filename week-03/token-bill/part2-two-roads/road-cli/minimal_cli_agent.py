# © 2026 Marc Alier i Forment (Universitat Politècnica de Catalunya) · https://wasabi.essi.upc.edu/ludo · https://lamb-project.org
# BSC Agents Course — Transformers, LLMs, RAG and Agents: From Theory to Production
# Licensed under Creative Commons BY-NC-SA 4.0 — reuse must credit the author, no commercial use, derivatives under the same license.

"""
A minimal CLI agent — agents in 2026, in one file.

Three folders give the agent a self:
    agent.md   — who it is and what it must do (top of the system prompt)
    memory/    — markdown files, loaded whole at startup (fixed memory)
    skills/    — one folder per skill; only the FIRST LINE of each skill.md
                 is loaded at startup — the full text is read ON DEMAND

Two tools give it hands:
    run_command — one shell command, printed and y-gated before it runs
    read_skill  — fetch the full instructions of a skill by name

The engine is the same six-line loop from 'give the LLM hands'.

Usage:
    uv run minimal_cli_agent.py "make me a word report of the workspace"
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
                api_key=os.getenv("OPENAI_API_KEY", "ollama"),
                timeout=1800)
MODEL = os.getenv("MODEL", "qwen3:1.7b")
HOME = Path(__file__).resolve().parent
# W3-Ex2 (Josep Coll): a turn budget, so a small model that starts going in
# circles stops instead of burning the meter forever. Same reason as road two.
MAX_TURNS = int(os.getenv("MAX_TURNS", "12"))


# --- The self: agent.md + memory, loaded whole; skills, listed by first line --
def build_system():
    parts = [(HOME / "agent.md").read_text()]

    memory = sorted((HOME / "memory").glob("*.md"))
    if memory:
        parts.append("## Memory\n\n" + "\n\n".join(f.read_text() for f in memory))

    skills = sorted(d for d in (HOME / "skills").iterdir()
                    if (d / "skill.md").is_file())
    if skills:
        index = [f"- {d.name}: {(d / 'skill.md').read_text().splitlines()[0].lstrip('# ')}"
                 for d in skills]
        parts.append("## Skills available\n"
                     "Read a skill with read_skill BEFORE using it — the index "
                     "below is only the first line of each.\n\n" + "\n".join(index))
    return "\n\n".join(parts)


# --- The hands ---------------------------------------------------------------
TOOLS = [
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Run ONE shell command on the user's machine. The user "
                       "sees the exact command and must approve it.",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "The shell command."}},
            "required": ["command"]}}},
    {"type": "function", "function": {
        "name": "read_skill",
        "description": "Read the full instructions of an available skill.",
        "parameters": {"type": "object", "properties": {
            "name": {"type": "string", "description": "Skill folder name."}},
            "required": ["name"]}}},
]


def tool_run_command(command):
    """The y-gate: security lives here, in the scaffolding — never in the prompt."""
    print(f"\n⚠️  The agent wants to run:\n    $ {command}")
    if input("    Allow? (type 'y'): ").strip().lower() != "y":
        return "USER DENIED: the user refused this command. Do not retry it."
    r = subprocess.run(command, shell=True, capture_output=True, text=True,
                       timeout=120, cwd=HOME)
    out = (r.stdout + r.stderr)[:12000]
    return f"exit={r.returncode}\n{out}"


def tool_read_skill(name):
    f = HOME / "skills" / name / "skill.md"
    return f.read_text() if f.is_file() else f"ERROR: no skill named '{name}'."


DISPATCH = {"run_command": tool_run_command, "read_skill": tool_read_skill}


# --- The engine: the same six lines ------------------------------------------
def run(user_prompt):
    messages = [{"role": "system", "content": build_system()},
                {"role": "user", "content": user_prompt}]
    total_prompt = total_completion = 0
    for turn in range(1, MAX_TURNS + 1):                       # 1  the loop
        resp = client.chat.completions.create(                 # 2  ask, with tools
            model=MODEL, messages=messages, tools=TOOLS)
        u = resp.usage
        total_prompt += u.prompt_tokens
        total_completion += u.completion_tokens
        print(f"── call #{turn}: prompt_tokens={u.prompt_tokens} "
              f"completion_tokens={u.completion_tokens}", flush=True)
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))
        if not msg.tool_calls:                                 # 3  answer → stop
            print(f"\n✅ {msg.content}")
            break
        for tc in msg.tool_calls:                              # 4-5 run what it asked
            args = json.loads(tc.function.arguments or "{}")
            print(f"  → {tc.function.name}({args})", flush=True)
            result = DISPATCH.get(tc.function.name,
                                  lambda **_: "ERROR: unknown tool")(**args)
            messages.append({"role": "tool", "tool_call_id": tc.id,  # 6 feed back
                             "content": result})
    else:
        print(f"⛔ stopped: hit the {MAX_TURNS}-turn budget")

    print(f"\nTOTAL prompt_tokens={total_prompt} completion_tokens={total_completion} "
          f"total={total_prompt + total_completion}")


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) or "Introduce yourself: who are you, what do you remember, and what can you do?"
    print(f"⚙️  model={MODEL}  endpoint={client.base_url}")
    run(prompt)
