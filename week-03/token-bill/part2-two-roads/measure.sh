#!/usr/bin/env bash
# Week 3 · Exercise 2, Part 2 — Josep Coll
#
# Same task, two roads, one meter.
#
# The meter is a LiteLLM proxy: both agents are pointed at http://localhost:4000/v1,
# so every call either road makes is counted in one place, by one tokenizer.
#
# Before running this, in two other terminals:
#   1)  cd forum && uv run --with fastapi --with uvicorn --with python-multipart python app.py
#   2)  litellm --model ollama/qwen2.5:7b --port 4000
#
# Use a NON-THINKING model. Through the proxy, qwen3's reasoning is stripped and
# `content` arrives empty, so the loop sees a blank answer and stops on turn one.
#
#   usage:  ./measure.sh
set -u

PROXY="${OPENAI_BASE_URL:-http://localhost:4000/v1}"
export OPENAI_BASE_URL="$PROXY" OPENAI_API_KEY="${OPENAI_API_KEY:-sk-anything}"
export MODEL="${MODEL:-qwen2.5:7b}" MAX_TURNS="${MAX_TURNS:-12}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/runs"; mkdir -p "$OUT"

echo "meter=$PROXY  model=$MODEL  turn budget=$MAX_TURNS"
echo

# --- road one: the CLI ------------------------------------------------------
# `yes y` is the human at the y-gate approving each command, as the exercise says.
cd "$HERE/road-cli"
yes y | timeout 3000 uv run python minimal_cli_agent.py \
    "Post the comment 'hello from my CLI agent' to the week-3 thread on the course forum." \
    > "$OUT/road-1-cli.log" 2>&1
echo "road 1 (CLI)     : $(grep -oP 'TOTAL \K.*' "$OUT/road-1-cli.log")"

# --- road two: the browser --------------------------------------------------
# Same task, same wording, so the two bills are for the same work.
cd "$HERE/road-browser"
timeout 5400 uv run python browser_agent.py \
    "Open http://localhost:6673/thread/1 and post the comment 'hello from my browser agent' in the comment form on that page." \
    > "$OUT/road-2-browser.log" 2>&1
echo "road 2 (browser) : $(grep -oP 'TOTAL \K.*' "$OUT/road-2-browser.log")"

echo
echo "--- what landed on the forum ---"
"$HERE/road-cli/forum-cli" read 1

echo
echo "--- the bill, both ways (see tally.py for why two ways) ---"
cd "$HERE" && python3 tally.py
