"""Maps objectives and steps to registered tools and agents."""

from odin_backend.models.task import AgentId

TOOL_AGENT_MAP: dict[str, AgentId] = {
    "read_file": AgentId.MIMIR,
    "write_file": AgentId.MIMIR,
    "list_directory": AgentId.MIMIR,
    "search_web": AgentId.HUGIN,
    "get_system_info": AgentId.HEIMDALL,
    "execute_terminal": AgentId.BROKK,
    "open_browser": AgentId.VALKYRIE,
    "send_email": AgentId.BRAGI,
    "get_browser_tabs": AgentId.VALKYRIE,
    "extract_tab_content": AgentId.HUGIN,
    "summarize_content": AgentId.MUNIN,
    "generate_email": AgentId.BRAGI,
    "take_screenshot": AgentId.VALKYRIE,
}

KEYWORD_TOOL_HINTS: list[tuple[list[str], str, AgentId]] = [
    (["browser", "tab", "page"], "get_browser_tabs", AgentId.VALKYRIE),
    (["summarize", "summary"], "summarize_content", AgentId.MUNIN),
    (["email", "mail"], "generate_email", AgentId.BRAGI),
    (["search", "research", "find online"], "search_web", AgentId.HUGIN),
    (["file", "read", "write"], "read_file", AgentId.MIMIR),
    (["terminal", "command", "shell"], "execute_terminal", AgentId.BROKK),
]


class ToolSelector:
    def agent_for_tool(self, tool_name: str) -> AgentId:
        return TOOL_AGENT_MAP.get(tool_name, AgentId.VALKYRIE)

    def suggest_tools(self, objective: str) -> list[tuple[str, AgentId]]:
        lower = objective.lower()
        suggestions: list[tuple[str, AgentId]] = []
        for keywords, tool, agent in KEYWORD_TOOL_HINTS:
            if any(k in lower for k in keywords):
                suggestions.append((tool, agent))
        return suggestions
