from __future__ import annotations

from pathlib import Path

from ai_os.audit import AuditLogger
from ai_os.goals import GoalStore


def test_goal_persistence(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    store = GoalStore(tmp_path / "goals.json", AuditLogger(log_path))
    goal = store.add_goal("finish project")

    reloaded = GoalStore(tmp_path / "goals.json", AuditLogger(log_path))
    goals = reloaded.list_goals()

    assert any(item.id == goal.id for item in goals)


def test_goal_removal(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    store = GoalStore(tmp_path / "goals.json", AuditLogger(log_path))
    goal = store.add_goal("temporary")

    assert store.remove_goal(goal.id) is True
    assert store.list_goals() == []
