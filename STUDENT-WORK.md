# Josep Coll — coursework

My work for **Transformers, LLMs, RAG and Agents: From Theory to Production** (BSC × UPC,
Prof. Marc Alier). This repository is a fork of the course repo: `demos/` folders and the
provided tools are the professor's; everything listed below is mine.

Every exercise runs **locally on a CPU-only WSL box against Ollama** — no API key, no money.
That constraint shaped a lot of the results, and where it did, I measured it instead of
mentioning it.

---

## Week 1 — Transformers, LLMs and the API call · [week index](week-01/MY-WORK.md)

| # | What I built | Where | Report |
|---|---|---|---|
| 1–4 | Tokenizers by hand, base vs. aligned models (GPT-2 vs. Qwen3-1.7B), and the bare API call in `curl` and in Python | [`week-01/ex-01-tokenise/`](week-01/ex-01-tokenise/) · [`ex-02-base-vs-aligned/`](week-01/ex-02-base-vs-aligned/) · [`ex-04-call-the-llm/`](week-01/ex-04-call-the-llm/) | [`entrega-w1.md`](week-01/entrega-w1.md) |
| 5 | **EASY-CHATGPT** — a chatbot with a FastAPI proxy (the browser never touches the model), vanilla-JS frontend, markdown rendering, a live view of the exact `messages` array sent, and SSE streaming; `docker compose up` | [`week-01/ex-05-easy-chatgpt/`](week-01/ex-05-easy-chatgpt/) | [`entrega-w5.md`](week-01/ex-05-easy-chatgpt/entrega-w5.md) |

**Measured:** the same paragraph costs **+66 % tokens in Spanish** than in English with the
GPT-2 tokenizer — the multilingual penalty, on my own text.

## Week 2 — RAG · [week index](week-02/MY-WORK.md)

| # | What I built | Where | Report |
|---|---|---|---|
| 1 | **EASY-ASSISTANT** — assistants defined by a system prompt + a prompt template, grounded on a single whole file, with the filled-in prompt and the token count on screen | [`week-02/ex-01-easy-assistant/`](week-02/ex-01-easy-assistant/) | [`entrega-w2-ex1.md`](week-02/ex-01-easy-assistant/entrega-w2-ex1.md) |
| 2–3 | Embeddings explorer, collections, ingestion and threshold experiments | [`week-02/`](week-02/) | [`entrega-w2-ex2.md`](week-02/entrega-w2-ex2.md) · [`entrega-w2-ex3.md`](week-02/entrega-w2-ex3.md) |
| Final | **EASY-RAG** — dynamic RAG: upload → markitdown → chunking (`sections(level=2)` with a char fallback) → one Chroma collection per assistant → top-K + threshold retrieval, answers that **link back to the source** and refuse honestly when nothing scores high enough | [`week-02/easy-rag/`](week-02/easy-rag/) | [`entrega-w2-final.md`](week-02/easy-rag/entrega-w2-final.md) |

**Measured:** on my own corpus with `nomic-embed-text`, an off-topic question tops out at **0.462**
in English but **0.539** in Spanish — sharing the corpus's language raises similarity by itself —
while a real question's chunks land at **0.61–0.807**. So I set the rejection threshold at
**0.55**, in the gap, from my numbers rather than from a tutorial's.

**Found the hard way:** embeddings capture *topic*, not *polarity* — *"I love this film"* and
*"I hate this film"* score **0.706** against each other, each the other's nearest neighbour.

## Week 3 — Agents · [week index](week-03/MY-WORK.md)

| # | What I built | Where | Report |
|---|---|---|---|
| 1 | **The Straw House Emergency** — the function-calling demo restaged: the youngest pig, in the straw house, whose only tool is a phone to his elder brother in the brick house. My own tool schema, with the *when not to call* written into the description | [`week-03/straw-house/`](week-03/straw-house/) | [`entrega-w3-ex1.md`](week-03/entrega-w3-ex1.md) |
| 2 | **The Token Bill** — what a mounted-but-unused MCP registry costs, and what the same task costs through a CLI versus through a browser. Includes a local forum, a `forum-cli` + a skill, and a Playwright MCP server I wrote | [`week-03/token-bill/`](week-03/token-bill/) | [`entrega-w3-ex2.md`](week-03/entrega-w3-ex2.md) |

**Measured — the MCP registry tax** (`prompt_tokens` of the first call, same 17-token question):

| no `tools` at all | 1 tool mounted, unused | 6 tools mounted, unused |
|---|---|---|
| 17 | 157 | 659 |

So the registry costs **140 tokens for one tool and 642 for six**, paid on *every* request,
used or not. Ten servers like that = 6,420 tokens per request → **321,000 over a fifty-turn
chat**, before anyone says anything.

**Measured — CLI vs. browser**, same task, both through one LiteLLM proxy:
**3,573 tokens by CLI against 27,249 by browser — 7.6×**.

**Where I disagreed with the brief:** the exercise says baseline-minus-mounted *"is roughly the
registry"*. In my setup it comes out **negative**, because the baseline loop already carries two
hand-written tool schemas and a system prompt. I added a control run with no `tools` field at all
to establish the real floor — and that also shows the charge is not an *MCP* charge but a
tools-in-the-context charge.

---

## What running everything on a CPU box taught me

Lecture 3.2 ends on *"the loop is trivial; the driver is not."* Week 3 turned that into the
binding constraint of the week, so I measured it. Same file, same prompt, same tool:

| model | plain `knock knock` | the real threat | verdict |
|---|---|---|---|
| `qwen3:1.7b` | **calls** the brother ❌ | calls ✅ | panics at a knock |
| `llama3.2:3b` | **calls** the brother ❌ | calls ✅ | same |
| `qwen2.5:3b` | doesn't call ✅ | **says** it will call, doesn't ❌ | fails the other way |
| `qwen3:4b` | — | — | thinks for hundreds of tokens at 2.7 tok/s; never finishes a turn |
| **`qwen2.5:7b`** | doesn't call ✅ | **calls** ✅ | the one I used |

Two operational findings that are not in any of the lectures:

- **Through a LiteLLM proxy, `qwen3`'s reasoning is stripped and `content` arrives empty**, so an
  agent loop sees a blank answer and stops on turn one. For agents on this machine: non-thinking
  models only.
- **Memory decides everything.** Ollama will happily hold two models resident; with 7.6 GB of RAM
  that pushes the big one into swap and it never completes a turn. `ollama stop` everything else
  first and `qwen2.5:7b` loads in 33 s and runs at 2.3 tok/s — slow, but usable.
