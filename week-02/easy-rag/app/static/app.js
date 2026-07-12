// EASY-RAG frontend — vanilla JS.
// Same shape as EASY-ASSISTANT, with two additions: an assistant holds MANY
// documents (each ingested into its collection), and every answer shows its
// PROVENANCE — which chunks were used, from which document, with what
// similarity — plus a link to the original file under /static.

const $ = (id) => document.getElementById(id);

let assistants = [];
let current = null;
const histories = {};               // assistant id -> bare turns

async function api(path, opts) {
  const res = await fetch(path, opts);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || res.statusText);
  return body;
}

async function loadConfig() {
  const cfg = await api("/api/config");
  $("model-badge").textContent = `model: ${cfg.model}`;
  $("retrieval-badge").textContent =
    `top-${cfg.top_k} · threshold ${cfg.threshold} · ${cfg.chunking.strategy}`;
  $("a-template").value = cfg.default_template;
}

async function refreshAssistants() {
  assistants = await api("/api/assistants");
  const ul = $("assistant-list");
  ul.innerHTML = "";
  for (const a of assistants) {
    const li = document.createElement("li");
    li.textContent = `${a.name} · ${a.documents.length} doc(s)`;
    li.className = current && current.id === a.id ? "selected" : "";
    li.onclick = () => selectAssistant(a);
    ul.appendChild(li);
  }
}

function selectAssistant(a) {
  current = a;
  histories[a.id] = histories[a.id] || [];
  const dl = $("doc-list");
  dl.innerHTML = "";
  for (const d of a.documents) {
    const li = document.createElement("li");
    li.innerHTML = `<a href="${d.doc_url}" target="_blank">${d.filename}</a>` +
      ` <span class="muted">${d.chunks} chunks · ${d.strategy}</span>`;
    dl.appendChild(li);
  }
  renderMessages();
  refreshAssistants();
}

function provenanceHtml(prov) {
  if (!prov || !prov.length) return "";
  const rows = prov.map(p =>
    `<tr><td>${p.similarity.toFixed(3)}</td>` +
    `<td><a href="${p.doc_url}" target="_blank">${p.title}</a></td>` +
    `<td>#${p.chunk_number}</td>` +
    `<td><a href="${p.md_url}" target="_blank">md</a></td></tr>`).join("");
  return `<table class="prov"><thead><tr><th>similarity</th><th>source</th>` +
         `<th>chunk</th><th></th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderMessages() {
  const div = $("messages");
  div.innerHTML = "";
  for (const m of histories[current?.id] || []) {
    const el = document.createElement("div");
    el.className = `msg ${m.role}` + (m.refused ? " refused" : "");
    el.innerHTML = (m.role === "assistant" ? marked.parse(m.content) : m.content)
                   + provenanceHtml(m.provenance);
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
  if (!file) return alert("choose a document");
  const form = new FormData();
  form.append("file", file);
  $("doc-status").textContent = "ingesting (convert → store → chunk → insert)…";
  try {
    const a = await api(`/api/assistants/${current.id}/documents`, { method: "POST", body: form });
    $("doc-status").textContent = "ingested ✓";
    selectAssistant(a);
  } catch (err) {
    $("doc-status").textContent = "";
    alert(err.message);
  }
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
    const bare = history.filter(m => !m.refused)
                        .map(m => ({ role: m.role, content: m.content }));
    const res = await api(`/api/assistants/${current.id}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ history: bare.slice(0, -1), message: text }),
    });
    history.push({ role: "assistant", content: res.reply,
                   provenance: res.provenance, refused: res.refused });
    renderMessages();
    $("usage").textContent = res.usage
      ? `prompt_tokens: ${res.usage.prompt_tokens} · completion_tokens: ${res.usage.completion_tokens} · total: ${res.usage.total_tokens}`
      : "tokens: 0 — refused before calling the model";
    $("retrieval-info").textContent =
      `${res.retrieval.hits} chunk(s) passed (top-${res.retrieval.top_k}, threshold ${res.retrieval.threshold}) ` +
      `out of ${res.retrieval.collection_chunks} in the collection`;
    $("augmented").textContent = res.augmented_prompt || "— nothing injected (refusal) —";
  } catch (err) {
    history.push({ role: "assistant", content: `⚠️ ${err.message}` });
    renderMessages();
  } finally {
    $("send").disabled = false;
  }
};

loadConfig().then(refreshAssistants);
