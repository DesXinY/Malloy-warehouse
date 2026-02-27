---
name: malloy-warehouse-migration
description: Assist with Malloy syntax onboarding, semantic modeling, and automated migration from legacy Hive tables plus HiveSQL scheduling into GitHub-managed Malloy projects. Use when tasks involve translating Hive SQL models, building migration inventories, generating Malloy scaffolds, validating metric parity, or defining code-as-semantic warehouse workflows.
---

# Malloy Warehouse Migration

## Objective

Migrate from legacy Hive-centered warehouses to a Malloy-first semantic codebase with repeatable automation.
Deliver modeling standards, migration scripts, and GitHub operating patterns that keep semantic definitions versioned and reviewable.

## Quick Intake

Capture the following before execution:
- Legacy scope: Hive databases, table count, SQL job repositories, scheduler type
- Target scope: Malloy runtime and warehouse connector, repository layout, release cadence
- Parity constraints: KPI definitions, SLA windows, backfill requirements
- Cutover mode: dual-run period, rollback trigger, ownership

## Workflow

1. Inventory legacy warehouse assets.
- Run `scripts/hive_inventory_from_files.sh <legacy_sql_root> <output_dir>`.
- Output `hive_tables.csv` and `hive_jobs.csv` as migration baseline.

2. Build semantic mapping contract.
- Start from `assets/migration-map.template.yaml`.
- Map each Hive table/view/job to Malloy source/query/explore outputs.
- Resolve metric ownership and naming conventions before generating code.

3. Generate Malloy scaffolds.
- Run `scripts/generate_malloy_scaffold.py --mapping <mapping.yaml> --out <malloy_dir>`.
- Review generated files and align style with team conventions.

4. Refactor HiveSQL scheduling to GitHub workflow units.
- Move business logic into Malloy files and keep orchestration minimal.
- Use references from `references/github-operating-model.md` to set PR, CI, and release gates.

5. Validate parity and run dual execution.
- Use validation checklist in `references/validation-and-cutover.md`.
- Compare baseline metrics for agreed windows before cutover.

6. Cut over and deprecate legacy jobs in controlled phases.
- Freeze legacy SQL edits except hotfix path.
- Keep rollback path for one full business cycle.

## References To Load On Demand

- `references/malloy-syntax-quickstart.md`: Use when writing or reviewing Malloy models.
- `references/hive-to-malloy-mapping.md`: Use when translating Hive concepts to Malloy semantics.
- `references/migration-playbook.md`: Use for phase-by-phase migration execution.
- `references/github-operating-model.md`: Use when designing repository and CI controls.
- `references/validation-and-cutover.md`: Use for reconciliation, dual-run, and go-live decisions.

## Automation Scripts

- `scripts/hive_inventory_from_files.sh`: Parse `.sql`/`.hql` files and emit migration inventory CSVs.
- `scripts/generate_malloy_scaffold.py`: Convert mapping file into starter Malloy sources and queries.
- `scripts/migration_readiness_report.py`: Score mapping completeness and output markdown report.

## Execution Rules

- Keep `SKILL.md` procedural and concise; store details in `references/`.
- Prefer deterministic scripts over ad-hoc one-off code for repeated migration operations.
- Always produce explicit artifacts: inventory CSV, mapping YAML, generated Malloy files, reconciliation report.
- Block cutover if critical metrics fail parity thresholds.

## Definition Of Done

- Malloy semantic layer committed in Git with reviewable diffs.
- Legacy-to-Malloy mapping coverage reaches agreed threshold.
- KPI parity checks pass for dual-run window.
- Rollback and ownership documented before production switch.
