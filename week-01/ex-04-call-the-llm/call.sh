#!/usr/bin/env bash
# The same Chat Completions call, raw HTTP — no SDK, just curl.
# Defaults to your local Ollama. Override with env vars to hit a cloud provider.
BASE_URL="${OPENAI_BASE_URL:-http://localhost:11434/v1}"
API_KEY="${OPENAI_API_KEY:-ollama}"
MODEL="${MODEL:-ministral-3:8b}"

curl "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$MODEL"'",
    "messages": [
      {"role": "system", "content": "You are a terse assistant."},
      {"role": "user",   "content": "Say hello in one sentence."}
    ],
    "temperature": 0.7
  }'
