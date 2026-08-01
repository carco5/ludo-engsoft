# Part 1 — The registry tax

**Josep Coll** · Week 3 · Exercise 2

Put a meter on the model and read what a mounted MCP server costs when nobody uses it.

## What is in here

| file | what it is |
|---|---|
| `give_the_llm_hands.py` | the course's plain loop (demo 02) **+ the one line the exercise asks for**: `print(f"prompt_tokens: {resp.usage.prompt_tokens}")` right after `resp = ...` |
| `agent_with_mcp.py` | the course's MCP agent (demo 03), with the server script made configurable (`SERVER_SCRIPT`) so the same agent can mount either server |
| `server.py` | the course's minimal MCP server — **1 tool** |
| `server_6tools.py` | the same server with **five more tools** — canned bodies, real descriptions, because descriptions are what cost |
| `control_no_tools.py` | my own control: the same question with **no tools at all** |
| `measure.sh` | runs everything and prints the numbers |
| `runs/` | the raw logs of the run in my report |

## Why the control run exists

The exercise says the difference between the baseline and the mounted server *"is roughly
the registry"*. Roughly — because the baseline is the plain loop, and that loop already
carries two hand-written tool schemas (`wget`, `execute_sql`) plus a system prompt. So
"baseline vs MCP" compares one registry against another, not a registry against nothing.

One extra run fixes it: the same question, same model, **no `tools` field at all**. That is
the floor. With it the MCP registry can be priced exactly instead of roughly — and the
comparison also becomes fair in the other direction, because it shows that the hand-written
function-calling tools are *not* free either. The tax is not an MCP tax. It is a
tools-in-the-context tax; MCP just makes it easy to mount a lot of it at once.

## Run it

```bash
uv venv && source .venv/bin/activate && uv sync
MODEL=qwen3:1.7b ./measure.sh
```

Only the **first** LLM call of each run is the measurement — that is where the registry
shows up, before any tool result has entered the context.

## The numbers

| # | run | `prompt_tokens` |
|---|---|---|
| 0 | *control: same question, no `tools` field* | *17* |
| 1 | baseline — plain loop, no MCP | **271** |
| 2 | mounted **and used** | **162** |
| 3 | mounted, **NOT used** | **157** |
| 4 | mounted with **6 tools**, NOT used | **659** |

So the registry itself costs **140 tokens for one tool and 642 for six** — about 100 per extra
tool — riding on a 17-token question. Note that run 1 is *higher* than run 3: the exercise's
"baseline minus mounted is roughly the registry" comes out **negative** here, which is exactly
what run 0 exists to explain.

Full conclusions in the report: [`../../entrega-w3-ex2.md`](../../entrega-w3-ex2.md).
