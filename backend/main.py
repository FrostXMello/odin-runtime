"""ODIN backend entry point."""

import uvicorn

from odin_backend.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "odin_backend.api.main:create_api",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
