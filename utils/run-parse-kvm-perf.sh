#!/bin/bash

PERF="/home/lbalara/viommu/linux-6.12.9/tools/perf/perf"
BASE="/home/lbalara/viommu/Fast-and-Safe-IO-Memory-Protection/utils/reports"
TS="2026-03-24-15-08-11"
SUFFIX="host-strict-guest-strict-nested"
TAIL="ringbuf512-sockbuf1-RUN"

folders=(
    # "$BASE/$TS-6.12.9-iommufd-RX-flow01-$SUFFIX-1cores-$TAIL"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow04-$SUFFIX-4cores-ringbuf512-sockbuf1-RUN-1"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow08-$SUFFIX-8cores-$TAIL"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow12-$SUFFIX-12cores-$TAIL"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow16-$SUFFIX-16cores-$TAIL"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow20-$SUFFIX-20cores-$TAIL"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow24-$SUFFIX-24cores-$TAIL"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow28-$SUFFIX-28cores-$TAIL"

    "$BASE/$TS-6.12.9-iommufd-RX-flow08-$SUFFIX-8cores-$TAIL-1"
    "$BASE/$TS-6.12.9-iommufd-RX-flow08-$SUFFIX-8cores-$TAIL-2"
    "$BASE/$TS-6.12.9-iommufd-RX-flow12-$SUFFIX-12cores-$TAIL-1"
    "$BASE/$TS-6.12.9-iommufd-RX-flow12-$SUFFIX-12cores-$TAIL-2"
)

LOCAL_BASE="reports"

for f in "${folders[@]}"; do
    OUT_CSV="$f/perf_kvm_nested_cores.csv"
    sudo python3 "$(dirname "$0")/parse_kvm_perf.py" --perf "$PERF" --csv "$OUT_CSV" "$f"
    LOCAL_DIR="$LOCAL_BASE/$(basename "$f")"
    sudo mkdir -p "$LOCAL_DIR"
    sudo cp "$OUT_CSV" "$LOCAL_DIR/perf_kvm_nested_cores.csv"
done

