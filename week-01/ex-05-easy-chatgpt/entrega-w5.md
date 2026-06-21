# Week 1 — Exercise 5: EASY-CHATGPT

**Student:** Josep Coll
**Repository:** https://github.com/carco5/ludo-engsoft — code at `week-01/ex-05-easy-chatgpt/`
**Course:** Transformers, LLMs, RAG and Agents: From Theory to Production (BSC × UPC)

## What I built

A small chatbot server. A **FastAPI** backend acts as a *proxy* between the browser and the LLM: the frontend never calls the model directly — it calls FastAPI, which calls the LLM over the OpenAI-compatible API (configured only via `.env`) and relays the answer back. The frontend is **vanilla JavaScript + HTML + CSS**, renders replies as **Markdown**, and has a **context view** that shows the exact `messages` array sent to the model and the token usage that comes back. It runs with `docker compose up` on port 6661, and implements both the baseline (blocking) and the advanced (SSE streaming) endpoints.

## Screenshot — EASY-CHATGPT running

![EASY-CHATGPT running: chat with a Markdown-rendered reply on the left, context view (messages sent + token usage) on the right](easy-chatgpt.png)

## Which model I drove the coding agent with, and why

I built EASY-CHATGPT by steering a capable coding model rather than hand-typing it. A capable model is needed because a tiny local model cannot scaffold a working FastAPI + frontend + Docker setup reliably; the small local model is kept for the experiments, not for driving the agent. My job was to decide what to build (the proxy shape, the context view, the streaming), read the files it produced, run it, and fix what did not work.

## One thing that went wrong that I caught and fixed

Getting it to run under `docker compose up` failed at first: the chat returned `502 Bad Gateway`. There were two real, related problems:

1. From inside the container, the LLM endpoint cannot be `localhost` — that is the container itself. It has to be `host.docker.internal`, which reaches the host machine.
2. Even after that, it returned `404 model not found`. `host.docker.internal` points at the **host's** Ollama, and on my machine the host's Ollama serves a different model (`llama3.2:3b`) than the one I had first put in `.env`. I caught it by reading the error from the proxy and fixed it by setting `MODEL` in `.env` to a model the host's Ollama actually serves (checked with `ollama list`).

After those two fixes, `docker compose up` worked end to end: browser → FastAPI → host's Ollama → reply.

## One thing I'd want it to do next

I'd give it per-user chat history and let it pull answers from my own documents (RAG) and call tools — which is exactly where Week 2 goes.
