# Developer Integrations (v0.36)

Read-only bridges for VSCode, Cursor, Git, GitHub, terminal, and filesystem watchers.

## Configuration

```env
ODIN_DEVELOPER_INTEGRATIONS_ENABLED=true
```

Git write operations require operator approval.

## API

- `GET /api/v1/runtime/repositories`
- `POST /api/v1/runtime/developer/ingest`
