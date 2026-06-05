# Meta-Reasoning (Prompt 33)

Self-observation and meta-level analysis of Odin's reasoning quality.

## Capabilities

- Reasoning quality analysis with calibration metrics
- Hallucination pattern detection (unsupported claims)
- Confidence calibration measurement
- Recursive loop instability detection (depth > 8)
- Behavioral drift detection (delta > 0.15)
- Meta-level retrospectives

## Output schema

Every analysis includes:
- `uncertainty` — quantified doubt
- `evidence_count` — supporting evidence
- `calibration_quality` — predicted vs actual alignment
- `causal_explanation` — reasoning chain label

## APIs

- `GET /api/v1/runtime/meta-reasoning`
- `GET /api/v1/missions/{id}/meta-analysis`

## Streaming

**Channel:** `meta:runtime`  
**Trace kinds:** `meta_analysis_generated`, `hallucination_detected`

## Safety

Meta-reasoning disabled by default. No autonomous self-modification. All outputs observable and operator-reviewable.
