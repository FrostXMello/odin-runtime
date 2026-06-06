# Privacy

Odin v0.37 privacy layer keeps sensitive data on-device.

## Capabilities

- Local credential vault (`SecureCredentials`)
- Encrypted runtime snapshots
- Sensitive-data masking in text pipelines
- Permission audit log
- Runtime permission checks before actions

## API

- `GET /api/v1/runtime/privacy`
- `POST /api/v1/runtime/privacy/filter` — redact PII patterns
- `POST /api/v1/runtime/privacy/check` — permission gate

## Principles

- Local-first only
- No telemetry
- No forced cloud services

Events emit on `privacy:runtime` when filters trigger.
