# Part 2 — Same task, two roads

**Josep Coll** · Week 3 · Exercise 2

One task — *post a comment to the course forum thread* — done twice: once through a CLI, once
through a browser. Both roads talk to the model through the **same LiteLLM proxy**, so the two
bills are counted in one place, by one tokenizer. That single detail is what makes the comparison
mean anything: if each agent had counted its own tokens, I would be comparing two rulers.

## Layout

```
part2-two-roads/
├── forum/                        the local Àrtemis stand-in (FastAPI)
│   └── app.py                    HTML thread page + JSON API, one store
├── road-cli/                     ROAD ONE
│   ├── forum-cli                 the CLI tool I wrote (argparse, --help)
│   ├── skills/forum-cli/skill.md the skill that says "use this tool"
│   ├── agent.md, memory/         the agent's self
│   └── minimal_cli_agent.py      the course's demo-04 agent + a token tally
├── road-browser/                 ROAD TWO
│   ├── playwright_mcp_server.py  the Playwright MCP server I wrote
│   ├── browser_agent.py          the course's demo-03 MCP loop + a token tally
│   ├── smoke_browser.py          checks the server without spending model time
│   └── registry_cost.py          prices the registry and one snapshot, in tokens
├── tally.py                      derives the results table from the logs
└── measure.sh                    runs both roads and reads the meter
```

## What I substituted, and which way it biases the result

The exercise posts to the **Àrtemis** course forum. I have no Àrtemis credentials on this machine,
so `forum/` is a local forum offering the two surfaces the comparison needs: an **HTML page with a
comment form** for the browser road and a **JSON API** for the CLI road, both writing to the same
thread so the two comments end up side by side.

Road two should be `npx -y @playwright/mcp@latest` inside OpenCode. This is WSL with no working
Node toolchain, so `road-browser/playwright_mcp_server.py` is the smallest server that reproduces
what is actually being measured: the same four core tools the official one exposes
(`browser_navigate`, `browser_snapshot`, `browser_type`, `browser_click`), the same
accessibility-tree snapshots with `[ref=eN]` handles, over the same stdio JSON-RPC transport,
mounted in **the course's own MCP agent loop**.

Both substitutions push the result the **same way — in the browser road's favour**: the official
Playwright MCP advertises about twenty tools where mine advertises four, and a real Àrtemis page is
far larger than mine, so its snapshots would be far larger too. **What I measured is a floor.** I
would rather publish a number I can defend than the one that makes my point better.

## The decisions I made, and why

**The task wording is identical on both roads.** My first browser run also asked the agent to sign
the comment with my name, and I threw that run away. `forum-cli` signs by default, so the browser
would have been paying for an extra typing step that the CLI got for free — an asymmetry I had
introduced myself, not one the roads have. Both prompts now ask for exactly one thing: post this
comment.

**Both agents get a turn budget.** Without one, a small model that starts going in circles burns
the meter until I notice. With one, a run that goes wrong still produces a bounded, comparable
number. Road one stopped by itself at 4 calls; road two hit the budget at 12.

**I kept the flailing in the numbers.** Both agents kept calling tools after the job was done. I
could have quietly reported only the clean part, but the honest bill of an agent includes its
mistakes — so I report the meter reading *and* the cost up to the call that actually posted, and
`tally.py` computes both from the logs rather than me typing them. The gap between those two rows
turned out to be the most interesting thing here.

**The y-gate is answered by a human, not removed.** `measure.sh` pipes `yes y` into road one
because the exercise says to approve the commands — but the gate still prints every command before
running it, exactly as the lecture argues security should work. Deleting the gate to make the
script tidier would have deleted the point of the demo.

## Two defects of mine I had to fix, both worth writing down

- A stale `ref` used to fail with a bare timeout. Refs die the moment the page navigates — and
  submitting the form *is* navigating — so the agent had nothing left to steer by and retried the
  dead ref forever. Now a failed action reports the failure **and hands back the current
  snapshot**, the way the official server does. `runs/road-2-browser-first-attempt.log` is the run
  that exposed it; I kept it in the repo instead of deleting the evidence.
- My snapshot listed no **static text**, so the comments already on the page were invisible and the
  agent could not verify its own work. A real accessibility tree lists them. Fixing it is more
  faithful — and it makes the browser road *more* expensive, which is to say it counts against my
  own thesis.

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

> **Two things that cost me hours, so you do not repeat them.** Use a **non-thinking** model:
> through the LiteLLM proxy `qwen3`'s reasoning is stripped and `content` arrives empty, so the
> agent loop sees a blank answer and stops on turn one. And **unload everything else from Ollama
> first** (`ollama stop <model>`): with 7.6 GB of RAM a second resident model pushes `qwen2.5:7b`
> into swap and it never finishes a turn.

## The numbers

| | road 1 — CLI | road 2 — browser | ratio |
|---|---|---|---|
| **total on the LiteLLM meter** | 3,573 *(4 calls)* | **27,249** *(12 calls)* | **7.6×** |
| *up to the call that actually posted* | *1,399 (2 calls)* | *3,228 (3 calls)* | *2.3×* |

Unit costs, measured with `registry_cost.py`: the 4-tool registry is **468 tokens in every
request**; one snapshot of this tiny forum page is **373 tokens, and it stays in the context
forever**. Those two numbers are what you scale if you want to know what the same run costs
against the official ~20-tool server, or against a real page.

## What the two roads actually do

**Road one.** The agent starts with an index of its skills — one line each — reads `forum-cli`
when the task matches, learns the one command it needs, runs it behind the y-gate, and stops.
Nothing about the tool was in the context until the agent asked for it: discovery on demand, the
same trick `--help` plays.

**Road two.** The MCP registry is in the context from the first token, used or not. Then every
step pays again: navigate returns a snapshot, type returns a snapshot, click returns a snapshot —
and each one stays in the conversation for every later call. By call 12 the model is re-reading
eleven copies of the same page.

Numbers, the ratio and the two sentences the exercise asks for are in the report:
[`../../entrega-w3-ex2.md`](../../entrega-w3-ex2.md).
