"""FastAPI routes for the Personal AI OS GUI."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_os.os_kernel import AIOperatingSystem


class MemoryCreate(BaseModel):
    """Payload for creating a memory entry."""

    text: str
    emotion_score: float = Field(ge=0.0, le=1.0)
    importance: float = Field(ge=0.0, le=1.0)


class IdentityUpdate(BaseModel):
    """Payload for updating identity traits."""

    trait: str
    category: str = "personality_hints"


class GoalCreate(BaseModel):
    """Payload for creating goals."""

    text: str


def build_kernel() -> AIOperatingSystem:
    """Create a kernel instance bound to the shared storage directory."""
    root = Path(__file__).resolve().parents[2]
    storage_root = root / "storage"
    return AIOperatingSystem(storage_root)


router = APIRouter()


@router.get("/memory")
def list_memory() -> List[Dict[str, Any]]:
    """Return all stored memories."""
    kernel = build_kernel()
    return kernel.show_memories()


@router.post("/memory")
def create_memory(payload: MemoryCreate) -> Dict[str, Any]:
    """Create a new memory entry."""
    kernel = build_kernel()
    message = kernel.remember(payload.text, payload.emotion_score, payload.importance)
    return {"message": message}


@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: str) -> Dict[str, Any]:
    """Delete a memory entry by id."""
    kernel = build_kernel()
    message = kernel.delete_memory(memory_id)
    if message == "Memory not found.":
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}


@router.get("/identity")
def get_identity() -> Dict[str, Any]:
    """Return current identity data."""
    kernel = build_kernel()
    return kernel.show_identity()


@router.post("/identity")
def update_identity(payload: IdentityUpdate) -> Dict[str, Any]:
    """Add an identity trait."""
    kernel = build_kernel()
    message = kernel.update_identity(payload.trait, payload.category)
    return {"message": message}


@router.get("/goals")
def list_goals() -> List[Dict[str, Any]]:
    """Return all goals."""
    kernel = build_kernel()
    return kernel.show_goals()


@router.post("/goals")
def create_goal(payload: GoalCreate) -> Dict[str, Any]:
    """Create a new goal."""
    kernel = build_kernel()
    message = kernel.add_goal(payload.text)
    return {"message": message}


@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: str) -> Dict[str, Any]:
    """Delete a goal by id."""
    kernel = build_kernel()
    if kernel.goals.remove_goal(goal_id):
        return {"message": f"Goal {goal_id} deleted."}
    raise HTTPException(status_code=404, detail="Goal not found.")


@router.get("/audit")
def get_audit() -> Dict[str, Any]:
    """Return audit log lines."""
    kernel = build_kernel()
    log_path = kernel.audit.log_path
    lines = log_path.read_text(encoding="utf-8").splitlines()
    return {"lines": lines}


@router.get("/snapshots")
def list_snapshots() -> Dict[str, Any]:
    """Return available snapshots."""
    kernel = build_kernel()
    snapshots = []
    for path in sorted(kernel.snapshots_dir.glob("*.json")):
        if path.name == "counter.json":
            continue
        snapshots.append(path.stem)
    return {"snapshots": snapshots}


@router.post("/snapshot")
def create_snapshot() -> Dict[str, Any]:
    """Create a snapshot of current state."""
    kernel = build_kernel()
    snapshot_id = kernel.create_snapshot()
    return {"snapshot_id": snapshot_id}


@router.post("/rollback/{snapshot_id}")
def rollback(snapshot_id: str) -> Dict[str, Any]:
    """Rollback to a snapshot."""
    kernel = build_kernel()
    message = kernel.rollback_snapshot(snapshot_id)
    if message == "Snapshot not found.":
        raise HTTPException(status_code=404, detail=message)
    return {"message": message}
