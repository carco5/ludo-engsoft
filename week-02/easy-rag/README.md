# EASY-RAG — Week 2 · Final Project

EASY-ASSISTANT grows into a real **dynamic RAG** application: many documents,
stored in a collection, retrieved by meaning, a few relevant chunks per
question — with provenance on every answer.

Built **on top of the course's provided utility** `collections-manager`
(`create_collection` / `insert` / `query` on ChromaDB), added as a path
dependency the same way `simple-dynamic-rag` does. The app talks to the
abstraction layer, never to the database engine.

## What it does

- **Assistants** — name, system prompt, prompt template with `{context}` /
  `{user_input}` (same object as Exercise 1). Persisted in a JSON file.
  Each assistant owns **one collection** (`assistant-<id>`).
- **Upload documents** (pdf, docx, md, txt, html…). On upload the backend
  **ingests** — the four steps from the lecture:
  1. *convert* to markdown with **markitdown**;
  2. *store* the original **and** the markdown distillation under
     `/static/docs/` so every chunk can link back to its source;
  3. *chunk* it — `sections(level=2)` by default, falling back to
     `chars(800/100)` when the document has no headings; all knobs are `.env`
     configuration, not constants;
  4. *insert* each chunk with metadata: document URL, title, markdown URL,
     chunk number, chunking strategy, ingestion date.
- **Chat with grounded answers** — the user's message *is* the query;
  the top-K chunks over the similarity threshold are formatted with their
  provenance and injected into the template. K and the threshold come from
  `.env` (defaults: `TOP_K=4`, `THRESHOLD=0.55` — the band I measured in
  Exercise 3).
- **Provenance on every answer** — a table with similarity, source document
  (clickable link to `/static`), chunk number and a link to the distilled
  markdown. Plus the exact filled prompt and the token usage.
- **Honest refusal** — when nothing passes the threshold the assistant says it
  does not know **without calling the model**: zero tokens spent on noise.

## Run it

```bash
ollama serve
ollama pull qwen3:1.7b          # writes the answers
ollama pull nomic-embed-text    # turns text into vectors

cp .env.example .env
uv run uvicorn app.main:app --port 6663    # open http://localhost:6663
```

## Try it

Three sample documents live in `sample-docs/` (a coffee roastery fact sheet, the
Acme robot handbook, a climbing-gym guide). Upload all three to one assistant
and ask a question only one of them answers — the provenance table shows the
chunks came from the right document. Then ask something none of them covers and
watch the honest refusal.
