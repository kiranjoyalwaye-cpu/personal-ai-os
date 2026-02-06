"""Reasoning layer that formats prompts and calls a model API or mock."""
from __future__ import annotations

import os
from dataclasses import asdict
from typing import List

from ai_os.identity import IdentityProfile
from ai_os.goals import Goal
from ai_os.memory import MemoryEntry


class Reasoner:
    """Inject identity, goals, and memory into a prompt and return model output."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")

    def build_prompt(
        self,
        identity: IdentityProfile,
        goals: List[Goal],
        memories: List[MemoryEntry],
        user_input: str,
    ) -> str:
        identity_block = asdict(identity)
        goals_block = [goal.text for goal in goals]
        memory_block = [memory.text for memory in memories]
        prompt = (
            "You are a reasoning engine for a Personal AI OS.\n"
            "Use the injected context to respond with helpful, grounded guidance.\n"
            f"Identity: {identity_block}\n"
            f"Goals: {goals_block}\n"
            f"Relevant Memory: {memory_block}\n"
            f"User Input: {user_input}\n"
            "Response:"
        )
        return prompt

    def respond(
        self,
        identity: IdentityProfile,
        goals: List[Goal],
        memories: List[MemoryEntry],
        user_input: str,
    ) -> str:
        prompt = self.build_prompt(identity, goals, memories, user_input)
        if not self.api_key:
            return (
                "[MOCK RESPONSE]\n"
                "(No OPENAI_API_KEY set, returning a mock reply.)\n"
                f"Prompt summary: {prompt[:200]}..."
            )
        try:
            from openai import OpenAI
        except ImportError:
            return (
                "[MOCK RESPONSE]\n"
                "(OpenAI SDK not installed, returning a mock reply.)\n"
                f"Prompt summary: {prompt[:200]}..."
            )
        client = OpenAI(api_key=self.api_key)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        return response.output_text
