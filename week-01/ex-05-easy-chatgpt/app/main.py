"""
EASY-CHATGPT — a tiny FastAPI server that sits as a proxy between the chat
frontend and the LLM. The browser never calls the model directly: it calls
this server, the server calls the LLM over the OpenAI-compatible API
(configured only via .env), and passes the answer back.
"""
import json
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "ollama")
MODEL = os.environ.get("MODEL", "qwen3:1.7b")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
app = FastAPI(title="EASY-CHATGPT")

STATIC = Path(__file__).parent / "static"


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def config():
    # the frontend shows which model/endpoint it is talking to
    return {"model": MODEL, "base_url": BASE_URL}


@app.post("/api/chat")
async def chat(request: Request):
    """Baseline: wait for the whole answer, then return it (+ token usage)."""
    body = await request.json()
    messages = body.get("messages", [])
    try:
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.7
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=502)
    return {
        "reply": resp.choices[0].message.content,
        "usage": resp.usage.model_dump() if resp.usage else None,
        "model": MODEL,
    }


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """Advanced: stream from the LLM and relay it to the browser as SSE."""
    body = await request.json()
    messages = body.get("messages", [])

    def gen():
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7,
                stream=True,
                stream_options={"include_usage": True},
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield "data: " + json.dumps({"delta": chunk.choices[0].delta.content}) + "\n\n"
                if getattr(chunk, "usage", None):
                    yield "data: " + json.dumps({"usage": chunk.usage.model_dump()}) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({"error": str(e)}) + "\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
