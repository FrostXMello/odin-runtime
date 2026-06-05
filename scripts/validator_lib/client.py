"""HTTP client with retries and timeouts."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

logger = logging.getLogger("odin.validator")


class ValidatorClient:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay

    def get_json(self, path: str, *, timeout: float | None = None) -> tuple[int, dict[str, Any] | list[Any] | None, str | None]:
        return self._request("GET", path, timeout=timeout)

    def post_json(
        self,
        path: str,
        body: dict[str, Any],
        *,
        timeout: float | None = None,
    ) -> tuple[int, dict[str, Any] | list[Any] | None, str | None]:
        return self._request("POST", path, json_body=body, timeout=timeout)

    def get_raw(self, url: str, *, timeout: float | None = None) -> tuple[int, dict[str, Any] | None, str | None]:
        """GET absolute URL (e.g. Ollama)."""
        last_error: str | None = None
        effective_timeout = timeout if timeout is not None else self.timeout
        for attempt in range(1, self.retries + 1):
            try:
                with httpx.Client(timeout=effective_timeout) as client:
                    response = client.get(url)
                if response.status_code >= 400:
                    return response.status_code, None, response.text[:500]
                try:
                    return response.status_code, response.json(), None
                except json.JSONDecodeError as exc:
                    return response.status_code, None, f"invalid json: {exc}"
            except httpx.HTTPError as exc:
                last_error = str(exc)
                logger.warning("request_failed", extra={"url": url, "attempt": attempt, "error": last_error})
                if attempt < self.retries:
                    time.sleep(self.retry_delay * attempt)
        return 0, None, last_error or "unknown error"

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> tuple[int, dict[str, Any] | list[Any] | None, str | None]:
        url = f"{self.base_url}{path}"
        last_error: str | None = None
        effective_timeout = timeout if timeout is not None else self.timeout

        for attempt in range(1, self.retries + 1):
            try:
                with httpx.Client(timeout=effective_timeout) as client:
                    if method == "GET":
                        response = client.get(url)
                    else:
                        response = client.post(url, json=json_body or {})

                if response.status_code >= 400:
                    return response.status_code, None, response.text[:500]

                try:
                    data = response.json()
                    return response.status_code, data, None
                except json.JSONDecodeError as exc:
                    return response.status_code, None, f"invalid json: {exc}"

            except httpx.HTTPError as exc:
                last_error = str(exc)
                logger.warning(
                    "request_failed",
                    extra={"method": method, "path": path, "attempt": attempt, "error": last_error},
                )
                if attempt < self.retries:
                    time.sleep(self.retry_delay * attempt)

        return 0, None, last_error or "unknown error"

    def health_ping(self) -> bool:
        code, data, err = self.get_json("/api/v1/health", timeout=5.0)
        return code == 200 and data is not None and err is None
