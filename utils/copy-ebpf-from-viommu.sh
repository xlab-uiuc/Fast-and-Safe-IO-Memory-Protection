#!/bin/bash

BASE="/home/schai/viommu_siyuan/utils/reports"
TS="2026-03-24-15-08-11"
SUFFIX="host-strict-guest-strict-nested"
TAIL="ringbuf512-sockbuf1-RUN"

folders=(
    # "$BASE/$TS-6.12.9-iommufd-RX-flow01-$SUFFIX-1cores-$TAIL"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow04-$SUFFIX-4cores-ringbuf512-sockbuf1-RUN-1"
    "$BASE/$TS-6.12.9-iommufd-RX-flow08-$SUFFIX-8cores-$TAIL-1"
    "$BASE/$TS-6.12.9-iommufd-RX-flow08-$SUFFIX-8cores-$TAIL-2"
    "$BASE/$TS-6.12.9-iommufd-RX-flow12-$SUFFIX-12cores-$TAIL-1"
    "$BASE/$TS-6.12.9-iommufd-RX-flow12-$SUFFIX-12cores-$TAIL-2"

    # "$BASE/$TS-6.12.9-iommufd-RX-flow16-$SUFFIX-16cores-$TAIL-1"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow20-$SUFFIX-20cores-$TAIL-1"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow24-$SUFFIX-24cores-$TAIL-1"
    # "$BASE/$TS-6.12.9-iommufd-RX-flow28-$SUFFIX-28cores-$TAIL-1"
)

LOCAL_BASE="reports"

for f in "${folders[@]}"; do
    sudo mkdir -p "$LOCAL_BASE/$(basename "$f")"
    scp viommu:"$f/ebpf_guest_stats.csv" "tmp_ebpf.csv"
    sudo mv "tmp_ebpf.csv" "$LOCAL_BASE/$(basename "$f")/ebpf_guest_stats.csv"
    # sudo chmod +666 "$LOCAL_BASE/$(basename "$f")/perf_kvm_nested_cores.csv"
    # scp "$LOCAL_BASE/$(basename "$f")/perf_kvm_nested_cores.csv"  viommu:"$f/perf_kvm_nested_cores.csv"
done