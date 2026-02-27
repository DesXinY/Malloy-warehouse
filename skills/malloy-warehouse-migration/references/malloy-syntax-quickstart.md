# Malloy Syntax Quickstart

## 1. Core Concepts

- `source`: Define base dataset from table or query.
- `dimension`: Define categorical field or transformed attribute.
- `measure`: Define aggregations and KPI metrics.
- `query`: Define reusable analytical result sets.
- `join_one` / `join_many`: Define semantic relationships.

## 2. Minimal Source Pattern

```malloy
source: orders is table('warehouse.orders') extend {
  primary_key: order_id

  dimension: order_date is order_ts.day
  dimension: channel is sales_channel

  measure: order_cnt is count()
  measure: gross_revenue is sum(amount)
}
```

## 3. Reusable Query Pattern

```malloy
query: daily_orders is orders -> {
  group_by: order_date
  aggregate:
    order_cnt
    gross_revenue
}
```

## 4. Join Pattern

```malloy
source: orders_enriched is orders extend {
  join_one: customers is table('warehouse.customers')
    with orders.customer_id = customers.customer_id

  dimension: customer_tier is customers.tier
}
```

## 5. Migration Style Rules

- Keep table names stable between Hive and Malloy source names where possible.
- Define business metrics once in `source` and reuse them in downstream `query`.
- Prefer explicit dimensions for time grains (`day`, `week`, `month`) over inline expressions.
- Keep file granularity small: one major source per file for easy review.

## 6. Review Checklist

- Every KPI has one canonical `measure` definition.
- Join cardinality matches business expectation.
- Time grain logic matches legacy SQL outputs.
- Query outputs are named by business domain, not technical pipeline step.
