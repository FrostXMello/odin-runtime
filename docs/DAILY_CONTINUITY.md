# Daily Continuity

`core/daily_continuity/` — daily and weekly workflow continuity.

## Capabilities

- Daily memory recording
- Unfinished work tracking
- Abandoned session detection
- Resume summaries and workflow predictions
- Project presence

## API

- `GET /api/v1/runtime/daily-continuity/resume`
- `POST /api/v1/runtime/daily-continuity/unfinished`

Traces: `unfinished_work_detected`, `workflow_prediction_generated`
