#!/bin/bash
# Usage: collect-period-tput.sh <exp-name-with-RUN>

if [ $# -eq 0 ]; then
    echo "Usage: $0 <exp-name>"
    exit 1
fi

period=(
    "0.*-30.*"
    "30.*-60.*"
    "60.*-90.*"
    "90.*-120.*"
    "120.*-150.*"
    "150.*-180.*"
    "180.*-210.*"
    "210.*-240.*"
    "240.*-270.*"
    "270.*-300.*"
)

report_dir="../utils/reports/$1"
report_file="$report_dir/iperf.bw.rpt"
log_file="../utils/logs/$1/iperf.bw.log"

if [ ! -f "$log_file" ]; then
    echo "ERROR: $log_file does not exist"
    exit 1
fi

> "$report_file"

last_tput=""
for p in "${period[@]}"; do
    iperf_tput=$(cat "$log_file" | grep "$p" | awk '{ sum += $7; n++ } END { if (n > 0) printf "%.3f", sum/1000; }')
    echo "Period $p tput: $iperf_tput" >> "$report_file"
    if [ -n "$iperf_tput" ]; then
        last_tput="$iperf_tput"
    fi
done
echo "Avg_iperf_tput: $last_tput" >> "$report_file"

echo "log_file: $log_file"
echo "tput report saved to $report_file"
