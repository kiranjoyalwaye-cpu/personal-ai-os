"""Memory engine with persistence, decay, and retrieval."""
from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_os.audit import AuditLogger


@dataclass
class MemoryEntry:
    """Structured memory entry stored on disk."""

    id: str
    text: str
    timestamp: str
    emotion_score: float
    importance: float
    last_accessed: str


class MemoryStore:
    """Persistent memory store with decay and retrieval logic."""

    def __init__(self, storage_path: Path, audit: AuditLogger) -> None:
        self.storage_path = storage_path
        self.audit = audit
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_memories([])

    def _read_memories(self) -> List[MemoryEntry]:
        raw = json.loads(self.storage_path.read_text(encoding="utf-8") or "[]")
        return [MemoryEntry(**entry) for entry in raw]

    def _write_memories(self, memories: List[MemoryEntry]) -> None:
        payload = [asdict(memory) for memory in memories]
        self.storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_memory(self, text: str, emotion_score: float, importance: float) -> MemoryEntry:
        now = datetime.utcnow().isoformat() + "Z"
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            text=text,
            timestamp=now,
            emotion_score=emotion_score,
            importance=importance,
            last_accessed=now,
        )
        memories = self._read_memories()
        memories.append(entry)
        self._write_memories(memories)
        self.audit.log("MEMORY_ADD", {"id": entry.id, "text": text})
        return entry

    def delete_memory(self, memory_id: str) -> bool:
        memories = self._read_memories()
        remaining = [m for m in memories if m.id != memory_id]
        if len(remaining) == len(memories):
            return False
        self._write_memories(remaining)
        self.audit.log("MEMORY_DELETE", {"id": memory_id})
        return True

    def decay_memories(self) -> None:
        memories = self._read_memories()
        now = datetime.utcnow()
        remaining: List[MemoryEntry] = []
        for memory in memories:
            last_accessed = datetime.fromisoformat(memory.last_accessed.replace("Z", ""))
            age_days = max((now - last_accessed).total_seconds() / 86400, 0.0)
            decay_rate = 0.02 if memory.emotion_score >= 0.6 else 0.06
            new_importance = max(memory.importance * math.exp(-decay_rate * age_days), 0.0)
            if new_importance < 0.1:
                self.audit.log(
                    "MEMORY_DELETE",
                    {"id": memory.id, "reason": "auto_decay"},
                )
                continue
            memory.importance = round(new_importance, 4)
            remaining.append(memory)
        self._write_memories(remaining)
        self.audit.log("DECAY", {"remaining": len(remaining)})

    def retrieve_relevant(self, limit: int = 5) -> List[MemoryEntry]:
        memories = self._read_memories()
        now = datetime.utcnow()

        def score(memory: MemoryEntry) -> float:
            timestamp = datetime.fromisoformat(memory.timestamp.replace("Z", ""))
            age_days = max((now - timestamp).total_seconds() / 86400, 0.0)
            recency = 1 / (1 + age_days)
            return (memory.importance * 0.6) + (memory.emotion_score * 0.2) + (recency * 0.2)

        sorted_memories = sorted(memories, key=score, reverse=True)
        selected = sorted_memories[:limit]
        updated_memories = []
        now_iso = datetime.utcnow().isoformat() + "Z"
        for memory in memories:
            if memory.id in {m.id for m in selected}:
                memory.last_accessed = now_iso
            updated_memories.append(memory)
        self._write_memories(updated_memories)
        return selected

    def list_memories(self) -> List[MemoryEntry]:
        return self._read_memories()

    def rollback(self, snapshot: List[Dict[str, Any]]) -> None:
        memories = [MemoryEntry(**entry) for entry in snapshot]
        self._write_memories(memories)
        self.audit.log("MEMORY_DELETE", {"reason": "rollback"})
