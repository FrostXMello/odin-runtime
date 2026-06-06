# Morning Briefing

`core/morning_briefing/` — startup briefings and overnight summaries.

App handle: `app.morning_briefing`

## Enable

```env
ODIN_MORNING_BRIEFING_ENABLED=1
```

## API

- `GET /api/v1/runtime/morning-briefing`

## Channel

`morning-briefing:runtime`

Generates executive summary, overnight findings, repo alerts, and suggested priorities.
