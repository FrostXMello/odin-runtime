"""Execution profiles — scope boundaries for tools."""

from enum import StrEnum

from pydantic import BaseModel, Field


class SandboxProfile(StrEnum):
    SAFE_BROWSER = "safe_browser"
    FILE_READONLY = "file_readonly"
    DEV_SANDBOX = "dev_sandbox"
    RESTRICTED = "restricted"


PROFILE_ALLOWED_TOOLS: dict[SandboxProfile, set[str]] = {
    SandboxProfile.SAFE_BROWSER: {"get_browser_tabs", "extract_tab_content", "search_web"},
    SandboxProfile.FILE_READONLY: {"read_file", "list_directory", "get_system_info"},
    SandboxProfile.DEV_SANDBOX: {
        "read_file",
        "write_file",
        "list_directory",
        "execute_terminal",
        "search_web",
    },
    SandboxProfile.RESTRICTED: set(),
}


class SandboxPolicy(BaseModel):
    profile: SandboxProfile = SandboxProfile.DEV_SANDBOX
    max_execution_seconds: int = 60
    max_output_bytes: int = 50_000
    working_directory: str = ""
    allowed_tools: set[str] = Field(default_factory=set)

    @classmethod
    def from_profile(cls, profile: SandboxProfile, work_dir: str) -> "SandboxPolicy":
        return cls(
            profile=profile,
            allowed_tools=PROFILE_ALLOWED_TOOLS.get(profile, set()),
            working_directory=work_dir,
        )
