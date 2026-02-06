"""Goal engine with persistence."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ai_os.audit import AuditLogger


@dataclass
class Goal:
    """Goal entry that persists across sessions."""

    id: str
    text: str
    created_at: str
    status: str


class GoalStore:
    """Store and manage goals."""

    def __init__(self, storage_path: Path, audit: AuditLogger) -> None:
        self.storage_path = storage_path
        self.audit = audit
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_goals([])

    def _read_goals(self) -> List[Goal]:
        raw = json.loads(self.storage_path.read_text(encoding="utf-8") or "[]")
        return [Goal(**entry) for entry in raw]

    def _write_goals(self, goals: List[Goal]) -> None:
        self.storage_path.write_text(
            json.dumps([asdict(goal) for goal in goals], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_goal(self, text: str) -> Goal:
        goal = Goal(
            id=str(uuid.uuid4()),
            text=text,
            created_at=datetime.utcnow().isoformat() + "Z",
            status="active",
        )
        goals = self._read_goals()
        goals.append(goal)
        self._write_goals(goals)
        self.audit.log("GOAL_UPDATE", {"action": "add", "id": goal.id, "text": text})
        return goal

    def remove_goal(self, goal_id: str) -> bool:
        goals = self._read_goals()
        remaining = [goal for goal in goals if goal.id != goal_id]
        if len(remaining) == len(goals):
            return False
        self._write_goals(remaining)
        self.audit.log("GOAL_UPDATE", {"action": "remove", "id": goal_id})
        return True

    def list_goals(self) -> List[Goal]:
        return self._read_goals()

    def rollback(self, snapshot: List[Dict[str, Any]]) -> None:
        goals = [Goal(**entry) for entry in snapshot]
        self._write_goals(goals)
        self.audit.log("GOAL_UPDATE", {"reason": "rollback"})
