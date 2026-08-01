# Week 2 (RAG) — Josep Coll's work

My exercises for **BSC Agents Course · Week 2**. `demos/`, `collections-manager/` and
`simple-dynamic-rag/` are the course's; everything below is mine.

| # | What I built | Folder | Report |
|---|---|---|---|
| **1** | **EASY-ASSISTANT** — assistants defined by a system prompt + a prompt template, grounded on one whole file, with the filled-in prompt and the token count visible on screen | [`ex-01-easy-assistant/`](ex-01-easy-assistant/) | [`entrega-w2-ex1.md`](ex-01-easy-assistant/entrega-w2-ex1.md) |
| **2** | **Embeddings explorer** — paraphrases, negation and cross-language, measured | *(course demo)* | [`entrega-w2-ex2.md`](entrega-w2-ex2.md) |
| **3** | **Collections, ingestion and the threshold** | *(course demos)* | [`entrega-w2-ex3.md`](entrega-w2-ex3.md) |
| **Final** | **EASY-RAG** — dynamic RAG end to end: upload → markitdown → chunking → one Chroma collection per assistant → top-K + threshold, answers that link back to the source and refuse when nothing scores high enough | [`easy-rag/`](easy-rag/) | [`entrega-w2-final.md`](easy-rag/entrega-w2-final.md) |

## What I measured

On **my own corpus** with `nomic-embed-text`: an off-topic question tops out at **0.462** in
English but **0.539** in Spanish — sharing the corpus's language pushes similarity up on its own —
while a real question's chunks land at **0.61–0.807**.

## The decisions I care about in this week

**I set my rejection threshold at 0.55, from my own numbers.** It sits in the gap between 0.539
and 0.61, and that gap is only about seven hundredths wide — which is the finding, not an
inconvenience. Copying a threshold from a tutorial would have meant picking a number with no idea
how much room it left me. And the number is not portable: my own off-topic floor moved from 0.46
to 0.54 just by asking the question in Spanish, so it belongs to *this* model, *this* corpus and
even the query language. That is why EASY-RAG shows the score next to every answer instead of
hiding it.

**Every answer links back to its source.** Ingestion stores both the original document and the
markdown distillation under `/static/docs/`, so a chunk can point at the page it came from. It
costs storage and a little bookkeeping, and it buys the one thing a RAG answer needs: the reader
can check it. Retrieval is a bet — the lecture is explicit about that — so the app should let you
verify the bet rather than ask you to trust it.

**Chunking by headings first, characters second.** `sections(level=2)` keeps a chunk to one idea
when the document has structure, and `chars(800/100)` is the fallback for documents that do not.
Chunking blindly by characters is simpler and cuts sentences in half.

## What surprised me

Embeddings capture **topic, not polarity**. *"I love this film"* and *"I hate this film"* score
**0.706** against each other and are each other's nearest neighbour. Opposite meaning, almost the
same position. Anything that needs to know whether a text is *for* or *against* something cannot
be built on cosine similarity alone.
