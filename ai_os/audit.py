"""Audit logging for the Personal AI OS."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class AuditLogger:
    """Append-only audit logger that records every system action."""

    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("")

    def log(self, action: str, details: Dict[str, Any]) -> None:
        """Write an audit entry with a UTC timestamp.

        Log format: timestamp | action | details
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        entry = f"{timestamp} | {action} | {details}"
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(entry + "\n")
