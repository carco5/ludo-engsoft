"""
EASY-ASSISTANT — EASY-CHATGPT grows its first RAG.

A user can create an assistant (name + system prompt + prompt template with
{context} and {user_input} gaps), upload ONE plain-text document for it, and
chat. On every turn the backend fills the template — {context} with the WHOLE
file, {user_input} with the user's message — sends it to the LLM, and returns
the answer TOGETHER with the exact filled prompt and the token usage, so the
frontend can show what was actually sent (the whole file rides along every turn).

Persistence is a JSON file on disk — no database needed for this exercise.
The LLM is reached over the OpenAI-compatible API, configured only via .env.
"""
import json
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "ollama")
MODEL = os.environ.get("MODEL", "qwen3:1.7b")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
app = FastAPI(title="EASY-ASSISTANT")

STATIC = Path(__file__).parent / "static"
DATA = Path(__file__).parent.parent / "data"
DOCUMENTS = DATA / "documents"
ASSISTANTS_FILE = DATA / "assistants.json"

DEFAULT_TEMPLATE = (
    "Use only the information in the context below to answer the question.\n"
    "If the answer is not in the context, say that you do not know.\n\n"
    "Context:\n----\n{context}\n----\n\nQuestion: {user_input}"
)


def load_assistants() -> dict:
    if ASSISTANTS_FILE.exists():
        return json.loads(ASSISTANTS_FILE.read_text(encoding="utf-8"))
    return {}


def save_assistants(assistants: dict) -> None:
    DATA.mkdir(exist_ok=True)
    ASSISTANTS_FILE.write_text(json.dumps(assistants, indent=2, ensure_ascii=False),
                               encoding="utf-8")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def config():
    return {"model": MODEL, "base_url": BASE_URL, "default_template": DEFAULT_TEMPLATE}


@app.get("/api/assistants")
def list_assistants():
    return list(load_assistants().values())


@app.post("/api/assistants")
async def create_assistant(request: Request):
    body = await request.json()
    name = (body.get("name") or "").strip()
    system_prompt = (body.get("system_prompt") or "").strip()
    template = body.get("prompt_template") or DEFAULT_TEMPLATE
    if not name or not system_prompt:
        raise HTTPException(400, "name and system_prompt are required")
    # The two gaps are the contract of the whole exercise — refuse a template without them.
    if "{context}" not in template or "{user_input}" not in template:
        raise HTTPException(400, "prompt_template must contain {context} and {user_input}")
    assistants = load_assistants()
    aid = uuid.uuid4().hex[:8]
    assistants[aid] = {"id": aid, "name": name, "system_prompt": system_prompt,
                       "prompt_template": template, "document": None}
    save_assistants(assistants)
    return assistants[aid]


@app.post("/api/assistants/{aid}/document")
async def upload_document(aid: str, file: UploadFile):
    assistants = load_assistants()
    if aid not in assistants:
        raise HTTPException(404, "no such assistant")
    text = (await file.read()).decode("utf-8", errors="replace")
    if not text.strip():
        raise HTTPException(400, "the file is empty")
    DOCUMENTS.mkdir(parents=True, exist_ok=True)
    (DOCUMENTS / f"{aid}.txt").write_text(text, encoding="utf-8")
    assistants[aid]["document"] = {"filename": file.filename, "chars": len(text)}
    save_assistants(assistants)
    return assistants[aid]


@app.post("/api/assistants/{aid}/chat")
async def chat(aid: str, request: Request):
    assistants = load_assistants()
    if aid not in assistants:
        raise HTTPException(404, "no such assistant")
    assistant = assistants[aid]
    doc_path = DOCUMENTS / f"{aid}.txt"
    if not assistant["document"] or not doc_path.exists():
        raise HTTPException(400, "upload a document first — the assistant has no context")

    body = await request.json()
    history = body.get("history", [])   # BARE turns only, what the chat UI keeps
    user_input = (body.get("message") or "").strip()
    if not user_input:
        raise HTTPException(400, "empty message")

    # Static RAG: the WHOLE file goes into {context}, rebuilt fresh on every turn.
    context = doc_path.read_text(encoding="utf-8")
    augmented = assistant["prompt_template"].format(context=context, user_input=user_input)
    messages = ([{"role": "system", "content": assistant["system_prompt"]}]
                + history
                + [{"role": "user", "content": augmented}])
    try:
        resp = client.chat.completions.create(model=MODEL, messages=messages, temperature=0.7)
    except Exception as e:
        raise HTTPException(502, f"LLM call failed: {e}")

    return {
        "reply": resp.choices[0].message.content,
        "usage": resp.usage.model_dump() if resp.usage else None,
        "model": MODEL,
        # Disclosure: the exact augmented prompt and the full messages array,
        # so the page can show what was actually sent on THIS turn.
        "augmented_prompt": augmented,
        "messages_sent": messages,
    }


app.mount("/static", StaticFiles(directory=STATIC), name="static")
