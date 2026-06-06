# Autonomous Debugging

Supervised debugging engine with confidence scoring.

## Capabilities

- Stack trace reasoning
- Failure localization
- Root cause analysis
- Debugging strategy selection
- Patch validation and regression detection
- Local failure replay in sandbox

## API

- `POST /api/v1/runtime/debugging/analyze`

All debugging loops require supervision. No unsupervised auto-merge.

Trace kinds: `bug_localized`, `debugging_strategy_selected` on `debugging:runtime`.
