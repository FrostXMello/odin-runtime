"""Regression: backend modules import and API factory boots without circular imports."""

import importlib
import sys

import pytest


def test_agents_base_imports_without_cycle():
    """agents.base must not pull core.app during import."""
    mod = importlib.import_module("odin_backend.agents.base")
    assert hasattr(mod, "Agent")


def test_tools_runtime_executor_imports_without_cycle():
    mod = importlib.import_module("odin_backend.tools.runtime.executor")
    assert hasattr(mod, "RuntimeToolExecutor")


def test_core_package_does_not_eager_load_app():
    """Importing odin_backend.core must not load core.app before explicit access."""
    if "odin_backend.core" in sys.modules:
        del sys.modules["odin_backend.core"]
    if "odin_backend.core.app" in sys.modules:
        del sys.modules["odin_backend.core.app"]

    import odin_backend.core as core_pkg

    assert "OdinApplication" in core_pkg.__all__
    assert "odin_backend.core.app" not in sys.modules
    _ = core_pkg.OdinApplication
    assert "odin_backend.core.app" in sys.modules


def test_create_api_factory():
    from odin_backend.api.main import create_api

    app = create_api()
    assert app.title
    assert hasattr(app, "router")


@pytest.mark.asyncio
async def test_odin_application_construct():
    from odin_backend.config import Settings
    from odin_backend.core.app import OdinApplication
    from odin_backend.environment_control import OdinEnvironmentConfig

    env = OdinEnvironmentConfig.model_construct(
        valkyrie_enabled=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        autonomy_level=3,
    )
    odin = OdinApplication(
        Settings(runtime_enable_background_loops=False, conscious_loop_enabled=False),
        use_redis=False,
        env_config=env,
    )
    assert odin.kernel is not None
    assert odin.agent_registry is not None
