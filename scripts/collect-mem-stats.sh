#!/usr/bin/env bash
set -euo pipefail

# Path to place resulting CSV file,
# this is the first argument passed to this script
# If not provided, it defaults to "memory_stats.csv" in the current directory
OUT="${1:-memory_stats.csv}"

# Time to wait between samples (in seconds)
WAIT="${2:-1}"

read_tx_active_pages() {
  local counter_file

  # Resolve the currently present mlx5 tx_active_pages file each sample,
  # as the PCIe address directory name can change between runs.
  counter_file="$(compgen -G '/sys/kernel/debug/mlx5/*/pages/dma_counters/tx_active_pages' | head -n1 || true)"
  if [[ -n "${counter_file}" && -r "${counter_file}" ]]; then
    cat "${counter_file}"
  else
    echo "-1"
  fi
}

read_rx_active_pages() {
  local counter_file

  counter_file="$(compgen -G '/sys/kernel/debug/mlx5/*/pages/dma_counters/rx_active' | head -n1 || true)"
  if [[ -n "${counter_file}" && -r "${counter_file}" ]]; then
    cat "${counter_file}"
  else
    echo "-1"
  fi
}

# Write header once
if [[ ! -f "$OUT" ]]; then
  echo "timestamp,mem_total,mem_used,mem_free,mem_shared,mem_buff_cache,mem_available,swap_total,swap_used,swap_free,tx_active_pages,rx_active_pages" > "$OUT"
fi

while true; do
  ts="$(date +"%Y-%m-%d %H:%M:%S.%6N%z")"
  tx_active_pages="$(read_tx_active_pages)"
  rx_active_pages="$(read_rx_active_pages)"
  free -b | awk -v ts="$ts" -v tx="$tx_active_pages" -v rx="$rx_active_pages" '/^Mem:/{m=$2","$3","$4","$5","$6","$7} /^Swap:/{s=$2","$3","$4} END{print ts","m","s","tx","rx}' >> "$OUT"
  sleep "$WAIT"
done
