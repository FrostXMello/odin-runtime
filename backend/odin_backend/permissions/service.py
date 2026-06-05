"""Permission evaluation — never allow uncontrolled execution."""

from odin_backend.models.task import AgentId
from odin_backend.permissions.models import PermissionClass, PermissionDecision


# Default tool permission map — extend via config/registry at runtime
DEFAULT_TOOL_PERMISSIONS: dict[str, PermissionClass] = {
    "read_file": PermissionClass.SAFE,
    "write_file": PermissionClass.CONFIRM_REQUIRED,
    "list_directory": PermissionClass.SAFE,
    "search_web": PermissionClass.SAFE,
    "get_system_info": PermissionClass.SAFE,
    "get_browser_tabs": PermissionClass.SAFE,
    "extract_tab_content": PermissionClass.SAFE,
    "summarize_content": PermissionClass.SAFE,
    "generate_email": PermissionClass.SAFE,
    "summarize_tabs": PermissionClass.SAFE,
    "take_screenshot": PermissionClass.CONFIRM_REQUIRED,
    "open_browser": PermissionClass.CONFIRM_REQUIRED,
    "send_email": PermissionClass.CONFIRM_REQUIRED,
    "execute_terminal": PermissionClass.RESTRICTED,
    "delete_file": PermissionClass.RESTRICTED,
    "system_shutdown": PermissionClass.BLOCKED,
}


class PermissionService:
    """Evaluates whether an agent may invoke a tool."""

    def __init__(
        self,
        tool_permissions: dict[str, PermissionClass] | None = None,
        agent_overrides: dict[AgentId, set[str]] | None = None,
    ) -> None:
        self._tool_permissions = dict(DEFAULT_TOOL_PERMISSIONS)
        if tool_permissions:
            self._tool_permissions.update(tool_permissions)
        self._agent_overrides = agent_overrides or {}

    def register_tool_permission(self, tool_name: str, permission_class: PermissionClass) -> None:
        self._tool_permissions[tool_name] = permission_class

    def check(
        self,
        tool_name: str,
        agent_id: AgentId,
        *,
        user_confirmed: bool = False,
    ) -> PermissionDecision:
        permission_class = self._tool_permissions.get(tool_name, PermissionClass.RESTRICTED)

        if permission_class == PermissionClass.BLOCKED:
            return PermissionDecision(
                allowed=False,
                permission_class=permission_class,
                tool_name=tool_name,
                agent_id=agent_id,
                reason=f"Tool '{tool_name}' is blocked by policy.",
            )

        if permission_class == PermissionClass.RESTRICTED:
            allowed_agents = self._agent_overrides.get(agent_id, set())
            if tool_name not in allowed_agents:
                return PermissionDecision(
                    allowed=False,
                    permission_class=permission_class,
                    tool_name=tool_name,
                    agent_id=agent_id,
                    reason=f"Agent '{agent_id}' lacks restricted access to '{tool_name}'.",
                )

        if permission_class == PermissionClass.CONFIRM_REQUIRED and not user_confirmed:
            return PermissionDecision(
                allowed=False,
                permission_class=permission_class,
                tool_name=tool_name,
                agent_id=agent_id,
                reason="Human confirmation required.",
                requires_confirmation=True,
            )

        return PermissionDecision(
            allowed=True,
            permission_class=permission_class,
            tool_name=tool_name,
            agent_id=agent_id,
        )
