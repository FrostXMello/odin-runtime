# Context Fusion

Odin v0.40 merges IDE, terminal, browser, and docs into a unified active context.

## Capabilities

- Cross-application context merge
- Attention graph and priority engine
- Intent continuity and interruption recovery
- Session fusion with local-only processing

## API

- `POST /api/v1/runtime/context/fuse`
- `GET /api/v1/runtime/context`

Trace kinds: `live_context_fused`, `active_context_updated` on `context:runtime`.

Privacy: local-only, configurable exclusions, no cloud telemetry.
