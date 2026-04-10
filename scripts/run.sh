#!/bin/bash
python3 report-tput-metrics.py
exps=(
    "2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow01-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_1cores"
    "2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow04-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_4cores"
    "2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow08-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_8cores"
    "2025-10-03-16-07-35-6.12.9-iommufd-extra-hooks-flow20-host-strict-guest-on-nested-ringbuf-512_sokcetbuf1_20cores"
)

for exp in "${exps[@]}"; do
    python3 report-tput-metrics.py $exp tput,drops,acks,iommu,cpu | tee ../utils/reports/$exp_name/summary.txt
done
