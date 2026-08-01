# Week 3 · Exercise 2, Part 2 — Josep Coll
"""
A minimal course forum — the local stand-in for the Àrtemis forum thread.

The exercise asks for the same task done twice: an agent posts a comment to a
course forum thread, once through a CLI and once through a browser. I have no
Àrtemis credentials from this machine, so the forum is local. Everything the
measurement depends on is preserved:

  * an HTML page a browser agent must read, fill in and submit
    (GET  /thread/1)
  * a JSON API a CLI tool can drive in one call
    (GET  /api/threads, GET /api/thread/1, POST /api/thread/1/comments)

Both roads write to the same store, so the two comments end up in the same
thread and you can see them side by side.

    uv run --with fastapi --with uvicorn python app.py     # http://localhost:6673
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

DATA = Path(__file__).resolve().parent / "data" / "comments.json"

THREADS = {
    1: {"title": "Week 3 — agents, MCP and the token bill",
        "opener": "Post here when you have finished Exercise 2. Say which road "
                  "your agent took and what the meter said."},
    2: {"title": "Week 2 — RAG: threshold values that worked for you",
        "opener": "Share the cosine threshold you settled on and why."},
}

SEED = [
    {"thread": 1, "author": "Marc Alier",
     "body": "Remember: the registry rides in every request, used or not.",
     "at": "2026-07-28T09:12:00Z"},
    {"thread": 1, "author": "Laia P.",
     "body": "Got the MCP agent running against Ollama. The unused-server number surprised me.",
     "at": "2026-07-29T18:40:00Z"},
    {"thread": 2, "author": "Marc Alier",
     "body": "Do not copy anyone's threshold. Measure your own corpus.",
     "at": "2026-07-20T11:00:00Z"},
]


def load():
    if not DATA.is_file():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        DATA.write_text(json.dumps(SEED, indent=2))
    return json.loads(DATA.read_text())


def save(comments):
    DATA.write_text(json.dumps(comments, indent=2))


def add(thread: int, author: str, body: str):
    comments = load()
    comments.append({"thread": thread, "author": author, "body": body,
                     "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    save(comments)
    return comments[-1]


app = FastAPI(title="Course forum (local Àrtemis stand-in)")


# --- the JSON API: what the CLI tool drives ---------------------------------
@app.get("/api/threads")
def api_threads():
    return [{"id": i, "title": t["title"]} for i, t in THREADS.items()]


@app.get("/api/thread/{thread_id}")
def api_thread(thread_id: int):
    return {"id": thread_id, "title": THREADS[thread_id]["title"],
            "comments": [c for c in load() if c["thread"] == thread_id]}


@app.post("/api/thread/{thread_id}/comments")
def api_post(thread_id: int, payload: dict):
    c = add(thread_id, payload.get("author", "anonymous"), payload["body"])
    return {"ok": True, "comment": c}


# --- the HTML: what the browser agent has to read and fill in ---------------
PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{title} — Course forum</title><style>
body{{font:15px/1.6 system-ui,sans-serif;max-width:760px;margin:32px auto;padding:0 18px;color:#1b1b1f}}
header{{border-bottom:2px solid #2f6df6;padding-bottom:8px;margin-bottom:18px}}
h1{{font-size:20px;margin:0}} .sub{{color:#667;font-size:13px}}
.comment{{border:1px solid #dcdfe5;border-radius:8px;padding:10px 14px;margin:10px 0;background:#fafbfe}}
.who{{font-weight:600}} .when{{color:#889;font-size:12px;margin-left:6px}}
form{{margin-top:22px;border-top:1px solid #dcdfe5;padding-top:16px}}
label{{display:block;font-weight:600;margin-bottom:4px}}
input,textarea{{width:100%;padding:8px;border:1px solid #c8ccd4;border-radius:6px;font:inherit}}
button{{margin-top:10px;padding:9px 18px;border:0;border-radius:6px;background:#2f6df6;color:#fff;font:inherit;cursor:pointer}}
nav a{{margin-right:12px}}
</style></head><body>
<nav><a href="/">Forum home</a></nav>
<header><h1>{title}</h1><div class="sub">Thread #{tid} · course forum</div></header>
<p>{opener}</p>
{comments}
<form method="post" action="/thread/{tid}/comment">
  <label for="author">Your name</label>
  <input id="author" name="author" value="">
  <label for="body" style="margin-top:10px">Your comment</label>
  <textarea id="body" name="body" rows="4"></textarea>
  <button type="submit">Post comment</button>
</form>
</body></html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    items = "".join(f'<li><a href="/thread/{i}">{t["title"]}</a></li>'
                    for i, t in THREADS.items())
    return f"<!doctype html><html><body><h1>Course forum</h1><ul>{items}</ul></body></html>"


@app.get("/thread/{thread_id}", response_class=HTMLResponse)
def thread_page(thread_id: int):
    t = THREADS[thread_id]
    rendered = "".join(
        f'<div class="comment"><span class="who">{c["author"]}</span>'
        f'<span class="when">{c["at"]}</span><div>{c["body"]}</div></div>'
        for c in load() if c["thread"] == thread_id)
    return PAGE.format(title=t["title"], tid=thread_id, opener=t["opener"],
                       comments=rendered)


@app.post("/thread/{thread_id}/comment")
def thread_post(thread_id: int, author: str = Form("anonymous"), body: str = Form(...)):
    add(thread_id, author or "anonymous", body)
    return RedirectResponse(f"/thread/{thread_id}", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=6673)
