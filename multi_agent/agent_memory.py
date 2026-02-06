"""Persistent storage for agent state and memory usage."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from multi_agent.agents import AgentResponse


class AgentStateStore:
    """Persist agent interaction state for inspectability."""

    def __init__(self, storage_path: Path) -> None:
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.write_state({"paused": False, "history": []})

    def read_state(self) -> Dict[str, Any]:
        raw = json.loads(self.storage_path.read_text(encoding="utf-8") or "{}")
        return {
            "paused": raw.get("paused", False),
            "history": raw.get("history", []),
        }

    def write_state(self, state: Dict[str, Any]) -> None:
        self.storage_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def append_run(self, run_id: str, query: str, responses: List[AgentResponse]) -> None:
        state = self.read_state()
        run_entry = {
            "run_id": run_id,
            "query": query,
            "responses": [asdict(response) for response in responses],
        }
        state["history"].append(run_entry)
        self.write_state(state)

    def set_paused(self, paused: bool) -> None:
        state = self.read_state()
        state["paused"] = paused
        self.write_state(state)
