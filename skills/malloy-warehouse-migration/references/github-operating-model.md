# GitHub Operating Model For Malloy

## 1. Repository Layout

- `malloy/sources/`: base semantic models
- `malloy/queries/`: reusable business queries
- `mappings/`: legacy-to-malloy mapping artifacts
- `checks/`: parity snapshots and quality assertions
- `.github/workflows/`: CI for lint, compile, and parity jobs

## 2. Branch Strategy

- `main`: production-ready semantic layer
- `feature/<domain>-<topic>`: incremental migrations
- `release/<yyyymmdd>`: controlled rollout branches when needed

## 3. Pull Request Controls

- Require code owner review for impacted domain.
- Require CI success: syntax check, scaffold integrity, parity smoke checks.
- Require migration note update for any KPI definition change.

## 4. CI Baseline

- Static checks: file naming, duplicate measure names, unresolved TODO markers.
- Compile checks: Malloy parse and compile command for changed files.
- Regression checks: sampled KPI parity against baseline outputs.

## 5. Release And Rollback

- Tag semantic releases (`semantic-vYYYY.MM.DD`).
- Keep last stable tag as rollback target.
- Record cutover decision with owner, timestamp, and parity report link.
