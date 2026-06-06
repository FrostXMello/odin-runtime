# Code Reasoning

Odin v0.38 adds a real coding copilot layer integrated with developer tools.

## Capabilities

- Repository graph understanding
- Architecture summaries
- Bug localization and debug workflows
- Incremental patch generation
- Code review and refactor advice

## API

- `POST /api/v1/runtime/copilot/analyze-repo`
- `POST /api/v1/runtime/copilot/patch`
- `POST /api/v1/runtime/debugging/assist`

Integrations: Cursor, VSCode, Git, terminal sessions via existing developer integration runtime.

Trace kind: `code_patch_generated` on `copilot:runtime` and `debugging:runtime`.
