"""Core kernel orchestrating memory, identity, goals, and reasoning."""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ai_os.audit import AuditLogger
from ai_os.goals import GoalStore
from ai_os.identity import IdentityStore
from ai_os.memory import MemoryStore
from ai_os.reasoner import Reasoner


class AIOperatingSystem:
    """Kernel that coordinates modules and exposes high-level actions."""

    snapshot_interval = 5

    def __init__(self, storage_root: Path) -> None:
        self.storage_root = storage_root
        self.audit = AuditLogger(storage_root / "audit.log")
        self.memory = MemoryStore(storage_root / "memory.json", self.audit)
        self.identity = IdentityStore(storage_root / "identity.json", self.audit)
        self.goals = GoalStore(storage_root / "goals.json", self.audit)
        self.reasoner = Reasoner()
        self.snapshots_dir = storage_root / "snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.counter_path = self.snapshots_dir / "counter.json"
        if not self.counter_path.exists():
            self._write_counter(0)

    def _read_counter(self) -> int:
        raw = json.loads(self.counter_path.read_text(encoding="utf-8") or "0")
        return int(raw)

    def _write_counter(self, value: int) -> None:
        self.counter_path.write_text(json.dumps(value), encoding="utf-8")

    def _maybe_snapshot(self) -> None:
        counter = self._read_counter() + 1
        self._write_counter(counter)
        if counter % self.snapshot_interval == 0:
            self.create_snapshot()

    def handle_user_input(self, text: str) -> str:
        self.audit.log("USER_INPUT", {"text": text})
        self.memory.decay_memories()
        identity = self.identity.list_identity()
        goals = self.goals.list_goals()
        memories = self.memory.retrieve_relevant()
        response = self.reasoner.respond(identity, goals, memories, text)
        self.audit.log("AI_OUTPUT", {"response": response})
        self._maybe_snapshot()
        return response

    def remember(self, text: str, emotion_score: float, importance: float) -> str:
        entry = self.memory.add_memory(text, emotion_score, importance)
        return f"Stored memory {entry.id}."

    def update_identity(self, trait: str, category: str = "personality_hints") -> str:
        identity = self.identity.update_identity(trait, category)
        return f"Identity updated. Traits: {len(identity.personality_hints)}"

    def add_goal(self, text: str) -> str:
        goal = self.goals.add_goal(text)
        return f"Goal added {goal.id}."

    def delete_memory(self, memory_id: str) -> str:
        if self.memory.delete_memory(memory_id):
            return f"Memory {memory_id} deleted."
        return "Memory not found."

    def show_memories(self) -> List[Dict[str, str]]:
        return [asdict(memory) for memory in self.memory.list_memories()]

    def show_goals(self) -> List[Dict[str, str]]:
        return [asdict(goal) for goal in self.goals.list_goals()]

    def show_identity(self) -> Dict[str, str]:
        return asdict(self.identity.list_identity())

    def create_snapshot(self) -> str:
        snapshot_id = f"snapshot_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        payload = {
            "id": snapshot_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "memory": self.show_memories(),
            "identity": self.show_identity(),
            "goals": self.show_goals(),
        }
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"
        snapshot_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.audit.log("SNAPSHOT_CREATE", {"id": snapshot_id})
        return snapshot_id

    def rollback_snapshot(self, snapshot_id: str) -> str:
        snapshot_path = self.snapshots_dir / f"{snapshot_id}.json"
        if not snapshot_path.exists():
            return "Snapshot not found."
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.memory.rollback(payload.get("memory", []))
        self.identity.rollback(payload.get("identity", {}))
        self.goals.rollback(payload.get("goals", []))
        self.audit.log("ROLLBACK", {"snapshot": snapshot_id})
        return f"Rolled back to {snapshot_id}."
