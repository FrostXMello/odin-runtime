"""Federation authentication and security stubs."""

from __future__ import annotations

import hashlib
from typing import Any


class FederationSecurity:
    def __init__(self, settings: Any) -> None:
        self._settings = settings
        self._tokens: dict[str, str] = {}

    def issue_token(self, node_id: str) -> str:
        secret = getattr(self._settings, "federation_shared_secret", "local-only")
        token = hashlib.sha256(f"{node_id}:{secret}".encode()).hexdigest()[:32]
        self._tokens[node_id] = token
        return token

    def verify(self, node_id: str, token: str) -> bool:
        return self._tokens.get(node_id) == token

    def authenticate(self, node_id: str, token: str | None) -> tuple[bool, str]:
        if not token:
            return False, "missing_token"
        if not self.verify(node_id, token):
            return False, "invalid_token"
        return True, "ok"
