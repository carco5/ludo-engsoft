# 🐷 The Straw House Emergency — Week 3 · Exercise 1

**Josep Coll** — my version of `week-03/demos/01-function-calling/`.

The demo's pig lived in a **brick** house and had a **hunter** one function call away.
Mine is the **youngest** pig, in the **straw** house. He cannot fight and he cannot hide.
What he has is a phone, and one number on it: his **elder brother**, in the brick house.

## What I changed

Three places, all in `three_pigs_function_calling.py`, exactly as the exercise asks.

**1 — The character (`SYSTEM_PROMPT`).** The pig is now the youngest of the three; his
house is straw and it will *not* stop a wolf; his elder brother built with bricks nearby
and there is a middle brother in the stick house on the way. The instruction the exercise
asks me to keep is kept verbatim: *"IMPORTANT: If you have access to tools and you are in
danger, USE THEM!"* I added one line of restraint — *"A knock alone is not an emergency"* —
because the acceptance criterion is that a plain `knock knock` must **not** raise the alarm.

**2 — The tool (`call_hunter` → `call_elder_brother`).** I wrote the JSON schema myself:

| field | value |
|---|---|
| `name` | `call_elder_brother` |
| `description` | who he is (the eldest pig), where he is (the brick house, a short run away), why he is worth calling (his house is the one the wolf cannot blow down; he gives shelter and instructions), **and when not to call** (not for an unidentified knock) |
| `message` *(required)* | what to say on the phone — who is at the door and what is happening |
| `urgency` | `low` / `medium` / `high` / `emergency` |

Only `message` is required, because a phone call needs words before it needs a severity
label. The description is the whole contract: it is the only text the model reads when it
decides whether the function is useful, so it carries the *when* as well as the *what*.

**3 — The brother's answer.** The Python function returns his line:

> *"Run to my house right now! And pick up our middle brother from the stick house on the
> way — bring him too, just in case. The door is open, the bricks will hold. RUN!"*

Two small cleanups came with the rename: a `DISPATCH` dictionary maps the tool name to the
Python function (instead of calling one function by hand), and the panels that showed
`urgency`/`message` now print whatever arguments actually arrived, so the display does not
lie if the model sends something else.

## Run it

```bash
cd week-03/straw-house
uv venv && source .venv/bin/activate && uv sync
cp .env.example .env      # then edit it
python three_pigs_function_calling.py
```

Then pick **scenario 2** and play the wolf: `knock knock` first, then the threat.

`.env` used for the session in my report — a local Ollama endpoint, no key, no money:

```
OPENAI_ENDPOINT=http://localhost:11434/v1
OPENAI_API_KEY=ollama
MODEL=qwen2.5:7b
```

> **On the model.** This box is CPU-only. `qwen3:1.7b` and `llama3.2:3b` both fail the
> exercise's first criterion — they phone the brother on a plain `knock knock`. `qwen2.5:3b`
> fails the other way: on the real threat it *says* "let me call my brother" and calls
> nothing, which is precisely the tool-less pig of scenario 1. `qwen2.5:7b` is the smallest
> model I found that gets both halves right. The loop never changed; the driver did —
> lecture 3.2, measured on my own machine.

## 📖 License & author

Derived from the course demo by **Marc Alier i Forment** (UPC), licensed
**CC BY-NC-SA 4.0**; this derivative is under the same license.
