"""Identity model for user traits with versioning."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ai_os.audit import AuditLogger


@dataclass
class IdentityProfile:
    """User identity profile that can evolve over time."""

    preferences: List[str]
    personality_hints: List[str]
    long_term_characteristics: List[str]
    versions: List[Dict[str, Any]]


class IdentityStore:
    """Persisted identity store with version history."""

    def __init__(self, storage_path: Path, audit: AuditLogger) -> None:
        self.storage_path = storage_path
        self.audit = audit
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_identity(
                IdentityProfile(
                    preferences=[],
                    personality_hints=[],
                    long_term_characteristics=[],
                    versions=[],
                )
            )

    def _read_identity(self) -> IdentityProfile:
        raw = json.loads(self.storage_path.read_text(encoding="utf-8") or "{}")
        return IdentityProfile(
            preferences=raw.get("preferences", []),
            personality_hints=raw.get("personality_hints", []),
            long_term_characteristics=raw.get("long_term_characteristics", []),
            versions=raw.get("versions", []),
        )

    def _write_identity(self, identity: IdentityProfile) -> None:
        self.storage_path.write_text(
            json.dumps(asdict(identity), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def update_identity(self, trait: str, category: str = "personality_hints") -> IdentityProfile:
        identity = self._read_identity()
        if category not in {"preferences", "personality_hints", "long_term_characteristics"}:
            category = "personality_hints"
        getattr(identity, category).append(trait)
        identity.versions.append(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "category": category,
                "trait": trait,
            }
        )
        self._write_identity(identity)
        self.audit.log("IDENTITY_UPDATE", {"category": category, "trait": trait})
        return identity

    def list_identity(self) -> IdentityProfile:
        return self._read_identity()

    def rollback(self, snapshot: Dict[str, Any]) -> None:
        identity = IdentityProfile(
            preferences=snapshot.get("preferences", []),
            personality_hints=snapshot.get("personality_hints", []),
            long_term_characteristics=snapshot.get("long_term_characteristics", []),
            versions=snapshot.get("versions", []),
        )
        self._write_identity(identity)
        self.audit.log("ROLLBACK", {"scope": "identity"})
