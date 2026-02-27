# Validation And Cutover

## 1. Parity Rules

- Define metric-level tolerance before dual run.
- Use absolute and relative delta checks.
- Separate blocking KPIs from advisory KPIs.

## 2. Suggested Thresholds

- Revenue and financial KPIs: absolute delta = 0, relative delta <= 0.1%
- Volume KPIs: relative delta <= 0.5%
- Funnel conversion KPIs: relative delta <= 1.0%

Adjust thresholds based on data freshness and legacy known issues.

## 3. Reconciliation Procedure

- Compare by day first, then by business segment.
- Classify mismatches into join cardinality, filter logic, null handling, timezone, and late-arrival categories.
- Fix Malloy semantic definitions first; avoid patching in orchestration.

## 4. Cutover Checklist

- KPI parity passed for agreed dual-run window.
- Backfill outputs validated for representative historical period.
- On-call owner and rollback owner assigned.
- Rollback command and last stable semantic tag confirmed.

## 5. Rollback Trigger

- P1 KPI drift above threshold for two consecutive runs.
- Missing critical table/model in production outputs.
- Repeated pipeline instability beyond SLA.
