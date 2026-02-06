"""FastAPI routes for multi-agent coordination."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from multi_agent.coordinator import Coordinator


class AgentRunRequest(BaseModel):
    """Payload for running the agent pipeline."""

    query: str
    agent_name: Optional[str] = None


class OverrideRequest(BaseModel):
    """Payload for issuing a human override note."""

    message: str


def build_coordinator() -> Coordinator:
    root = Path(__file__).resolve().parents[2]
    storage_root = root / "storage"
    return Coordinator(storage_root)


router = APIRouter()


@router.post("/agents/run")
def run_agents(payload: AgentRunRequest) -> Dict[str, Any]:
    coordinator = build_coordinator()
    return coordinator.run(payload.query, payload.agent_name)


@router.post("/agents")
def run_agents_alias(payload: AgentRunRequest) -> Dict[str, Any]:
    """Alias to run the agent pipeline."""
    coordinator = build_coordinator()
    return coordinator.run(payload.query, payload.agent_name)


@router.get("/agents/state")
def get_state() -> Dict[str, Any]:
    coordinator = build_coordinator()
    return coordinator.state()


@router.get("/agents")
def get_state_alias() -> Dict[str, Any]:
    """Alias to fetch agent state."""
    coordinator = build_coordinator()
    return coordinator.state()


@router.post("/agents/pause")
def pause_agents() -> Dict[str, str]:
    coordinator = build_coordinator()
    coordinator.pause()
    return {"message": "Coordinator paused."}


@router.post("/agents/override")
def override_agents(payload: OverrideRequest) -> Dict[str, str]:
    coordinator = build_coordinator()
    coordinator.override(payload.message)
    return {"message": "Override recorded."}
