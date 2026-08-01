# The Token Bill — Week 3 · Exercise 2

**Josep Coll** — measure the two claims of the lectures instead of believing them.

> **Claim 1.** An MCP server's registry — the names, descriptions and schemas of its tools —
> rides in the context of *every* request, used or not.
> **Claim 2.** For most tasks, a CLI tool the model already knows is much cheaper than an
> MCP server it has to carry.

```
token-bill/
├── part1-registry-tax/   claim 1 — four prompt_tokens numbers on a tiny MCP server
└── part2-two-roads/      claim 2 — one real task, CLI vs browser, one LiteLLM meter
```

Each part has its own README with the setup; the numbers, the table and the conclusions are
in the report: [`../entrega-w3-ex2.md`](../entrega-w3-ex2.md).

Everything runs against a local Ollama endpoint on a CPU-only WSL box — no key, no money —
so all the numbers in a given table come from the same tokenizer and are comparable.

## 📖 License & author

Derived from the course demos by **Marc Alier i Forment** (UPC), licensed
**CC BY-NC-SA 4.0**; this derivative is under the same license.
