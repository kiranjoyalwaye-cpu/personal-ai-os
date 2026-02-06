"""CLI entry point for the Personal AI OS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

from ai_os.os_kernel import AIOperatingSystem


def parse_command(text: str) -> Tuple[str, str]:
    if not text.startswith("/"):
        return "", text
    parts = text.strip().split(" ", 1)
    command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""
    return command, argument


def prompt_float(label: str, default: float) -> float:
    raw = input(f"{label} (default {default}): ").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(0.0, min(1.0, value))


def main() -> None:
    storage_root = Path(__file__).resolve().parent / "storage"
    kernel = AIOperatingSystem(storage_root)

    print("Personal AI OS kernel started. Type /exit to quit.")

    while True:
        user_input = input("> ").strip()
        if not user_input:
            continue
        command, argument = parse_command(user_input)

        if command == "/exit":
            break
        if command == "/remember":
            if not argument:
                print("Usage: /remember text")
                continue
            emotion_score = prompt_float("Emotion score", 0.5)
            importance = prompt_float("Importance", 0.5)
            print(kernel.remember(argument, emotion_score, importance))
            continue
        if command == "/identity":
            if not argument:
                print("Usage: /identity trait")
                continue
            print(kernel.update_identity(argument))
            continue
        if command == "/goal":
            if not argument:
                print("Usage: /goal text")
                continue
            print(kernel.add_goal(argument))
            continue
        if command == "/delete":
            if not argument:
                print("Usage: /delete memory_id")
                continue
            print(kernel.delete_memory(argument))
            continue
        if command == "/show":
            if argument == "memory":
                print(json.dumps(kernel.show_memories(), indent=2))
                continue
            if argument == "goals":
                print(json.dumps(kernel.show_goals(), indent=2))
                continue
            if argument == "identity":
                print(json.dumps(kernel.show_identity(), indent=2))
                continue
            print("Usage: /show memory|goals|identity")
            continue

        response = kernel.handle_user_input(user_input)
        print(response)


if __name__ == "__main__":
    main()
