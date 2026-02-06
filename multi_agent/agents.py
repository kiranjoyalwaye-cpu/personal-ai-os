"""Agent definitions for the multi-agent cognitive dashboard."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class AgentResponse:
    """Structured response emitted by an agent."""

    name: str
    role: str
    output: str
    reasoning_trace: List[str]
    timestamp: str
    memory_ids: List[str]


class Agent:
    """Base agent with a deterministic reasoning function."""

    def __init__(self, name: str, role: str) -> None:
        self.name = name
        self.role = role

    def respond(
        self,
        query: str,
        shared_memory: List[Dict[str, Any]],
        identity: Dict[str, Any],
        goals: List[Dict[str, Any]],
        prior_outputs: List[AgentResponse],
    ) -> AgentResponse:
        """Generate a structured response based on provided context."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        memory_ids = [memory["id"] for memory in shared_memory]
        reasoning_trace = [
            f"Received query: {query}",
            f"Identity traits loaded: {len(identity.get('preferences', []))} preferences, "
            f"{len(identity.get('personality_hints', []))} personality hints, "
            f"{len(identity.get('long_term_characteristics', []))} long-term characteristics.",
            f"Goals loaded: {len(goals)}",
            f"Memories referenced: {len(shared_memory)}",
            f"Prior agent outputs: {len(prior_outputs)}",
        ]
        output = (
            f"Role: {self.role}. Focused on query '{query}'. "
            "Reviewing shared memory and goals to provide grounded guidance."
        )
        return AgentResponse(
            name=self.name,
            role=self.role,
            output=output,
            reasoning_trace=reasoning_trace,
            timestamp=timestamp,
            memory_ids=memory_ids,
        )


def default_agents() -> List[Agent]:
    """Return the default agent roster."""
    return [
        Agent("Analyst", "Analyze the query and extract key constraints."),
        Agent("Planner", "Outline a step-by-step response plan."),
        Agent("Critic", "Identify gaps, risks, and missing assumptions."),
        Agent("Researcher", "Surface relevant facts and memory context."),
        Agent("Safety Auditor", "Check safety, compliance, and user control."),
        Agent("Memory Curator", "Summarize which memories should persist."),
    ]
