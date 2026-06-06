# Operator Shell

Natural-language and shortcut control for the Odin runtime.

## Command center

- `GET /api/v1/runtime/command-center` — quick actions and shortcuts
- `POST /api/v1/runtime/command-center/execute` — run a command

## Example commands

- "show failed missions"
- "resume yesterday's session"
- "search Dynaci payment system"
- "optimize runtime for battery"

## Modules

- `command_router.py` — route typed commands
- `natural_command_parser.py` — intent extraction
- `quick_actions.py` — predefined operator actions
- `semantic_shortcuts.py` — keyboard-style shortcuts
- `runtime_search_router.py` — semantic search integration

## Streaming

Command executions emit `command_executed` on `activity:runtime`.
