"""Notification dispatch."""

from __future__ import annotations

from odin_backend.core.communications.desktop_notifications import format_notification


class NotificationRuntime:
    def notify(self, *, title: str, body: str) -> dict:
        return format_notification(title=title, body=body)
