from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from ai_os.audit import AuditLogger
from ai_os.memory import MemoryEntry, MemoryStore


def test_decay_slower_for_emotional(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    store = MemoryStore(tmp_path / "memory.json", AuditLogger(log_path))
    now = datetime.utcnow()
    emotional = MemoryEntry(
        id="emotional",
        text="important",
        timestamp=(now - timedelta(days=10)).isoformat() + "Z",
        emotion_score=0.9,
        importance=1.0,
        last_accessed=(now - timedelta(days=10)).isoformat() + "Z",
    )
    neutral = MemoryEntry(
        id="neutral",
        text="neutral",
        timestamp=(now - timedelta(days=10)).isoformat() + "Z",
        emotion_score=0.2,
        importance=1.0,
        last_accessed=(now - timedelta(days=10)).isoformat() + "Z",
    )
    store._write_memories([emotional, neutral])

    store.decay_memories()
    memories = {m.id: m for m in store.list_memories()}

    assert memories["emotional"].importance > memories["neutral"].importance


def test_auto_delete_low_importance(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    store = MemoryStore(tmp_path / "memory.json", AuditLogger(log_path))
    now = datetime.utcnow()
    low = MemoryEntry(
        id="low",
        text="low",
        timestamp=now.isoformat() + "Z",
        emotion_score=0.1,
        importance=0.05,
        last_accessed=(now - timedelta(days=1)).isoformat() + "Z",
    )
    store._write_memories([low])

    store.decay_memories()
    assert store.list_memories() == []

    log_contents = log_path.read_text(encoding="utf-8")
    assert "MEMORY_DELETE" in log_contents
    assert "auto_decay" in log_contents
