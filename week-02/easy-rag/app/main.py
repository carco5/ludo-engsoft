"""
EASY-RAG — the Week 2 final project: EASY-ASSISTANT grows into real dynamic RAG.

What changed from Exercise 1: an assistant no longer holds ONE pasted file.
It holds a COLLECTION (one per assistant, through the course's provided
collections-manager — create_collection / insert / query on ChromaDB).

  * Upload documents (pdf, docx, md, txt, ...). The backend INGESTS each one:
      1. convert to markdown (markitdown),
      2. store the original + the markdown distillation under /static so every
         chunk can link back to its source,
      3. chunk it (strategy, size and heading level are configuration),
      4. insert the chunks with metadata: doc url, title, md url, chunk number,
         chunking strategy, ingestion date.
  * Chat: the user's message IS the query. Retrieve top-K chunks over the
    similarity threshold, format them with their provenance, fill the same
    {context}/{user_input} template as Exercise 1, send.
  * Every answer returns its provenance (which chunks, from which document,
    with what similarity) and the token usage.
  * When nothing passes the threshold the assistant refuses honestly —
    it does not call the model to answer from noise.

The app talks to the abstraction layer (create_collection / insert / query),
never to the database engine underneath. K, the threshold and the chunking
knobs are configuration (.env), not constants.
"""
import datetime
import json
import os
import re
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from markitdown import MarkItDown
from openai import OpenAI

from collections_manager import create_collection, insert, query

BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "ollama")
MODEL = os.environ.get("MODEL", "qwen3:1.7b")

# Retrieval and chunking are configuration, not constants.
TOP_K = int(os.environ.get("TOP_K", "4"))
THRESHOLD = float(os.environ.get("THRESHOLD", "0.55"))
CHUNK_STRATEGY = os.environ.get("CHUNK_STRATEGY", "sections")  # sections | chars
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "100"))
SECTION_LEVEL = int(os.environ.get("SECTION_LEVEL", "2"))

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
app = FastAPI(title="EASY-RAG")

APP_DIR = Path(__file__).parent
STATIC = APP_DIR / "static"
DOCS = STATIC / "docs"                      # originals + markdown distillations, linkable
DATA = APP_DIR.parent / "data"
ASSISTANTS_FILE = DATA / "assistants.json"
COLLECTIONS_STORE = str(DATA / "collections-store")

DEFAULT_TEMPLATE = (
    "Use only the information in the context below to answer the question.\n"
    "If the answer is not in the context, say that you do not know.\n\n"
    "Context:\n----\n{context}\n----\n\nQuestion: {user_input}"
)

REFUSAL = ("I don't know — nothing in this assistant's documents is close enough "
           "to your question (no chunk passed the similarity threshold).")


# ---------------------------------------------------------------- chunking ---
# The two plain strategies from the lecture — a for-loop, not a framework.

def chunk_by_chars(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Sliding window of `size` characters, stepping by size-overlap."""
    step = max(1, size - overlap)
    chunks, i = [], 0
    while i < len(text):
        piece = text[i:i + size].strip()
        if piece:
            chunks.append(piece)
        i += step
    return chunks


def chunk_by_sections(markdown: str, level: int = 2) -> list[str]:
    """Split a markdown document at headings of `level` (2 = ##, 4 = ####)."""
    heading = re.compile(rf"^#{{{level}}}\s", flags=re.MULTILINE)
    starts = [m.start() for m in heading.finditer(markdown)]
    if not starts:
        return [markdown.strip()] if markdown.strip() else []
    cuts = [0] + starts + [len(markdown)]
    return [markdown[a:b].strip() for a, b in zip(cuts, cuts[1:]) if markdown[a:b].strip()]


# ------------------------------------------------------------- persistence ---

def load_assistants() -> dict:
    if ASSISTANTS_FILE.exists():
        return json.loads(ASSISTANTS_FILE.read_text(encoding="utf-8"))
    return {}


def save_assistants(assistants: dict) -> None:
    DATA.mkdir(exist_ok=True)
    ASSISTANTS_FILE.write_text(json.dumps(assistants, indent=2, ensure_ascii=False),
                               encoding="utf-8")


def collection_for(aid: str):
    """One collection per assistant, persisted on disk, behind the abstraction layer."""
    return create_collection(f"assistant-{aid}", description="EASY-RAG assistant knowledge",
                             metric="cosine", persist_path=COLLECTIONS_STORE)


# ------------------------------------------------------------------ routes ---

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/config")
def config():
    return {"model": MODEL, "base_url": BASE_URL, "default_template": DEFAULT_TEMPLATE,
            "top_k": TOP_K, "threshold": THRESHOLD,
            "chunking": {"strategy": CHUNK_STRATEGY, "size": CHUNK_SIZE,
                         "overlap": CHUNK_OVERLAP, "level": SECTION_LEVEL}}


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
    if "{context}" not in template or "{user_input}" not in template:
        raise HTTPException(400, "prompt_template must contain {context} and {user_input}")
    assistants = load_assistants()
    aid = uuid.uuid4().hex[:8]
    assistants[aid] = {"id": aid, "name": name, "system_prompt": system_prompt,
                       "prompt_template": template, "documents": []}
    save_assistants(assistants)
    return assistants[aid]


@app.post("/api/assistants/{aid}/documents")
async def upload_document(aid: str, file: UploadFile):
    """Ingestion, the four steps from the lecture: convert, store, chunk, insert."""
    assistants = load_assistants()
    if aid not in assistants:
        raise HTTPException(404, "no such assistant")

    DOCS.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "document").name
    original_path = DOCS / f"{aid}-{safe_name}"
    original_path.write_bytes(await file.read())

    # 1 — convert whatever arrived (pdf, docx, md, txt, html...) to markdown
    try:
        result = MarkItDown().convert(str(original_path))
    except Exception as e:
        original_path.unlink(missing_ok=True)
        raise HTTPException(400, f"could not convert the document: {e}")
    markdown = result.text_content
    title = (result.title or Path(safe_name).stem).strip()

    # 2 — store the original and its distillation where they can be linked
    md_path = original_path.with_suffix(original_path.suffix + ".md")
    md_path.write_text(markdown, encoding="utf-8")
    doc_url = f"/static/docs/{original_path.name}"
    md_url = f"/static/docs/{md_path.name}"

    # 3 — chunk with the configured strategy
    if CHUNK_STRATEGY == "sections":
        chunks = chunk_by_sections(markdown, level=SECTION_LEVEL)
        strategy_label = f"sections(level={SECTION_LEVEL})"
        # A document with no headings degrades to one giant chunk — fall back.
        if len(chunks) <= 1:
            chunks = chunk_by_chars(markdown, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            strategy_label = f"chars(size={CHUNK_SIZE},overlap={CHUNK_OVERLAP}) [fallback]"
    else:
        chunks = chunk_by_chars(markdown, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
        strategy_label = f"chars(size={CHUNK_SIZE},overlap={CHUNK_OVERLAP})"
    if not chunks:
        raise HTTPException(400, "the document produced no chunks (is it empty?)")

    # 4 — insert every chunk with its provenance metadata
    col = collection_for(aid)
    source = f"{aid}-{Path(safe_name).stem}"
    inserted = 0
    for n, chunk in enumerate(chunks):
        r = insert(col, chunk, {
            "source": source,
            "doc_url": doc_url,
            "md_url": md_url,
            "title": title,
            "chunk_number": n,
            "chunking_strategy": strategy_label,
            "ingested_at": datetime.date.today().isoformat(),
        })
        inserted += r["ok"]

    assistants[aid]["documents"].append({
        "filename": safe_name, "title": title, "doc_url": doc_url, "md_url": md_url,
        "chunks": inserted, "strategy": strategy_label, "markdown_chars": len(markdown),
    })
    save_assistants(assistants)
    return assistants[aid]


@app.post("/api/assistants/{aid}/chat")
async def chat(aid: str, request: Request):
    assistants = load_assistants()
    if aid not in assistants:
        raise HTTPException(404, "no such assistant")
    assistant = assistants[aid]
    if not assistant["documents"]:
        raise HTTPException(400, "upload at least one document first")

    body = await request.json()
    history = body.get("history", [])   # BARE turns only — what the chat UI keeps
    user_input = (body.get("message") or "").strip()
    if not user_input:
        raise HTTPException(400, "empty message")

    # Dynamic augmentation: the user input IS the query.
    col = collection_for(aid)
    hits = query(col, user_input, top_k=TOP_K, threshold=THRESHOLD)

    if not hits:
        # Honest refusal: nothing passed the gate, so we do not ask the model
        # to invent an answer from noise — and we spend zero LLM tokens on it.
        return {"reply": REFUSAL, "refused": True, "usage": None, "model": MODEL,
                "provenance": [], "augmented_prompt": None,
                "retrieval": {"top_k": TOP_K, "threshold": THRESHOLD, "hits": 0,
                              "collection_chunks": col.count()}}

    # Format the surviving chunks with their provenance — nice markdown, so the
    # day you debug what actually goes into the LLM, you can read it.
    context = "\n\n".join(
        f"[{h['metadata']['title']} · chunk {h['metadata']['chunk_number']} "
        f"· similarity {h['similarity']:.3f}]\n{h['chunk']}"
        for h in hits)
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
        "refused": False,
        "usage": resp.usage.model_dump() if resp.usage else None,
        "model": MODEL,
        # Where the answer came from: document link, chunk number, similarity.
        "provenance": [{
            "title": h["metadata"]["title"],
            "source": h["metadata"]["source"],
            "chunk_number": h["metadata"]["chunk_number"],
            "similarity": h["similarity"],
            "doc_url": h["metadata"]["doc_url"],
            "md_url": h["metadata"]["md_url"],
        } for h in hits],
        "augmented_prompt": augmented,
        "retrieval": {"top_k": TOP_K, "threshold": THRESHOLD, "hits": len(hits),
                      "collection_chunks": col.count()},
    }


app.mount("/static", StaticFiles(directory=STATIC), name="static")
