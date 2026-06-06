# Presence System

Bounded embodied presence in `core/presence/`.

## Design principles

- **No fake consciousness claims**
- **No manipulative behavior**
- Simulated emotional states are always labeled `simulated: true`
- Operator sync scoring for collaborative pacing

## Modules

- `emotion_model` — bounded mood from interaction energy
- `expression_engine` — visual metadata for operator UI
- `interaction_energy`, `conversational_rhythm`, `ambient_state`
- `personality_projection` — stable trait continuity

## API

- `GET /api/v1/runtime/presence`
- `POST /api/v1/runtime/presence/update`
- `GET /api/v1/runtime/personality`

## Traces

- `presence_shifted`
- `emotional_state_updated`

Channel: `presence:runtime`
