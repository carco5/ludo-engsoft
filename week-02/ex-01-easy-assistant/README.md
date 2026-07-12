# EASY-ASSISTANT — Week 2 · Exercise 1

EASY-CHATGPT (week 1) grows its first RAG. A user can now:

- **Create an assistant** with a *name*, a *system prompt* and a *prompt template*
  containing the two gaps `{context}` and `{user_input}`.
- **Upload one plain-text document** — the assistant's whole knowledge.
- **Chat.** On every turn the backend fills the template — `{context}` with the
  **whole file**, `{user_input}` with the message — and sends it to the model.
- **See what was actually sent**: the page shows the exact filled prompt, the
  full `messages` array, and the token usage, so you can watch the whole file
  riding along on every single turn.

This is *static* (single-file) RAG: no index, no similarity search — the
simplest member of the RAG family. The point it teaches is the cost: watch
`prompt_tokens` never shrink, because the document is re-sent every turn.

Assistants persist in a JSON file (`data/assistants.json`); the uploaded
documents live in `data/documents/`. No database.

## Two models, two jobs

1. **The model that wrote this code** — a capable coding agent that I steered.
2. **The model the assistant talks to** — a small local model through Ollama,
   configured only via `.env` (default `qwen3:1.7b` on `http://localhost:11434/v1`).
   Switching to a frontier model is a `.env` change, not a code change.

## Run it

```bash
ollama serve && ollama pull qwen3:1.7b     # the assistant's model

cp .env.example .env                        # edit if needed
uv run uvicorn app.main:app --port 6662     # then open http://localhost:6662
```

Or with Docker (Ollama on the host):

```bash
docker compose up          # http://localhost:6662
```

## Try it

There is a sample document in `sample-docs/nebula-coffee.txt`. Create an
assistant, upload it, and ask *"How much does a bag of Orion Blend cost?"* —
it answers from the file. Then ask *"Who is the president of France?"* — it
says it does not know, which is the proof that it answers from **your**
document and not from the model's training data.
