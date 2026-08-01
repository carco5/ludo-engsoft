# Part 2 — Same task, two roads

**Josep Coll** · Week 3 · Exercise 2

One task — *post a comment to the course forum thread* — done twice: once through a CLI,
once through a browser. Both roads talk to the model through the **same LiteLLM proxy**, so
the two bills are counted in one place by one tokenizer.

## What is a stand-in here, and why

The exercise posts to the **Àrtemis** course forum. I have no Àrtemis credentials on this
machine, so `forum/` is a local forum that offers the two surfaces the comparison needs: an
**HTML page with a comment form** for the browser road, and a **JSON API** for the CLI road.
Both roads write to the same thread, so the two comments end up side by side.

Road two should be `npx -y @playwright/mcp@latest` inside OpenCode. This is WSL with no
working Node toolchain, so `road-browser/playwright_mcp_server.py` is the smallest server
that reproduces what is being measured: the same four core tools the official one exposes
(`browser_navigate`, `browser_snapshot`, `browser_type`, `browser_click`), the same
accessibility-tree snapshots with `[ref=eN]` handles, over the same stdio JSON-RPC
transport, mounted in **the course's own MCP agent loop**.

Both substitutions push the result the **same way — in the browser road's favour**: the
official Playwright MCP advertises about twenty tools where mine advertises four, and a real
Àrtemis page is far larger than my forum page, so its snapshots would be far larger too.
The ratio measured here is a **floor**.

## Layout

```
part2-two-roads/
├── forum/                        the local Àrtemis stand-in (FastAPI)
│   └── app.py                    HTML thread page + JSON API, one store
├── road-cli/                     ROAD ONE
│   ├── forum-cli                 the CLI tool (argparse, --help)
│   ├── skills/forum-cli/skill.md the skill that says "use this tool"
│   ├── agent.md, memory/         the agent's self
│   └── minimal_cli_agent.py      the course's demo-04 agent + a token tally
├── road-browser/                 ROAD TWO
│   ├── playwright_mcp_server.py  a minimal Playwright MCP server
│   └── browser_agent.py          the course's demo-03 MCP loop + a token tally
└── measure.sh                    runs both roads and reads the meter
```

## Run it

Three terminals.

```bash
# 1 — the forum
cd forum && uv run --with fastapi --with uvicorn --with python-multipart python app.py

# 2 — the meter
litellm --model ollama/qwen2.5:7b --port 4000

# 3 — both roads, then the bill
./measure.sh
```

`road-browser` needs its browser once: `cd road-browser && uv sync && uv run playwright install chromium`.
`smoke_browser.py` checks the MCP server without spending any model time, and prints the registry
and one snapshot — the two things the browser road pays for.

> **Use a non-thinking model.** Through the LiteLLM proxy, `qwen3`'s reasoning is stripped and
> `content` arrives empty, so the agent loop sees a blank answer and stops on turn one. And unload
> everything else from Ollama first (`ollama stop <model>`): with 7.6 GB of RAM, a second resident
> model pushes `qwen2.5:7b` into swap and it never finishes a turn.

## The numbers

| | road 1 — CLI | road 2 — browser | ratio |
|---|---|---|---|
| **total on the LiteLLM meter** | 3,573 *(4 calls)* | **27,249** *(12 calls)* | **7.6×** |
| *up to the call that actually posted* | *1,399 (2 calls)* | *3,228 (3 calls)* | *2.3×* |

Unit costs, measured with `registry_cost.py`: the 4-tool registry is **468 tokens in every
request**; one snapshot of this tiny forum page is **373 tokens, and it stays in the context
forever**. `tally.py` derives the table above from the logs in `runs/` — it is not typed by hand.

## Two defects I had to fix, both worth writing down

- A stale `ref` used to fail with a bare timeout. Refs die the moment the page navigates — and
  submitting the form *is* navigating — so the agent had nothing to steer by and retried the dead
  ref forever. Now a failed action reports the failure **and hands back the current snapshot**,
  the way the official server does. `runs/road-2-browser-first-attempt.log` is the run that
  found it.
- The snapshot listed no **static text**, so posted comments were invisible and the agent could
  not verify its own work. A real accessibility tree lists them. Adding them is more faithful —
  and it makes the browser road *more* expensive, which is to say it counts against my own thesis.

## What the two roads actually do

**Road one.** The agent starts with an index of its skills (one line each), reads
`forum-cli` when the task matches, learns the one command it needs, runs it behind the
y-gate, and stops. Nothing about the tool was in the context until the agent asked for it —
discovery on demand, the same trick `--help` plays.

**Road two.** The MCP registry is in the context from the first token, used or not. Then
every step pays again: navigate returns a snapshot, type returns a snapshot, click returns
a snapshot, and each one stays in the conversation for every later call.

Numbers, the ratio and the two sentences the exercise asks for are in the report:
`../../entrega-w3-ex2.md`.
