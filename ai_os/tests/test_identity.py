from __future__ import annotations

from pathlib import Path

from ai_os.audit import AuditLogger
from ai_os.identity import IdentityStore


def test_identity_persistence(tmp_path: Path) -> None:
    log_path = tmp_path / "audit.log"
    store = IdentityStore(tmp_path / "identity.json", AuditLogger(log_path))
    store.update_identity("likes tea", category="preferences")

    reloaded = IdentityStore(tmp_path / "identity.json", AuditLogger(log_path))
    identity = reloaded.list_identity()

    assert "likes tea" in identity.preferences
    assert identity.versions
