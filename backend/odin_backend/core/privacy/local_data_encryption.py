"""Local data encryption stubs."""

from __future__ import annotations

import hashlib
from typing import Any


def encrypt_local(data: str, *, key_hint: str = "local") -> dict[str, Any]:
    digest = hashlib.sha256(f"{key_hint}:{data}".encode()).hexdigest()
    return {"ciphertext": digest[:32], "encrypted": True, "local_only": True}
