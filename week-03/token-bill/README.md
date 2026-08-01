# The Token Bill — Week 3 · Exercise 2

**Josep Coll.** Two claims from the lectures. Instead of believing them, I put a meter on my own
machine and measured both.

> **Claim 1.** An MCP server's registry — the names, descriptions and schemas of its tools —
> rides in the context of *every* request, used or not.
> **Claim 2.** For most tasks, a CLI tool the model already knows is much cheaper than an
> MCP server it has to carry.

```
token-bill/
├── part1-registry-tax/   claim 1 — what a mounted-but-unused MCP server costs
└── part2-two-roads/      claim 2 — one real task, CLI vs browser, one LiteLLM meter
```

## What I found

**Claim 1 is true, and cheaper to prove than I expected.** The registry costs **140 tokens for
one tool and 642 for six**, on a question that is 17 tokens long, paid on every single request.
Ten servers like my fat one would be 6,420 tokens per request — 321,000 over a fifty-turn chat,
before anybody says anything.

**Claim 2 is true, but I could not reproduce the "order of magnitude" the lecture claims — I got
7.6×.** I know exactly why, because I measured the two pieces separately: my Playwright server
advertises 4 tools where the official one advertises ~20, and my forum page is about 1 KB where a
real page is tens. Both substitutions make the browser road look *cheaper* than it really is, so
what I report is a floor. I would rather publish a floor I can defend than a headline I cannot.

## Three decisions worth explaining

**I added a run the exercise did not ask for.** The brief says baseline-minus-mounted *"is roughly
the registry"*. On my setup that difference comes out **negative**, because the baseline loop
already carries two hand-written tool schemas *and* a system prompt while the MCP agent carries
one tool and no system prompt. So I measured the same question with **no `tools` field at all** to
get the real floor. That one extra run turns "roughly" into an exact number — and it also changes
the conclusion: the charge is not an *MCP* charge, it is a tools-in-the-context charge. MCP only
makes it easy to mount a lot of it at once.

**I report Part 2 two ways instead of one.** Both agents kept calling tools after they had already
finished the job — a small-model failure, not a road failure. A single total would have said as
much about my driver as about the roads. So I give the meter reading (what the exercise asks for)
next to the cost up to the call that actually posted. The gap between those two rows turned out to
be the most interesting result of the whole exercise: the same flailing cost the CLI agent 2,174
extra tokens and the browser agent **24,021**, because every browser retry re-reads the whole pile
of snapshots underneath it.

**I wrote down what I substituted, and which way it biases the result.** I have no Àrtemis
credentials and no Node toolchain on this box, so the forum is local and the Playwright MCP server
is mine. Both substitutions favour the browser road. Saying so is not a disclaimer — it is what
makes the number usable by somebody else.

## How to reproduce it

Each part has its own README with the exact commands. Everything runs against local Ollama on a
CPU-only WSL box — no key, no money — so every number inside a table comes from one tokenizer and
is comparable. The conclusions are in the report: [`../entrega-w3-ex2.md`](../entrega-w3-ex2.md).

## 📖 License & author

Derived from the course demos by **Marc Alier i Forment** (UPC), licensed
**CC BY-NC-SA 4.0**; this derivative is under the same license.
