# Hive To Malloy Mapping

## 1. Object Mapping

- Hive table -> Malloy `source: ... is table('...')`
- Hive view / derived SQL -> Malloy `query`
- Hive UDF metric logic -> Malloy `measure` with explicit naming
- Hive join blocks -> Malloy `join_one` / `join_many`
- Hive partition filters -> Malloy time dimensions + query constraints

## 2. Scheduling Mapping

- HiveSQL scheduler job -> GitHub workflow unit + execution runner command
- SQL DAG dependencies -> explicit job graph in CI/CD config
- Backfill jobs -> parameterized workflow dispatch with date range inputs

## 3. Semantic Refactor Rules

- Move business logic out of orchestration SQL into Malloy semantic files.
- Keep scheduler code thin: orchestration only, not metric definitions.
- Collapse duplicate Hive metrics into single Malloy measure definitions.
- Tag every generated artifact with owning domain and reviewer.

## 4. Naming Convention

- Source file: `sources/<domain>_<entity>.malloy`
- Query file: `queries/<domain>_<analysis>.malloy`
- Mapping id: `<domain>.<legacy_object>`
- KPI naming: snake_case with business language (`net_revenue`, `active_buyer_cnt`)

## 5. Risk Hotspots

- Late-arriving data behavior may differ between Hive batch logic and Malloy runtime filters.
- NULL handling differences can shift metric parity.
- Many-to-many joins from legacy SQL often require explicit remodeling.
- Hidden scheduler assumptions (timezone, retries, start offsets) must be documented before cutover.
