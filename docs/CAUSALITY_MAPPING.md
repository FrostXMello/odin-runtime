# Causality Mapping

`core/causality_mapping/` — causal execution graphing and failure-chain linkage.

App handle: `app.causality_mapping`

## Enable

```env
ODIN_CAUSALITY_MAPPING_ENABLED=1
```

## API

- `GET /api/v1/runtime/causality-mapping/graph`
- `POST /api/v1/runtime/causality-mapping/failure-chain`
- `GET /api/v1/runtime/failure-lineage`
- `GET /api/v1/runtime/runtime-dependencies`

## Channel

`causality-mapping:runtime`

## Trace kinds

- `causality_graph_generated`
- `failure_chain_traced`
- `runtime_dependency_mapped`
- `reasoning_path_reconstructed`

Operator-visible reasoning lineage with cross-runtime dependency mapping.
