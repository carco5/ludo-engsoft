# Course cheatsheet — terminal · git · Python · the model

One page to keep open during the first week. You don't need to memorise any of this — you need to **recognise** it when an agent does it, and be able to do it yourself when you have to. Render to PDF with `/md2pdf` for handout.

---

## The terminal

| Command | What it does |
|---|---|
| `ls` | list what's in the current folder (`ls -la` = all, with details) |
| `cd foo` | go into folder `foo` · `cd ..` = up one · `cd ~` = home · `cd -` = back |
| `pwd` | print where you are |
| `cat file` | print a file to the screen |
| `less file` | page through a long file (`q` to quit) |
| `nano file` | edit a file (`Ctrl-O` save, `Ctrl-X` exit) |
| `mkdir foo` | make a folder · `rm file` delete · `rm -r foo` delete a folder (careful) |
| `cp a b` / `mv a b` | copy / move (or rename) |
| `head -n 20 file` / `tail` | first / last 20 lines |
| `grep "text" file` | find lines containing `text` |

**The three streams** every program has — they look alike on screen, they are not the same thing:

| Stream | What it carries |
|---|---|
| **stdin** | what the program reads as input |
| **stdout** | the program's normal output |
| **stderr** | error messages — a *separate* channel from stdout |

**Redirection & pipes** — you'll see agents use these constantly:

| Symbol | Meaning |
|---|---|
| `cmd > file` | send stdout **into** a file (overwrite) |
| `cmd >> file` | append stdout to a file |
| `cmd 2> errs.txt` | send **stderr** to a file (the `2` is stderr's number) |
| `cmd1 \| cmd2` | pipe cmd1's stdout into cmd2's stdin |

---

## git — the five verbs that cover 90%

| Command | What it does |
|---|---|
| `git clone <url>` | copy a remote repo to your machine |
| `git status` | what's changed / staged right now |
| `git add <file>` (or `git add .`) | stage changes for the next commit |
| `git commit -m "message"` | save a snapshot with a message |
| `git push` | send your commits up to GitHub |
| `git pull` | bring down what others (or you, elsewhere) pushed |
| `git log --oneline` | history, one line per commit |

**Branches** — try things without breaking what works:

| Command | What it does |
|---|---|
| `git branch` | list branches · `git branch foo` create one |
| `git checkout foo` | switch to branch `foo` (`git checkout -b foo` = create + switch) |
| `git checkout -- file` | throw away uncommitted changes to `file` |

**First-time git setup** (once, ever):
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

---

## Python with `uv`

`uv` runs Python and handles dependencies, so scripts "just run."

| Command | What it does |
|---|---|
| `python3 --version` | check your Python (we want ≥ 3.11) |
| `uv run script.py` | run a script in a managed environment |
| `uv run --with openai --with chromadb python script.py` | run with extra packages, no manual install |
| `uv venv && source .venv/bin/activate` | make + enter a virtual environment (the manual way) |
| `uv sync` | install everything a project's `pyproject.toml` declares |

---

## The model on your machine — Ollama

| Command | What it does |
|---|---|
| `ollama serve` | start the local model server (often already running as an app) |
| `ollama pull qwen3:1.7b` | download a small model (~1.5 GB — runs on almost anything) |
| `ollama run qwen3:1.7b "say hi"` | quick chat from the terminal |
| `ollama list` | what you've got downloaded |

The course talks to Ollama through the **OpenAI-compatible** endpoint at `http://localhost:11434/v1` — no API key, no money, no internet. The same code reaches a cloud model by changing one config line. (That's a lesson, not a shortcut — see Week 2.)

## The coding agent — OpenCode

Install it now (see the setup guide); we drive it properly from Week 2.

| Command | What it does |
|---|---|
| `opencode` | start it in the current folder |
| `opencode --version` | confirm it's installed |

---

## "Am I ready?" — the smoke test

Run these. If all five answer cleanly, you're set for day one:

```bash
python3 --version          # 3.11 or higher
uv --version               # any version
git --version              # any version
ollama run qwen3:1.7b "reply with exactly one short sentence"
opencode --version         # any version
```

If any of them errors, read the message on **stderr**, check the setup guide, and if you're still stuck — **email us before the course starts.**

---

## Where to learn more (optional, if a section was new)

- **Terminal:** *The Missing Semester of Your CS Education* (MIT) — `missing.csail.mit.edu` — the shell + tooling lectures are exactly this floor.
- **git:** the *Pro Git* book (free) — `git-scm.com/book` — read chapters 1–3. Or `learngitbranching.js.org` for a visual, hands-on tour of branches.
- **Python (refresher):** the official tutorial — `docs.python.org/3/tutorial`.
- **`uv`:** `docs.astral.sh/uv`.
- **Ollama:** `ollama.com` → the model library + README.
