# Part 1 — The registry tax

**Josep Coll** · Week 3 · Exercise 2

I put a meter on the model and read what a mounted MCP server costs when nobody uses it.

## What is in here

| file | what it is |
|---|---|
| `give_the_llm_hands.py` | the course's plain loop (demo 02) **+ the one line the exercise asks for**: `print(f"prompt_tokens: {resp.usage.prompt_tokens}")` right after `resp = ...` |
| `agent_with_mcp.py` | the course's MCP agent (demo 03). I made the server script configurable (`SERVER_SCRIPT`) so the same agent can mount either server without editing code — otherwise the two runs would differ by more than the thing I am measuring |
| `server.py` | the course's minimal MCP server — **1 tool** |
| `server_6tools.py` | the same server with **five more tools** I wrote |
| `control_no_tools.py` | a control run of my own: the same question with **no tools at all** |
| `measure.sh` | runs everything and prints the numbers |
| `runs/` | the raw logs behind every number in my report |

## The decisions I made, and why

**Why the control run exists.** The exercise says the difference between the baseline and the
mounted server *"is roughly the registry"*. Roughly — because the baseline is the plain loop, and
that loop already carries two hand-written tool schemas (`wget`, `execute_sql`) plus a system
prompt. So "baseline vs MCP" compares one registry against *another*, not a registry against
nothing. On my numbers that difference even comes out **negative**, which would have looked like a
mistake rather than a finding.

One extra run fixes it: same question, same model, **no `tools` field at all**. That is the floor,
and with it the registry can be priced exactly instead of roughly. It also changed my conclusion:
the hand-written function-calling tools are not free either, so **the tax is not an MCP tax — it
is a tools-in-the-context tax**. MCP just makes it easy to mount a lot of it at once.

**Why the five extra tools have real descriptions.** Their bodies return canned strings, because
what they *do* is irrelevant to a token measurement. But I wrote the descriptions the way I would
write them for real — full sentences, when to use the tool, what the arguments mean. That is
deliberate: **the description is what costs**, and a measurement made with `"description": "gets
stuff"` would flatter MCP and teach me nothing.

**Why only the first call of each run counts.** After the first call, tool *results* start
entering the context and the numbers stop being about the registry. The first call is the only
moment where the registry is the sole difference between the runs.

**Why `qwen3:1.7b` here, when I needed `qwen2.5:7b` everywhere else.** This part measures
`prompt_tokens`, which is the tokenizer counting the input — it does not depend on the model
reasoning well. The small model is several times faster on this CPU, and using one model for all
five runs is what makes them comparable. Judgement only mattered in Part 2, and there I paid for
the bigger model.

## Run it

```bash
uv venv && source .venv/bin/activate && uv sync
MODEL=qwen3:1.7b ./measure.sh
```

## The numbers

| # | run | `prompt_tokens` |
|---|---|---|
| 0 | *control: same question, no `tools` field* | *17* |
| 1 | baseline — plain loop, no MCP | **271** |
| 2 | mounted **and used** | **162** |
| 3 | mounted, **NOT used** | **157** |
| 4 | mounted with **6 tools**, NOT used | **659** |

So the registry itself costs **140 tokens for one tool and 642 for six** — about 100 per extra
tool — riding on a 17-token question. Note run 1 sitting *above* run 3: that is the negative
difference the control run explains.

Full conclusions in the report: [`../../entrega-w3-ex2.md`](../../entrega-w3-ex2.md).
