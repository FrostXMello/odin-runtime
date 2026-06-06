# Cognitive Kernel

`core/cognitive_kernel/` — central cognition orchestration layer above existing runtimes.

App handle: `app.cognitive_kernel`

## Enable

```env
ODIN_COGNITIVE_KERNEL_ENABLED=1
```

## API

- `POST /api/v1/runtime/cognitive-kernel/heartbeat`
- `POST /api/v1/runtime/cognitive-kernel/restore`
- `POST /api/v1/runtime/cognitive-kernel/profile`

## Profiles

`survival` · `lightweight` · `balanced` · `immersive` · `overnight` · `cinematic`

## Channel

`kernel:runtime`

Does not replace `cognitive_daemon`, `cognitive_workspace`, or engineering runtimes — orchestrates them.
