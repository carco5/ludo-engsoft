// EASY-ASSISTANT frontend — vanilla JS, no framework.
// The page keeps only the BARE turns per assistant; the backend rebuilds the
// augmented prompt (whole file + question) fresh on every turn and returns it,
// so the context pane can show exactly what the model received.

const $ = (id) => document.getElementById(id);

let assistants = [];
let current = null;                 // selected assistant object
const histories = {};               // assistant id -> bare turns [{role, content}]

async function api(path, opts) {
  const res = await fetch(path, opts);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || res.statusText);
  return body;
}

async function loadConfig() {
  const cfg = await api("/api/config");
  $("model-badge").textContent = `model: ${cfg.model}`;
  $("a-template").value = cfg.default_template;
}

async function refreshAssistants() {
  assistants = await api("/api/assistants");
  const ul = $("assistant-list");
  ul.innerHTML = "";
  for (const a of assistants) {
    const li = document.createElement("li");
    li.textContent = a.name + (a.document ? ` · ${a.document.filename}` : " · (no doc)");
    li.className = current && current.id === a.id ? "selected" : "";
    li.onclick = () => selectAssistant(a);
    ul.appendChild(li);
  }
}

function selectAssistant(a) {
  current = a;
  histories[a.id] = histories[a.id] || [];
  $("doc-info").textContent = a.document
    ? `${a.document.filename} (${a.document.chars} chars) — sent whole, every turn`
    : "no document — upload one";
  renderMessages();
  refreshAssistants();
}

function renderMessages() {
  const div = $("messages");
  div.innerHTML = "";
  for (const m of histories[current?.id] || []) {
    const el = document.createElement("div");
    el.className = `msg ${m.role}`;
    el.innerHTML = m.role === "assistant" ? marked.parse(m.content) : m.content;
    div.appendChild(el);
  }
  div.scrollTop = div.scrollHeight;
}

$("create-form").onsubmit = async (e) => {
  e.preventDefault();
  try {
    const a = await api("/api/assistants", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: $("a-name").value,
        system_prompt: $("a-system").value,
        prompt_template: $("a-template").value,
      }),
    });
    $("a-name").value = "";
    selectAssistant(a);
  } catch (err) { alert(err.message); }
};

$("doc-upload").onclick = async () => {
  if (!current) return alert("select an assistant first");
  const file = $("doc-file").files[0];
  if (!file) return alert("choose a .txt file");
  const form = new FormData();
  form.append("file", file);
  try {
    const a = await api(`/api/assistants/${current.id}/document`, { method: "POST", body: form });
    selectAssistant(a);
  } catch (err) { alert(err.message); }
};

$("chat-form").onsubmit = async (e) => {
  e.preventDefault();
  if (!current) return alert("select an assistant first");
  const text = $("input").value.trim();
  if (!text) return;
  $("input").value = "";
  const history = histories[current.id];
  history.push({ role: "user", content: text });
  renderMessages();
  $("send").disabled = true;
  try {
    const res = await api(`/api/assistants/${current.id}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history: history.slice(0, -1), message: text }),
    });
    history.push({ role: "assistant", content: res.reply });
    renderMessages();
    // The disclosure pane: the filled prompt, the messages array, the bill.
    if (res.usage) {
      $("usage").textContent =
        `prompt_tokens: ${res.usage.prompt_tokens} · completion_tokens: ${res.usage.completion_tokens} · total: ${res.usage.total_tokens}`;
    }
    $("augmented").textContent = res.augmented_prompt;
    $("context-json").textContent = JSON.stringify(res.messages_sent, null, 2);
  } catch (err) {
    history.push({ role: "assistant", content: `⚠️ ${err.message}` });
    renderMessages();
  } finally {
    $("send").disabled = false;
  }
};

loadConfig().then(refreshAssistants);
