#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  hive_inventory_from_files.sh <legacy_sql_root> [output_dir]

Description:
  Scan .sql/.hql files and generate migration inventory CSV files:
  - hive_tables.csv
  - hive_jobs.csv
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 1
fi

legacy_root="$1"
output_dir="${2:-migration_output}"

if [[ ! -d "$legacy_root" ]]; then
  echo "Error: legacy_sql_root does not exist: $legacy_root" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "Error: ripgrep (rg) is required but not found." >&2
  exit 1
fi

mkdir -p "$output_dir"
tables_csv="$output_dir/hive_tables.csv"
jobs_csv="$output_dir/hive_jobs.csv"
tmp_targets="$output_dir/.targets.tmp"
tmp_deps="$output_dir/.deps.tmp"
tmp_files="$output_dir/.sql_files.tmp"

echo "file_path,table_name,object_type" >"$tables_csv"
echo "file_path,job_type,target_table,dependencies,schedule_hint" >"$jobs_csv"

rg --files "$legacy_root" -g '*.sql' -g '*.hql' | sort >"$tmp_files" || true

if [[ ! -s "$tmp_files" ]]; then
  echo "No .sql/.hql files found under: $legacy_root" >&2
  exit 0
fi

while IFS= read -r file; do
  rel="$file"
  if [[ "$file" == "$legacy_root/"* ]]; then
    rel="${file#$legacy_root/}"
  fi

  rg -Noi 'create\s+(external\s+)?table\s+`?[a-zA-Z0-9_.]+`?' "$file" \
    | sed -E 's/`//g; s/[[:space:]]+/ /g; s/^.*table //' \
    | awk -v rel="$rel" 'NF {print rel "," $1 ",create_table"}' \
    >>"$tables_csv" || true

  rg -Noi 'create\s+view\s+`?[a-zA-Z0-9_.]+`?' "$file" \
    | sed -E 's/`//g; s/[[:space:]]+/ /g; s/^.*view //' \
    | awk -v rel="$rel" 'NF {print rel "," $1 ",create_view"}' \
    >>"$tables_csv" || true

  : >"$tmp_targets"
  rg -Noi 'insert\s+(overwrite|into)\s+table\s+`?[a-zA-Z0-9_.]+`?' "$file" \
    | sed -E 's/`//g; s/[[:space:]]+/ /g; s/^.*table //' \
    | awk 'NF {print $1}' \
    >"$tmp_targets" || true

  : >"$tmp_deps"
  rg -Noi 'from\s+`?[a-zA-Z0-9_.]+`?' "$file" \
    | sed -E 's/`//g; s/[[:space:]]+/ /g; s/^.*from //' \
    | awk 'NF {print $1}' \
    | sort -u >"$tmp_deps" || true

  dependencies="$(paste -sd ';' "$tmp_deps" | sed 's/,/|/g')"
  if [[ -z "$dependencies" ]]; then
    dependencies="none"
  fi

  schedule_hint="$(rg -Noi '((cron|schedule)\s*[:=]\s*[^[:space:]]+)' "$file" | head -n 1 | sed -E 's/[[:space:]]+/ /g' || true)"
  if [[ -z "$schedule_hint" ]]; then
    schedule_hint="unspecified"
  else
    schedule_hint="${schedule_hint//,/|}"
  fi

  if [[ -s "$tmp_targets" ]]; then
    while IFS= read -r target; do
      clean_target="${target//,/|}"
      echo "$rel,insert_table,$clean_target,$dependencies,$schedule_hint" >>"$jobs_csv"
    done <"$tmp_targets"
  fi
done <"$tmp_files"

rm -f "$tmp_targets" "$tmp_deps" "$tmp_files"
echo "Inventory generated:"
echo "  - $tables_csv"
echo "  - $jobs_csv"
