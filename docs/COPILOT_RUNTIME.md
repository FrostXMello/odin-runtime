# Copilot Production Runtime (v0.34)

The copilot layer now provides a production desktop-assistance pipeline with proactive guidance while keeping the operator safety model unchanged.

## Modules

- `core/copilot/copilot_production_runtime.py` — orchestrator mounted as `app.copilot_production`.
- `core/copilot/realtime_assistant.py` — real-time assistant loop.
- `core/copilot/workflow_prediction.py` — workflow trajectory prediction.
- `core/copilot/attention_model.py` — operator focus and salience estimation.
- `core/copilot/ui_understanding.py` — UI context extraction.
- `core/copilot/contextual_help.py` — just-in-time assistance synthesis.
- `core/copilot/operator_intent.py` — intent classification for workspace actions.
- `core/copilot/proactive_workspace_assistance.py` — proactive suggestion planner.

## Safety and approvals

- Approval model is preserved.
- Simulation mode remains supported.
- Existing runtime safety restrictions are unchanged.
