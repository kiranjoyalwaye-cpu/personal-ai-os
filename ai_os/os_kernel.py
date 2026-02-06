"""Core kernel orchestrating memory, identity, goals, and reasoning."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Dict, List

from ai_os.audit import AuditLogger
from ai_os.goals import GoalStore
from ai_os.identity import IdentityStore
from ai_os.memory import MemoryStore
from ai_os.reasoner import Reasoner


class AIOperatingSystem:
    """Kernel that coordinates modules and exposes high-level actions."""

    def __init__(self, storage_root: Path) -> None:
        self.audit = AuditLogger(storage_root / "audit.log")
        self.memory = MemoryStore(storage_root / "memory.json", self.audit)
        self.identity = IdentityStore(storage_root / "identity.json", self.audit)
        self.goals = GoalStore(storage_root / "goals.json", self.audit)
        self.reasoner = Reasoner()

    def handle_user_input(self, text: str) -> str:
        self.audit.log("USER_INPUT", {"text": text})
        self.memory.decay_memories()
        identity = self.identity.list_identity()
        goals = self.goals.list_goals()
        memories = self.memory.retrieve_relevant()
        response = self.reasoner.respond(identity, goals, memories, text)
        self.audit.log("AI_OUTPUT", {"response": response})
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
