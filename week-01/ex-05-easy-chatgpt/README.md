# EASY-CHATGPT

A small but real chatbot server. A **FastAPI** backend sits as a *proxy* between
the browser and the LLM: the frontend never calls the model directly — it calls
this server, the server calls the LLM over the OpenAI-compatible API (configured
only via `.env`), and passes the answer back. The frontend is plain
**JavaScript + HTML + CSS**, renders replies as **Markdown**, and shows a
**context view** with the exact messages sent and the token usage that comes back.

## Layout

```
ex-05-easy-chatgpt/
├── app/
│   ├── main.py            # FastAPI: serves the UI + /api/chat (baseline) + /api/chat/stream (SSE)
│   └── static/            # index.html, style.css, app.js  (vanilla frontend)
├── .env.example           # config: base_url, key, model  (copy to .env)
├── Dockerfile
└── docker-compose.yml     # serves on port 6661
```

## Run it

1. Have a model available on your **host's** Ollama (the container reaches the
   host, not the WSL distro):
   ```bash
   ollama serve            # if it is not already running
   ollama pull llama3.2:3b
   ```
2. Configure (never commit `.env`):
   ```bash
   cp .env.example .env
   ```
   The defaults reach the host's Ollama through `host.docker.internal` and use
   `llama3.2:3b`. Set `MODEL` to whatever your host's Ollama serves (`ollama list`).
3. Bring it up:
   ```bash
   docker compose up --build
   ```
4. Open **http://localhost:6661** in your browser.

## What it does

- **Baseline (no streaming):** `POST /api/chat` — FastAPI waits for the whole answer and returns it with the token `usage`.
- **Advanced (streaming):** `POST /api/chat/stream` — FastAPI streams from the LLM and relays it to the browser as Server-Sent Events, so the reply types out token by token. Toggle "streaming" in the header.
- **Context view:** the right panel shows the full `messages` array sent to the model (it grows turn by turn) and the prompt/completion/total tokens.

## Networking note

Inside Docker, `localhost` is the container itself, so the LLM endpoint uses
`host.docker.internal` to reach the host. The model name in `.env` must match a
model the **host's** Ollama serves, or you get `404 model not found`.

Config (`base_url`, `key`, `model`) lives only in `.env`; to call a cloud model
instead of local Ollama, change those three lines — the code does not change.
