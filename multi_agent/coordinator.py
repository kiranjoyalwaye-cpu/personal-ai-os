"""Coordinator orchestrating a transparent multi-agent pipeline."""
from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_os.os_kernel import AIOperatingSystem
from multi_agent.agent_memory import AgentStateStore
from multi_agent.agents import Agent, AgentResponse, default_agents


class Coordinator:
    """Orchestrate agent runs with audit logging and persistence."""

    def __init__(self, storage_root: Path) -> None:
        self.kernel = AIOperatingSystem(storage_root)
        self.audit = self.kernel.audit
        self.state_store = AgentStateStore(storage_root / "agent_state.json")
        self.agents = default_agents()

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.log(action, details)

    def pause(self) -> None:
        self.state_store.set_paused(True)
        self._log("AGENT_PAUSE", {"paused": True})

    def resume(self) -> None:
        self.state_store.set_paused(False)
        self._log("AGENT_PAUSE", {"paused": False})

    def override(self, message: str) -> None:
        self._log("AGENT_OVERRIDE", {"message": message})

    def run(self, query: str, agent_name: Optional[str] = None) -> Dict[str, Any]:
        state = self.state_store.read_state()
        if state.get("paused"):
            return {"status": "paused", "message": "Coordinator is paused."}

        identity = self.kernel.show_identity()
        goals = self.kernel.show_goals()
        memories = [m for m in self.kernel.show_memories()]

        run_id = f"run_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}"
        self._log("AGENT_RUN", {"run_id": run_id, "query": query})

        outputs: List[AgentResponse] = []
        prior_outputs: List[AgentResponse] = []

        pipeline = [
            "Analyst",
            "Planner",
            "Critic",
            "Safety Auditor",
        ]

        for agent in self.agents:
            if agent_name and agent.name != agent_name:
                continue
            if agent.name not in pipeline and agent_name is None:
                continue
            response = agent.respond(query, memories, identity, goals, prior_outputs)
            outputs.append(response)
            prior_outputs.append(response)
            self._log("AGENT_OUTPUT", {"agent": agent.name, "run_id": run_id})

        synthesis = self._synthesize(query, outputs)
        self._log("AGENT_SYNTHESIS", {"run_id": run_id})

        self.state_store.append_run(run_id, query, outputs)

        return {
            "status": "completed",
            "run_id": run_id,
            "query": query,
            "outputs": [response.__dict__ for response in outputs],
            "synthesis": synthesis,
        }

    def _synthesize(self, query: str, outputs: List[AgentResponse]) -> Dict[str, Any]:
        summary = " | ".join(response.output for response in outputs)
        reasoning_chain = [
            {
                "agent": response.name,
                "role": response.role,
                "timestamp": response.timestamp,
                "trace": response.reasoning_trace,
            }
            for response in outputs
        ]
        return {
            "summary": summary,
            "query": query,
            "reasoning_chain": reasoning_chain,
        }

    def state(self) -> Dict[str, Any]:
        return self.state_store.read_state()
