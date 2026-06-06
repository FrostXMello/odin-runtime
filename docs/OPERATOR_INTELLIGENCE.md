# Operator Intelligence

Odin v0.38 learns operator context to provide bounded proactive assistance.

## Capabilities

- Active work context modeling
- Workflow and intent prediction
- Project priority inference
- Habit learning
- Interruption awareness during focus sessions

## API

- `POST /api/v1/runtime/operator/infer`
- `POST /api/v1/runtime/research-quality/validate`

Examples:

- "Resume Odin runtime work?"
- "You paused debugging 14 hours ago."

Trace kind: `operator_intent_inferred` on `intelligence:runtime`.
