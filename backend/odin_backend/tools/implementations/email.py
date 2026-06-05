"""Email tool — controlled, logs when SMTP not configured."""

from typing import Any

from odin_backend.permissions.models import PermissionClass
from odin_backend.tools.base import Tool, ToolContext, ToolResult
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class SendEmailTool(Tool):
    name = "send_email"
    description = "Send email (requires confirmation)"
    permission_class = PermissionClass.CONFIRM_REQUIRED

    async def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        to = params.get("to", "")
        subject = params.get("subject", "")
        body = params.get("body", "")

        if not context.user_confirmed:
            return ToolResult(success=False, error="Email requires user_confirmed=True")

        # Foundation: log intent; SMTP integration in later milestone
        logger.info("email_prepared", to=to, subject=subject, body_len=len(body))
        return ToolResult(
            success=True,
            data={
                "to": to,
                "subject": subject,
                "sent": False,
                "note": "Email logged — configure SMTP for live send",
            },
        )
