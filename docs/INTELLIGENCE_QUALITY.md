# Intelligence Quality

Odin v0.38 adds a cognitive quality engine that scores reasoning, plans, and outputs before they propagate.

## Modules

- `reasoning_evaluator` — chain depth and grounding
- `response_grader` — usefulness signals
- `plan_quality` — validate autonomous plans
- `hallucination_barrier` — detect high-risk outputs
- `contradiction_reducer` — dedupe conflicting memory
- `confidence_calibration` — adjusted confidence scores

## API

- `GET /api/v1/runtime/intelligence`
- `POST /api/v1/runtime/intelligence/evaluate`

Trace kinds: `reasoning_quality_scored`, `hallucination_risk_detected` on `intelligence:runtime`.
