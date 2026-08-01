# Week 1 (Transformers, LLMs and the API call) — Josep Coll's work

My exercises for **BSC Agents Course · Week 1**. `demos/` and `README.md` in this folder are the
course's; everything below is mine.

| # | What I built | Folder | Report |
|---|---|---|---|
| **1** | **Tokenization** — real tokenizers loaded with `transformers`, counting what the model actually sees | [`ex-01-tokenise/`](ex-01-tokenise/) | [`entrega-w1.md`](entrega-w1.md) |
| **2** | **Base vs. aligned** — GPT-2 (never RLHF'd) and Qwen3-1.7B side by side on the same four prompts | [`ex-02-base-vs-aligned/`](ex-02-base-vs-aligned/) | [`entrega-w1.md`](entrega-w1.md) |
| **3–4** | **The API call** — the bare `chat/completions` request in `curl` and in Python, against my own Ollama | [`ex-04-call-the-llm/`](ex-04-call-the-llm/) | [`entrega-w1.md`](entrega-w1.md) |
| **5** | **EASY-CHATGPT** — a chatbot: FastAPI proxy + vanilla-JS frontend, markdown rendering, a live view of the exact `messages` array, and SSE streaming | [`ex-05-easy-chatgpt/`](ex-05-easy-chatgpt/) | [`entrega-w5.md`](ex-05-easy-chatgpt/entrega-w5.md) |

## What I measured

The same paragraph costs **+66 % more tokens in Spanish than in English** with the GPT-2
tokenizer. That is not a fact I read — it is my own text, counted. Tokenizers are trained mostly
on English, so Spanish words get split into more sub-words, and my bill goes up for writing in my
own language.

## The decision I care about in this week

**The browser never talks to the model.** In EASY-CHATGPT the frontend calls *my* FastAPI backend,
and the backend calls the LLM. It would have been fewer lines to call the model straight from
JavaScript — and it would have shipped my API key to every visitor's browser. The proxy is also
what let me show the exact `messages` array on screen: once every request goes through one place
of mine, I can print it.

The whole provider choice lives in `.env`. Nothing else in the code knows whether it is talking to
Ollama, OpenAI or anything else — which is the point the course makes about the model being a
commodity, made concrete in one file.
