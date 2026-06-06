# Deployment

Odin v0.37 adds a one-command deployment layer under `odin_backend/deployment/`.

## Quick start

### Linux / macOS

```bash
bash backend/odin_backend/deployment/scripts/install.sh
bash backend/odin_backend/deployment/scripts/start-odin.sh
```

### Windows

```powershell
.\backend\odin_backend\deployment\scripts\install.ps1
.\backend\odin_backend\deployment\scripts\start-odin.ps1
```

## Environment flags

| Flag | Purpose |
|------|---------|
| `ODIN_DEPLOYMENT_ENABLED` | Enable deployment validation on startup |
| `ODIN_PERFORMANCE_ENABLED` | Enable performance optimizer |
| `ODIN_DAILY_DRIVER_ENABLED` | Enable daily workflow suggestions |

## Profiles

Hardware-aware profiles: `ultra_light`, `balanced`, `performance`, `overnight`.

Bootstrap via API: `POST /api/v1/runtime/deployment/bootstrap`

## Backup / restore

- Export: `POST /api/v1/runtime/deployment/export`
- Restore: `POST /api/v1/runtime/deployment/restore`

Snapshots include project registry and guardian state.

## Upgrade migrations

`POST /api/v1/runtime/deployment/upgrade` with `{ "to_version": "0.37.0" }`.
