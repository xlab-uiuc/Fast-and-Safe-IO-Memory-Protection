#!/usr/bin/env bash
set -euo pipefail

# Path to place resulting CSV file,
# this is the first argument passed to this script
# If not provided, it defaults to "memory_stats.csv" in the current directory
OUT="${1:-memory_stats.csv}"

# Time to wait between samples (in seconds)
WAIT="${2:-1}"

# Write header once
if [[ ! -f "$OUT" ]]; then
  echo "timestamp,mem_total,mem_used,mem_free,mem_shared,mem_buff_cache,mem_available,swap_total,swap_used,swap_free" > "$OUT"
fi

while true; do
  ts="$(date +"%Y-%m-%d %H:%M:%S.%6N%z")"
  free -b | awk -v ts="$ts" '/^Mem:/{m=$2","$3","$4","$5","$6","$7} /^Swap:/{s=$2","$3","$4} END{print ts","m","s}' >> "$OUT"
  sleep "$WAIT"
done
