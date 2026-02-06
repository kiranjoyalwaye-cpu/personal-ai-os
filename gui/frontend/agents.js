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

async function loadState() {
  const state = await fetchJson("/agents/state");
  const history = state.history || [];
  if (history.length === 0) {
    document.getElementById("agent-cards").innerHTML = "<p>No agent runs yet.</p>";
    document.getElementById("timeline").innerHTML = "";
    document.getElementById("memory-sync").innerHTML = "";
    return;
  }

  const latest = history[history.length - 1];
  renderAgents(latest.responses || []);
  renderTimeline(latest.responses || []);
  renderMemorySync(latest.responses || []);
}

function renderAgents(responses) {
  const container = document.getElementById("agent-cards");
  container.innerHTML = "";
  responses.forEach((response) => {
    const card = document.createElement("div");
    card.className = "panel";
    card.innerHTML = `
      <h3>${response.name}</h3>
      <p><strong>Role:</strong> ${response.role}</p>
      <p>${response.output}</p>
      <details>
        <summary>Reasoning Trace</summary>
        <ul>${response.reasoning_trace.map((item) => `<li>${item}</li>`).join("")}</ul>
      </details>
      <small>${response.timestamp}</small>
    `;
    container.appendChild(card);
  });
}

function renderTimeline(responses) {
  const timeline = document.getElementById("timeline");
  timeline.innerHTML = "";
  responses.forEach((response) => {
    const item = document.createElement("li");
    item.textContent = `${response.name} → ${response.output}`;
    timeline.appendChild(item);
  });
}

function renderMemorySync(responses) {
  const list = document.getElementById("memory-sync");
  list.innerHTML = "";
  responses.forEach((response) => {
    const item = document.createElement("li");
    item.innerHTML = `<strong>${response.name}</strong>: ${response.memory_ids.join(", ") || "No memories"}`;
    list.appendChild(item);
  });
}

async function runAgents(query, agentName) {
  return fetchJson("/agents/run", {
    method: "POST",
    body: JSON.stringify({ query, agent_name: agentName || null }),
  });
}

async function pauseAgents() {
  return fetchJson("/agents/pause", { method: "POST" });
}

async function overrideAgents(message) {
  return fetchJson("/agents/override", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

async function createSnapshot() {
  return fetchJson("/snapshot", { method: "POST" });
}

async function rollbackLatest() {
  const payload = await fetchJson("/snapshots");
  const latest = payload.snapshots[payload.snapshots.length - 1];
  if (!latest) {
    alert("No snapshots available.");
    return;
  }
  await fetchJson(`/rollback/${latest}`, { method: "POST" });
}

document.getElementById("agent-run-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = document.getElementById("agent-query").value.trim();
  const agentName = document.getElementById("agent-select").value;
  if (!query) return;
  await runAgents(query, agentName);
  await loadState();
});

document.getElementById("pause-btn").addEventListener("click", async () => {
  await pauseAgents();
  await loadState();
});

document.getElementById("snapshot-btn").addEventListener("click", async () => {
  await createSnapshot();
});

document.getElementById("rollback-btn").addEventListener("click", async () => {
  await rollbackLatest();
  await loadState();
});

document.getElementById("override-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = document.getElementById("override-text").value.trim();
  if (!message) return;
  await overrideAgents(message);
  event.target.reset();
});

loadState();
