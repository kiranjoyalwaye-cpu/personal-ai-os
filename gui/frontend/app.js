const API_BASE = "http://localhost:8000";

async function fetchJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

async function loadMemories() {
  const list = document.getElementById("memory-list");
  list.innerHTML = "";
  const memories = await fetchJson("/memory");
  memories.forEach((memory) => {
    const item = document.createElement("li");
    const info = document.createElement("div");
    info.innerHTML = `<strong>${memory.text}</strong><br /><small>Importance: ${memory.importance} | Emotion: ${memory.emotion_score}</small>`;
    const button = document.createElement("button");
    button.className = "secondary";
    button.textContent = "Delete";
    button.onclick = async () => {
      await fetchJson(`/memory/${memory.id}`, { method: "DELETE" });
      loadMemories();
      loadAudit();
    };
    item.appendChild(info);
    item.appendChild(button);
    list.appendChild(item);
  });
}

async function loadIdentity() {
  const identity = await fetchJson("/identity");
  const preferences = document.getElementById("identity-preferences");
  const personality = document.getElementById("identity-personality");
  const longterm = document.getElementById("identity-longterm");
  [preferences, personality, longterm].forEach((list) => (list.innerHTML = ""));

  identity.preferences.forEach((trait) => {
    const item = document.createElement("li");
    item.textContent = trait;
    preferences.appendChild(item);
  });
  identity.personality_hints.forEach((trait) => {
    const item = document.createElement("li");
    item.textContent = trait;
    personality.appendChild(item);
  });
  identity.long_term_characteristics.forEach((trait) => {
    const item = document.createElement("li");
    item.textContent = trait;
    longterm.appendChild(item);
  });
}

async function loadGoals() {
  const list = document.getElementById("goals-list");
  list.innerHTML = "";
  const goals = await fetchJson("/goals");
  goals.forEach((goal) => {
    const item = document.createElement("li");
    const info = document.createElement("div");
    info.innerHTML = `<strong>${goal.text}</strong><br /><small>${goal.id}</small>`;
    const button = document.createElement("button");
    button.className = "secondary";
    button.textContent = "Remove";
    button.onclick = async () => {
      await fetchJson(`/goals/${goal.id}`, { method: "DELETE" });
      loadGoals();
      loadAudit();
    };
    item.appendChild(info);
    item.appendChild(button);
    list.appendChild(item);
  });
}

async function loadAudit() {
  const log = document.getElementById("audit-log");
  const payload = await fetchJson("/audit");
  log.textContent = payload.lines.join("\n");
}

async function loadAgents() {
  const container = document.getElementById("agent-output-list");
  container.innerHTML = "";
  const state = await fetchJson("/agents");
  const history = state.history || [];
  if (history.length === 0) {
    container.innerHTML = "<p>No agent runs recorded yet.</p>";
    return;
  }
  const latest = history[history.length - 1];
  (latest.responses || []).forEach((response) => {
    const card = document.createElement("div");
    card.className = "agent-card";
    card.innerHTML = `
      <strong>${response.name}</strong> (${response.role})<br />
      <small>${response.timestamp}</small>
      <p>${response.output}</p>
    `;
    container.appendChild(card);
  });
}

async function loadSnapshots() {
  const list = document.getElementById("snapshot-list");
  list.innerHTML = "";
  const payload = await fetchJson("/snapshots");
  payload.snapshots.forEach((snapshot) => {
    const item = document.createElement("li");
    const info = document.createElement("div");
    info.textContent = snapshot;
    const button = document.createElement("button");
    button.className = "secondary";
    button.textContent = "Rollback";
    button.onclick = async () => {
      await fetchJson(`/rollback/${snapshot}`, { method: "POST" });
      await refreshAll();
    };
    item.appendChild(info);
    item.appendChild(button);
    list.appendChild(item);
  });
}

async function refreshAll() {
  await Promise.all([
    loadMemories(),
    loadIdentity(),
    loadGoals(),
    loadAgents(),
    loadAudit(),
    loadSnapshots(),
  ]);
}

document.getElementById("memory-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = document.getElementById("memory-text").value.trim();
  const emotion = Number(document.getElementById("memory-emotion").value);
  const importance = Number(document.getElementById("memory-importance").value);
  if (!text) return;
  await fetchJson("/memory", {
    method: "POST",
    body: JSON.stringify({ text, emotion_score: emotion, importance }),
  });
  event.target.reset();
  await refreshAll();
});

document.getElementById("identity-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const trait = document.getElementById("identity-trait").value.trim();
  const category = document.getElementById("identity-category").value;
  if (!trait) return;
  await fetchJson("/identity", {
    method: "POST",
    body: JSON.stringify({ trait, category }),
  });
  event.target.reset();
  await refreshAll();
});

document.getElementById("goals-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = document.getElementById("goal-text").value.trim();
  if (!text) return;
  await fetchJson("/goals", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
  event.target.reset();
  await refreshAll();
});

document.getElementById("snapshot-create").addEventListener("click", async () => {
  await fetchJson("/snapshot", { method: "POST" });
  await refreshAll();
});

document.getElementById("audit-refresh").addEventListener("click", async () => {
  await loadAudit();
});

refreshAll();
