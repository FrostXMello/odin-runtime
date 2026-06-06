# Upgrade Governance

`core/evolution_governance/` — approval engine and risk scoring.

## Capabilities

- Risk classification by area and regression probability
- Modification policies (branch isolation, rollback mandatory)
- Operator review packets with expected gains/losses
- Audit trail for all reviews and approvals

## Default

`proposal_only` — Odin proposes; operator must approve before supervised apply.

## API

- `POST /api/v1/runtime/upgrades/review`
- `POST /api/v1/runtime/upgrades/approve`

Direct self-modification is blocked by `safety_constraints`.
