#!/usr/bin/env python3
"""Build a markdown migration readiness report from mapping and inventory files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


def load_mapping(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(raw)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "YAML input requires PyYAML. Install with: pip install pyyaml "
            "or use JSON mapping file."
        ) from exc
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise SystemExit("Mapping root must be an object.")
    return data


def contains_todo(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return "todo" in lowered or "tbd" in lowered
    if isinstance(value, list):
        return any(contains_todo(item) for item in value)
    if isinstance(value, dict):
        return any(contains_todo(v) for v in value.values())
    return False


def load_inventory_tables(path: Path | None) -> Set[str]:
    if path is None or not path.exists():
        return set()
    tables: Set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            table_name = (row.get("table_name") or "").strip()
            if table_name:
                tables.add(table_name)
    return tables


def safe_list(obj: Any) -> List[Any]:
    return obj if isinstance(obj, list) else []


def readiness_score(
    source_count: int,
    query_count: int,
    mapped_tables: Set[str],
    inventory_tables: Set[str],
    todo_count: int,
    missing_required: int,
) -> int:
    score = 0
    if source_count > 0:
        score += 20
    if query_count > 0:
        score += 20
    if inventory_tables:
        coverage = len(mapped_tables & inventory_tables) / max(len(inventory_tables), 1)
        score += int(30 * coverage)
    else:
        score += 15
    score += max(0, 20 - min(20, todo_count * 2))
    score += max(0, 10 - min(10, missing_required * 3))
    return max(0, min(100, score))


def collect_blockers(sources: Iterable[Dict[str, Any]], queries: Iterable[Dict[str, Any]]) -> List[str]:
    blockers: List[str] = []
    for src in sources:
        if not src.get("name"):
            blockers.append("Source missing `name`.")
        if not src.get("table"):
            blockers.append(f"Source `{src.get('name', 'unknown')}` missing `table`.")
        if not safe_list(src.get("measures")):
            blockers.append(f"Source `{src.get('name', 'unknown')}` has no measures.")
    for qry in queries:
        if not qry.get("name"):
            blockers.append("Query missing `name`.")
        if not qry.get("from"):
            blockers.append(f"Query `{qry.get('name', 'unknown')}` missing `from`.")
    return blockers


def summarize(mapping: Dict[str, Any], inventory_tables: Set[str]) -> Tuple[str, int]:
    sources = [x for x in safe_list(mapping.get("sources")) if isinstance(x, dict)]
    queries = [x for x in safe_list(mapping.get("queries")) if isinstance(x, dict)]
    mapped_tables = {str(src.get("table")) for src in sources if src.get("table")}
    todo_count = sum(1 for section in (sources + queries) if contains_todo(section))
    blockers = collect_blockers(sources, queries)
    missing_required = len(blockers)
    score = readiness_score(
        source_count=len(sources),
        query_count=len(queries),
        mapped_tables=mapped_tables,
        inventory_tables=inventory_tables,
        todo_count=todo_count,
        missing_required=missing_required,
    )

    lines: List[str] = []
    lines.append("# Malloy Migration Readiness Report")
    lines.append("")
    lines.append(f"- Readiness score: **{score}/100**")
    lines.append(f"- Source definitions: **{len(sources)}**")
    lines.append(f"- Query definitions: **{len(queries)}**")
    lines.append(f"- Mapped legacy tables: **{len(mapped_tables)}**")
    if inventory_tables:
        covered = len(mapped_tables & inventory_tables)
        lines.append(f"- Inventory table coverage: **{covered}/{len(inventory_tables)}**")
    else:
        lines.append("- Inventory table coverage: **N/A** (inventory not provided)")
    lines.append(f"- TODO/TBD markers: **{todo_count}**")
    lines.append("")
    lines.append("## Blocking Issues")
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- No blocking structural issues detected.")
    lines.append("")
    lines.append("## Next Actions")
    lines.append("- Resolve all blockers before dual-run.")
    lines.append("- Remove TODO/TBD markers and assign owners.")
    lines.append("- Re-run scaffold generation and parity checks after updates.")
    return "\n".join(lines) + "\n", score


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", required=True, type=Path, help="YAML/JSON mapping file.")
    parser.add_argument(
        "--inventory-tables",
        type=Path,
        default=None,
        help="Optional hive_tables.csv from inventory script.",
    )
    parser.add_argument("--out", required=True, type=Path, help="Output markdown report.")
    args = parser.parse_args()

    mapping = load_mapping(args.mapping)
    inventory_tables = load_inventory_tables(args.inventory_tables)
    report, _ = summarize(mapping, inventory_tables)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"Readiness report written: {args.out}")


if __name__ == "__main__":
    main()
