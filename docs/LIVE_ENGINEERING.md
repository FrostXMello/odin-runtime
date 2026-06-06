# Live Engineering

`core/live_engineering/` — real-time engineering companion mode.

## Integrations

- `context_fusion` — IDE + terminal merge
- `workstation_awareness` — activity observation
- Engineering memory and repository graph (via existing runtimes)

## Capabilities

- Live repo awareness
- Debug assistant hints
- Terminal reasoning
- Supervised patch suggestions (`approval_required`, `no_main_commit`)

## API

- `GET /api/v1/runtime/live-engineering`
- `POST /api/v1/runtime/live-engineering/session`

Traces: `live_engineering_detected`, `live_patch_suggested`

Channel: `live-engineering:runtime`
