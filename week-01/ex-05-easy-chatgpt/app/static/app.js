const messagesEl = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("input");
const contextJson = document.getElementById("context-json");
const usageEl = document.getElementById("usage");
const streamToggle = document.getElementById("stream-toggle");
const modelBadge = document.getElementById("model-badge");

// The whole conversation. This is exactly what gets sent to the model each turn.
const messages = [
  { role: "system", content: "You are a helpful assistant. Answer using Markdown." },
];

function escapeHtml(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function renderMarkdown(text) {
  return window.marked ? marked.parse(text) : escapeHtml(text);
}

function addMessage(role, content) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  div.innerHTML = '<div class="role">' + role + '</div><div class="content"></div>';
  const c = div.querySelector(".content");
  c.innerHTML = role === "assistant" ? renderMarkdown(content) : escapeHtml(content);
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return c;
}

function updateContext(usage) {
  contextJson.textContent = JSON.stringify(messages, null, 2);
  if (usage) {
    usageEl.textContent =
      "tokens — prompt: " + usage.prompt_tokens +
      ", completion: " + usage.completion_tokens +
      ", total: " + usage.total_tokens;
  }
}

async function loadConfig() {
  try {
    const r = await fetch("/api/config");
    const c = await r.json();
    modelBadge.textContent = "model: " + c.model;
  } catch (e) { /* ignore */ }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  messages.push({ role: "user", content: text });
  addMessage("user", text);
  updateContext();
  try {
    if (streamToggle.checked) await sendStreaming();
    else await sendBlocking();
  } catch (err) {
    addMessage("assistant", "**Error:** " + err.message);
  }
});

async function sendBlocking() {
  const contentEl = addMessage("assistant", "…");
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  const data = await r.json();
  if (data.error) { contentEl.textContent = "Error: " + data.error; return; }
  contentEl.innerHTML = renderMarkdown(data.reply);
  messages.push({ role: "assistant", content: data.reply });
  updateContext(data.usage);
}

async function sendStreaming() {
  const contentEl = addMessage("assistant", "");
  let acc = "";
  let usage = null;
  const r = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  });
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop();
    for (const part of parts) {
      const line = part.replace(/^data: /, "").trim();
      if (!line || line === "[DONE]") continue;
      try {
        const obj = JSON.parse(line);
        if (obj.delta) {
          acc += obj.delta;
          contentEl.innerHTML = renderMarkdown(acc);
          messagesEl.scrollTop = messagesEl.scrollHeight;
        }
        if (obj.usage) usage = obj.usage;
        if (obj.error) acc += "\n\n**Error:** " + obj.error;
      } catch (e) { /* ignore partial */ }
    }
  }
  messages.push({ role: "assistant", content: acc });
  updateContext(usage);
}

loadConfig();
updateContext();
