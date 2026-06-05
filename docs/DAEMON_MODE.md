# Daemon Mode (v0.34)

Daemon mode enables Odin to run as a persistent background local runtime with restart recovery and lightweight idle behavior.

## Modules

- `core/daemon/daemon_runtime.py` — orchestrator mounted as `app.daemon_runtime`.
- `core/daemon/startup_manager.py` — startup and boot policy hooks.
- `core/daemon/tray_runtime.py` — tray/background lifecycle integration.
- `core/daemon/persistent_sessions.py` — session persistence and restoration.
- `core/daemon/wake_scheduler.py` — scheduled wake and maintenance tasks.
