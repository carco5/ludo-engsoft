# Week 3 (Agents) — Josep Coll's work

My exercises for **BSC Agents Course · Week 3**. The `demos/` folder is the course's;
everything below is mine.

| # | What it is | Folder | Report |
|---|---|---|---|
| **1** | **The Straw House Emergency** — the function-calling demo restaged: the youngest pig, in the straw house, whose only tool is a phone to his elder brother in the brick house. | [`straw-house/`](straw-house/) | [`entrega-w3-ex1.md`](entrega-w3-ex1.md) |
| **2** | **The Token Bill** — measuring the two claims of the lectures: what a mounted-but-unused MCP registry costs, and what the same task costs through a CLI versus through a browser. | [`token-bill/`](token-bill/) | [`entrega-w3-ex2.md`](entrega-w3-ex2.md) |

## The one thing that shaped every result

This is a **CPU-only WSL box** with about 7.6 GB of RAM, running everything against local
Ollama. That turned Lecture 3.2's closing corollary — *the loop is trivial; the driver is not* —
into the practical constraint of the week:

- `qwen3:1.7b` and `llama3.2:3b` phone the brother on a plain `knock knock`;
- `qwen2.5:3b` announces it will call and calls nothing;
- `qwen3:4b` thinks for hundreds of tokens at 2.7 tok/s and never finishes a turn;
- **`qwen2.5:7b`** gets it right, at 2.3 tok/s, and only if every other model is unloaded first.

The same file, the same prompt, the same tool. Only the engine changed.

A second, sharper one for anyone reusing this: **through a LiteLLM proxy, `qwen3`'s reasoning
is stripped and `content` arrives empty**, so an agent loop sees a blank answer and stops. For
agents on this machine: non-thinking models.

## Running anything here

Each folder is independent — its own `pyproject.toml`, its own `.venv`:

```bash
cd week-03/straw-house
uv venv && source .venv/bin/activate && uv sync
cp .env.example .env    # then edit
python three_pigs_function_calling.py
```

`token-bill/part1-registry-tax/` and `token-bill/part2-two-roads/` each carry a README with
their own setup and the exact commands that produced the numbers in the reports.
