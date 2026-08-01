#!/usr/bin/env bash
# Week 3 · Exercise 2, Part 1 — Josep Coll
#
# The four runs the exercise asks for, plus one control of my own.
# Only the FIRST LLM call of each run matters: that is where the registry shows up.
#
#   usage:  MODEL=qwen3:1.7b ./measure.sh
#
# Everything runs against the local Ollama endpoint, so the four numbers come
# from the same tokenizer and are comparable.
set -u

MODEL="${MODEL:-qwen3:1.7b}"
BASE="${OPENAI_BASE_URL:-http://localhost:11434/v1}"
export MODEL OPENAI_BASE_URL="$BASE" OPENAI_API_KEY="${OPENAI_API_KEY:-ollama}"

SIMPLE="what is the capital of France?"
ROBOT="what is the top speed of the Pallet Pup?"
OUT="runs"
mkdir -p "$OUT"

first_tokens () { grep -m1 -oP 'prompt_tokens:\s*\K[0-9]+' "$1"; }

echo "model=$MODEL endpoint=$BASE"
echo

# --- 0 · control (mine): the same question with NO tools at all --------------
#     Not asked for, but without it you cannot separate "the registry" from
#     "the two hand-written tools the plain loop already carries".
uv run python control_no_tools.py "$SIMPLE" | tee "$OUT/0-control-no-tools.log"

# Only the FIRST call of each run is the measurement, so each run gets a wall
# clock: a small model that keeps asking for tools must not hold up the meter.
# `yes n` answers the plain loop's y-gate — nothing is allowed to touch the net.
CAP=600

# --- 1 · baseline: the plain loop (2 hand-written tools), simple question ----
yes n | timeout $CAP uv run python give_the_llm_hands.py "$SIMPLE" > "$OUT/1-baseline-plain-loop.log" 2>&1
echo "1 baseline (plain loop, no MCP)     : $(first_tokens "$OUT/1-baseline-plain-loop.log")"

# --- 2 · server mounted AND used --------------------------------------------
timeout $CAP uv run python agent_with_mcp.py "$ROBOT" > "$OUT/2-mcp-used.log" 2>&1
echo "2 MCP mounted and used              : $(first_tokens "$OUT/2-mcp-used.log")"

# --- 3 · server mounted and NOT used ----------------------------------------
timeout $CAP uv run python agent_with_mcp.py "$SIMPLE" > "$OUT/3-mcp-unused.log" 2>&1
echo "3 MCP mounted, NOT used             : $(first_tokens "$OUT/3-mcp-unused.log")"

# --- 4 · same, with the server grown to six tools ----------------------------
SERVER_SCRIPT=server_6tools.py timeout $CAP uv run python agent_with_mcp.py "$SIMPLE" \
    > "$OUT/4-mcp-unused-6tools.log" 2>&1
echo "4 MCP mounted (6 tools), NOT used   : $(first_tokens "$OUT/4-mcp-unused-6tools.log")"
