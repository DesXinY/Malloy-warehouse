#!/usr/bin/env python3
"""Generate Malloy source/query scaffold files from mapping configuration."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List


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


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_").lower() or "unnamed"


def iter_items(items: Iterable[Any]) -> Iterable[Dict[str, Any]]:
    for item in items:
        if isinstance(item, str):
            yield {"name": item, "expr": item}
        elif isinstance(item, dict):
            yield item
        else:
            raise SystemExit(f"Unsupported item format: {item!r}")


def render_source(item: Dict[str, Any]) -> str:
    name = item.get("name")
    table = item.get("table")
    if not name or not table:
        raise SystemExit("Each source needs both `name` and `table`.")

    lines: List[str] = [f"source: {name} is table('{table}') extend {{"]
    if item.get("primary_key"):
        lines.append(f"  primary_key: {item['primary_key']}")

    for dim in iter_items(item.get("dimensions", [])):
        lines.append(f"  dimension: {dim['name']} is {dim.get('expr', dim['name'])}")

    for measure in iter_items(item.get("measures", [])):
        lines.append(f"  measure: {measure['name']} is {measure.get('expr', measure['name'])}")

    for join in item.get("joins", []):
        if not isinstance(join, dict):
            raise SystemExit(f"Join must be object: {join!r}")
        relationship = join.get("relationship", "one")
        keyword = "join_many" if relationship == "many" else "join_one"
        join_name = join.get("name")
        on_clause = join.get("on")
        target_source = join.get("target_source")
        target_table = join.get("table")

        if not join_name or not on_clause:
            raise SystemExit(f"Join requires `name` and `on`: {join!r}")

        if target_source:
            lines.append(f"  {keyword}: {join_name} is {target_source} with {on_clause}")
        elif target_table:
            lines.append(
                f"  {keyword}: {join_name} is table('{target_table}') with {on_clause}"
            )
        else:
            raise SystemExit(
                f"Join requires `target_source` or `table`: {join!r}"
            )

    lines.append("}")
    return "\n".join(lines) + "\n"


def render_query(item: Dict[str, Any]) -> str:
    name = item.get("name")
    from_source = item.get("from")
    if not name or not from_source:
        raise SystemExit("Each query needs both `name` and `from`.")

    lines: List[str] = [f"query: {name} is {from_source} -> {{"]
    groups = [g["name"] for g in iter_items(item.get("group_by", []))]
    aggs = [a["name"] for a in iter_items(item.get("aggregate", []))]
    where = item.get("where")

    if groups:
        lines.append("  group_by:")
        lines.extend([f"    {g}" for g in groups])
    if aggs:
        lines.append("  aggregate:")
        lines.extend([f"    {a}" for a in aggs])
    if where:
        lines.append(f"  where: {where}")

    lines.append("}")
    return "\n".join(lines) + "\n"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", required=True, type=Path, help="YAML/JSON mapping file.")
    parser.add_argument("--out", required=True, type=Path, help="Output directory.")
    args = parser.parse_args()

    mapping = load_mapping(args.mapping)
    sources = mapping.get("sources", [])
    queries = mapping.get("queries", [])

    if not isinstance(sources, list) or not isinstance(queries, list):
        raise SystemExit("`sources` and `queries` must be arrays.")

    source_count = 0
    query_count = 0

    for src in sources:
        if not isinstance(src, dict):
            raise SystemExit(f"Source must be object: {src!r}")
        name = normalize_name(str(src.get("name", "")))
        content = render_source(src)
        write_file(args.out / "sources" / f"{name}.malloy", content)
        source_count += 1

    for qry in queries:
        if not isinstance(qry, dict):
            raise SystemExit(f"Query must be object: {qry!r}")
        name = normalize_name(str(qry.get("name", "")))
        content = render_query(qry)
        write_file(args.out / "queries" / f"{name}.malloy", content)
        query_count += 1

    print(f"Generated {source_count} source file(s) and {query_count} query file(s) in {args.out}")


if __name__ == "__main__":
    main()
