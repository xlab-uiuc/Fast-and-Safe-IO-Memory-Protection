#!/usr/bin/env python3
"""Collect per-core CPU utilization and per-core throughput for a single RUN."""

import sys
import os
import glob
import re

def parse_cpu_util(cpu_util_log):
    """Parse sar cpu_util.log and return {core: avg_util%}."""
    cpu_util = {}
    num_samples = {}

    header_len = None
    cpu_index = None
    idle_index = None

    with open(cpu_util_log) as f:
        for line in f:
            elements = line.split()
            if not elements or 'Linux' in elements[0] or 'CPU' not in elements:
                continue
            if '%idle' in elements:
                header_len = len(elements)
                cpu_index = elements.index('CPU')
                idle_index = elements.index('%idle')
                break

        if header_len is None:
            print(f"ERROR: could not parse {cpu_util_log}", file=sys.stderr)
            return {}

        f.seek(0)
        for line in f:
            elements = line.split()
            if len(elements) == header_len and elements[cpu_index] != "CPU":
                cpu = int(elements[cpu_index])
                idle = float(elements[idle_index])
                if cpu not in cpu_util:
                    cpu_util[cpu] = 0.0
                    num_samples[cpu] = 0
                cpu_util[cpu] += (100 - idle)
                num_samples[cpu] += 1

    for cpu in cpu_util:
        if num_samples[cpu] > 0:
            cpu_util[cpu] /= num_samples[cpu]

    return cpu_util


def parse_iperf_log(log_file):
    """Parse an iperf3 per-thread log file. Returns list of (interval_str, tput_mbps)."""
    intervals = []
    with open(log_file) as f:
        for line in f:
            m = re.match(r'\[\s*\d+\]\s+([\d.]+-[\d.]+\s+sec)\s+[\d.]+\s+\w+Bytes\s+([\d.]+)\s+Mbits/sec', line)
            if m:
                intervals.append((m.group(1).strip(), float(m.group(2))))
    return intervals


def main():
    if len(sys.argv) < 2:
        print("Usage: collect-per-core-stats.py <exp-RUN-dir> [period]")
        print("  exp-RUN-dir: path to a single RUN directory (in utils/logs/ or utils/reports/)")
        print("  period: interval to report, e.g. '60.03-90.03' (default: last complete interval)")
        sys.exit(1)

    run_dir = sys.argv[1]
    target_period = sys.argv[2] if len(sys.argv) > 2 else None

    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils", "logs", run_dir)
    

    print(f"log_dir: {log_dir}")
    iperf_files = sorted(glob.glob(os.path.join(log_dir, "iperf.bw.counter*.core*.log")))
    if not iperf_files:
        iperf_single = os.path.join(log_dir, "iperf.bw.log")
        if os.path.exists(iperf_single):
            print("WARN: Only single iperf.bw.log found; per-core throughput unavailable.", file=sys.stderr)
        else:
            print("ERROR: No iperf log files found.", file=sys.stderr)
        sys.exit(1)

    per_core_tput = {}
    for f in iperf_files:
        basename = os.path.basename(f)
        m = re.match(r'iperf\.bw\.counter(\d+)\.core(\d+)\.log', basename)
        if not m:
            continue
        counter = int(m.group(1))
        core = int(m.group(2))
        intervals = parse_iperf_log(f)
        if not intervals:
            per_core_tput[(counter, core)] = None
            continue

        if target_period:
            matched = [t for (iv, t) in intervals if target_period in iv]
            tput = matched[0] if matched else None
        else:
            tput = intervals[-1][1] if intervals else None

        per_core_tput[(counter, core)] = tput

    cpu_util_log = os.path.join(log_dir, "cpu_util.log")
    cpu_utils = parse_cpu_util(cpu_util_log) if os.path.exists(cpu_util_log) else {}

    print(f"{'counter':>8}  {'core':>4}  {'tput_mbps':>10}  {'tput_gbps':>10}  {'cpu_util%':>9}  {'gbps/cpu%':>9}")
    print("-" * 62)

    total_tput = 0.0
    for (counter, core) in sorted(per_core_tput.keys()):
        tput = per_core_tput[(counter, core)]
        tput_str = f"{tput:10.1f}" if tput is not None else "       N/A"
        gbps_str = f"{tput/1000:10.3f}" if tput is not None else "       N/A"
        cpu = cpu_utils.get(core)
        cpu_str = f"{cpu:9.2f}" if cpu is not None else "      N/A"
        if tput is not None and cpu is not None and cpu > 0:
            eff_str = f"{(tput/1000)/cpu:9.4f}"
        else:
            eff_str = "      N/A"
        print(f"{counter:>8}  {core:>4}  {tput_str}  {gbps_str}  {cpu_str}  {eff_str}")
        if tput is not None:
            total_tput += tput

    print("-" * 62)
    avg_cpu = sum(cpu_utils.get(core, 0) for (_, core) in per_core_tput) / len(per_core_tput) if per_core_tput else 0
    total_eff = f"{(total_tput/1000)/avg_cpu:9.4f}" if avg_cpu > 0 else "      N/A"
    print(f"{'TOTAL':>8}  {'':>4}  {total_tput:10.1f}  {total_tput/1000:10.3f}  {avg_cpu:9.2f}  {total_eff}")


if __name__ == "__main__":
    main()
