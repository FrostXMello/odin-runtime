# Operator Experience

`core/daily_operator_experience/` — daily driver desktop orchestration.

## Capabilities

- Startup resume + morning briefing
- Unfinished work recovery
- Repo / workspace restoration
- Idle cognition summaries
- Focus shift tracking
- Evolution review (approval-gated)

## Enable

```env
ODIN_DAILY_OPERATOR_EXPERIENCE_ENABLED=1
```

## API

- `POST /api/v1/runtime/operator-experience/startup`
- `POST /api/v1/runtime/operator-experience/focus`
- `POST /api/v1/runtime/operator-experience/evolution-review`

App handle: `app.daily_operator_experience`

## Traces

`workspace_rehydrated`, `operator_focus_shifted`, `evolution_review_opened` → `operator-experience:runtime`
