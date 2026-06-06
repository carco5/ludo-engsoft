# Getting your machine ready — environment setup

This guide gets your computer ready for the course. Do it in the week before we start, so that if something goes wrong you have time to ask for help. Budget **30–40 minutes** — most of that is just waiting for downloads. At the end there is a **smoke test**: five commands that, if they all work, mean you are ready. If anything fails, read the error message and **email us before day one** — a week of runway only helps if you use it.

You do not need to understand every detail today. You need the tools installed and the smoke test passing. As you go, if a word or an idea is new, ask ChatGPT, Claude, or your coding agent to explain it — that habit *is* part of the course.

## First: what is "the terminal", and why does this course live in it?

The **terminal** (also called the *shell* or the *command line*) is a text window where you type commands to your computer instead of clicking buttons. If you have lived in graphical apps and notebooks, it can feel like a step backwards. It is not. It is where real software work happens — and, more importantly for us, **it is where AI coding agents work.** An agent builds your software by running terminal commands; your job is to read what it did, catch its mistakes, and steer it. If you cannot read the terminal, you cannot supervise an agent — and supervising the agent is the whole skill this course teaches.

You do not need to be a terminal expert. You need a handful of commands and the confidence to read output. The companion **cheatsheet** (`cheatsheet.md`) lists every command you'll need; keep it open during the first week. If you want a proper, friendly grounding, the MIT lecture series *The Missing Semester of Your CS Education* is the best free resource: <https://missing.csail.mit.edu>.

## The tools you'll install, and what each one is for

You will install five things. Here is what each one is and why it matters — install instructions for your operating system come after.

- **Python 3.11+** — the programming language the course examples are written in. You will *read* a lot of Python and *edit* some; you will rarely write it from scratch. Version 3.11 or newer matters because some libraries we use need it. Learn more / refresher: <https://docs.python.org/3/tutorial/>.

- **`uv`** — a tool that runs Python programs and manages their dependencies (the extra libraries a program needs). Without it, "it works on my machine but not yours" is a constant problem, because everyone has different libraries installed. `uv` makes a program bring its own dependencies, so it just runs. One command (`uv run …`) and you don't think about it again. Learn more: <https://docs.astral.sh/uv/>.

- **git** — the version-control system that records the history of your code and lets you share it. In this course your deliverables *live in a git repository*: you build something, you `commit` it (save a snapshot), and you `push` it to GitHub so we can see it. The AI agent will often commit for you — which is exactly why you need to understand git well enough to look at what it did and undo it when it does something wrong. New to git? Read chapters 1–3 of the free *Pro Git* book (<https://git-scm.com/book>), or play through the visual tutorial at <https://learngitbranching.js.org>.

- **Ollama** + a small model — Ollama runs a language model **on your own computer**, with no API key, no cost, and no internet needed after the first download. We use it for the course *experiments* — so you can run things freely without a bill. The small model we default to (`qwen3:1.7b`) is about 1.5 GB and runs on almost any laptop. Learn more and browse other models: <https://ollama.com>.

- **OpenCode** — the AI coding agent you will *drive* from Week 2 onward to build your software. **Important:** a coding agent is only as good as the model behind it, and a *tiny* local model is **not** good enough to drive one through real work. So OpenCode needs a **capable** model — a strong endpoint your course provides (if it has one), or your own subscription to a capable agentic model (Qwen, DeepSeek, Pi, MiniMax; Claude if you are serious about this). Keep the small local Ollama model for the *experiments*; use the capable model for *driving the agent*. (We explain this two-model split again in Week 2 — it confuses everyone at first, so don't worry if it isn't fully clear yet.) Learn more: <https://opencode.ai>.

Now follow the section for **your** operating system.

---

## macOS

macOS comes with a terminal (open **Terminal.app**, or install **iTerm2** if you prefer). We install everything with **Homebrew**, the standard package manager for macOS — it's the tool that downloads and installs developer software for you. If you don't have it yet, install it with this one line (it will explain what it's doing and ask for your password):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

(More on Homebrew: <https://brew.sh>.) Then install the tools:

```bash
# Python, git, and uv
brew install python@3.11 git
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ollama — installs the app; it then runs quietly in your menu bar
brew install ollama
ollama serve &                 # or just launch the Ollama app from Applications
ollama pull qwen3:1.7b         # downloads the small model (~1.5 GB) — be patient

# OpenCode — the coding agent
curl -fsSL https://opencode.ai/install | bash
```

After installing, **open a new terminal window** so that `uv` and `opencode` are found (the installers add them to your `PATH`, the list of places your terminal looks for commands, and that only takes effect in a fresh window).

---

## Linux (Ubuntu / Debian)

You already have a real terminal. Install the system basics with `apt` (Ubuntu's package manager), then the rest:

```bash
# System basics
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git curl wget

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:1.7b         # the small model (~1.5 GB)

# OpenCode — the coding agent
curl -fsSL https://opencode.ai/install | bash
```

Then open a new terminal (or run `source ~/.bashrc`) so the new tools are on your `PATH`.

---

## Windows — you need a real Unix terminal (PowerShell will not do)

This course runs in a **Unix** terminal (the kind macOS and Linux have). Windows' built-in **PowerShell is a different system** — many of our commands and tools simply don't work there, and fighting that difference all term is not worth it. So on Windows you run a small Linux *inside* Windows. The easy, recommended way is **WSL2** (the Windows Subsystem for Linux) — it gives you a genuine Ubuntu terminal that behaves exactly like the Linux section above, with no separate virtual machine to manage.

1. Open **PowerShell as Administrator** (right-click → "Run as administrator") and run:
   ```powershell
   wsl --install
   ```
   Reboot when it asks. By default this installs Ubuntu. (Microsoft's official guide, if you want the details: <https://learn.microsoft.com/windows/wsl/install>.)
2. From the Start menu, launch **Ubuntu**. The first time, it asks you to create a Linux username and password — these are separate from your Windows login.
3. Inside that Ubuntu terminal, follow the **Linux (Ubuntu / Debian)** section above. Everything works the same.

> **Can't run WSL2?** (Very old hardware, or a locked-down work laptop that won't allow it.) Don't fight it alone — email us before the course starts and we'll help you find a working setup.

---

## Do one git round-trip now (so it isn't new on day one)

git has a small vocabulary you'll use constantly. Practising it once, now, on a throwaway repository means it won't be unfamiliar when your grade depends on it. First, tell git who you are — you only ever do this once:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Then clone a public repository, look inside it, and read its history:

```bash
git clone https://github.com/octocat/Hello-World.git   # copy a repo to your machine
cd Hello-World                                          # go into it
git status                                              # what's changed right now?
git log --oneline                                       # the history, one line per commit
```

That is the rhythm you'll repeat all term: **clone → change → `add` → `commit` → `push`.** If any of these words are fuzzy, the *Pro Git* chapters linked above explain each one clearly.

---

## Smoke test — are you ready?

Run these five commands. Each one checks that a tool is installed and working. If all five answer cleanly, you're set for day one:

```bash
python3 --version    # should print 3.11 or higher
uv --version         # any version
git --version        # any version
ollama run qwen3:1.7b "reply with exactly one short sentence"
opencode --version   # any version
```

The fourth command is the interesting one: the first time you run it, it finishes downloading the model, and then it prints a single sentence **generated on your own computer** — no internet, no account, no cost. When you see that sentence appear, the hard part of setup is done.

**If any command gives an error:** read the message carefully (errors are printed on a separate channel called `stderr` — see the cheatsheet), make sure you opened a fresh terminal after installing, and try asking ChatGPT or Claude to explain the exact error text. If you're still stuck, **email us before the course starts.**
