# Migration Playbook

## Phase 0: Scope And Baseline

- Collect Hive repositories, scheduler jobs, and table catalog.
- Define migration domains and sequence by business criticality.
- Freeze baseline KPIs and reconciliation windows.

Deliverables:
- `hive_tables.csv`
- `hive_jobs.csv`
- migration scope matrix

## Phase 1: Inventory

- Run inventory script against all SQL/HQL paths.
- Group legacy assets by domain and owner.
- Identify dead jobs and duplicate SQL logic.

Gate:
- 100% critical jobs mapped to a migration id.

## Phase 2: Semantic Mapping

- Fill `migration-map.template.yaml`.
- Capture source tables, joins, dimensions, measures, and output queries.
- Mark unresolved fields with owner and due date.

Gate:
- Mapping completeness target reached (recommended >= 90%).

## Phase 3: Scaffold And Refactor

- Generate starter Malloy files from mapping.
- Refactor generated files into team style.
- Add domain tests and snapshot checks where available.

Gate:
- All critical KPIs have canonical measure definitions.

## Phase 4: Dual Run And Parity

- Execute legacy and Malloy outputs in parallel.
- Compare KPI deltas by date and segment.
- Triage deviations and fix semantic definitions.

Gate:
- KPI parity passes agreed threshold for full dual-run window.

## Phase 5: Cutover

- Switch orchestrator to Malloy-backed pipelines.
- Keep rollback toggle for one business cycle.
- Deprecate legacy jobs with explicit sign-off.

Gate:
- No P1 data incidents during stabilization window.
