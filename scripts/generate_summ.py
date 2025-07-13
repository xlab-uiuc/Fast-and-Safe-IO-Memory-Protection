import os
import re
import sys
import pandas as pd

def parse_trace_stats(file_path):
    with open(file_path, 'r') as f:
        text = f.read()

    def extract(pattern, count, label):
        match = re.search(pattern, text, re.DOTALL)
        if not match or len(match.groups()) < count:
            raise ValueError(f"Missing or malformed section for {label}")
        return tuple(float(match.group(i + 1)) for i in range(count))

    return {
        "active_pages": extract(r"active_pages:\s+mean:\s+([\d.]+)\s+standard deviation:\s+([\d.]+).*?99th percentile:\s+([\d.]+)", 3, "active_pages"),
        "cache_occ": extract(r"cache_occ:\s+mean:\s+([\d.]+)\s+standard deviation:\s+([\d.]+).*?99th percentile:\s+([\d.]+)", 3, "cache_occ"),
        "ring_occ": extract(r"ring_occ:\s+mean:\s+([\d.]+)\s+standard deviation:\s+([\d.]+).*?99th percentile:\s+([\d.]+)", 3, "ring_occ"),
        "rcv_wnd": extract(r"rcv_wnd:\s+mean:\s+([\d.]+)\s+MB\s+std:\s+([\d.]+)\s+KB", 2, "rcv_wnd"),
        "cache_per_1M": extract(r"normalized_cache_count:\s+([0-9.eE+-]+)", 1, "cache")[0],
        "ring_per_1M": extract(r"normalized_ring_count:\s+([0-9.eE+-]+)", 1, "ring")[0],
        "slow_per_1M": extract(r"normalized_slow_count:\s+([0-9.eE+-]+)", 1, "slow")[0],
    }

def extract_flow_count(folder_name):
    match = re.search(r"flow-(\d+)", folder_name)
    return int(match.group(1)) if match else None

def read_single_value(filepath, label, pattern):
    if not os.path.isfile(filepath):
        raise ValueError(f"{label} file not found")
    with open(filepath) as f:
        content = f.read()
    match = re.search(pattern, content)
    if not match:
        raise ValueError(f"{label} value missing or malformed")
    return float(match.group(1))

def parse_tput_metrics(filepath, tput):
    if not os.path.isfile(filepath):
        return [None] * 4
    with open(filepath) as f:
        lines = f.readlines()
    if len(lines) < 2:
        return [None] * 4
    headers = lines[0].strip().split(",")
    values = list(map(float, lines[1].strip().split(",")))
    metrics = dict(zip(headers, values))
    denom = tput * 500 * 64 if tput > 0 else 1e-9
    return [
        metrics.get("iotlb_misses_mean", 0.0) / denom,
        metrics.get("l1_misses_mean", 0.0) / denom,
        metrics.get("l2_misses_mean", 0.0) / denom,
        metrics.get("l3_misses_mean", 0.0) / denom,
    ]

def main(base_dir):
    rows = []
    DENOM = 1_000_000

    for subfolder in sorted(os.listdir(base_dir)):
        if "RUN" in subfolder:
            continue

        sub_path = os.path.join(base_dir, subfolder)
        stats_file = os.path.join(sub_path, "trace_stats.txt")
        tput_metrics_file = os.path.join(sub_path, "tput_metrics.dat")
        if not os.path.isfile(stats_file):
            continue

        flow_count = extract_flow_count(subfolder)
        if flow_count is None:
            print(f"Warning: could not extract flow count from folder {subfolder}")
            continue

        run_path = os.path.join(base_dir, subfolder + "-RUN-0")
        cpu_rpt = os.path.join(run_path, "cpu_util.rpt")
        tput_rpt = os.path.join(run_path, "iperf.bw.rpt")

        try:
            stats = parse_trace_stats(stats_file)
            tput = read_single_value(tput_rpt, "tput", r"Avg_iperf_tput:\s+([0-9.]+)")
            cpu_util = read_single_value(cpu_rpt, "cpu_util", r"avg_cpu_util:\s+([0-9.]+)")

            cache_sec = stats["cache_per_1M"] * tput * 1024 * 32 / DENOM
            ring_sec = stats["ring_per_1M"] * tput * 1024 * 32 / DENOM
            slow_sec = stats["slow_per_1M"] * tput * 1024 * 32 / DENOM

            iotlb, l1, l2, l3 = parse_tput_metrics(tput_metrics_file, tput)

            row = {
                "#_flows": flow_count,
                "avg_tput": tput,
                "avg_cpu_util": cpu_util,
                "rcv_wnd_mean": stats["rcv_wnd"][0],
                "rcv_wnd_std": stats["rcv_wnd"][1],
                "active_pages_mean": stats["active_pages"][0],
                "active_pages_std": stats["active_pages"][1],
                "active_pages_99p": stats["active_pages"][2],
                "cache_occ_mean": stats["cache_occ"][0],
                "cache_occ_std": stats["cache_occ"][1],
                "cache_occ_99p": stats["cache_occ"][2],
                "ring_occ_mean": stats["ring_occ"][0],
                "ring_occ_std": stats["ring_occ"][1],
                "ring_occ_99p": stats["ring_occ"][2],
                "cache_accesses_per_1M_pages": stats["cache_per_1M"],
                "ring_accesses_per_1M_pages": stats["ring_per_1M"],
                "slow_accesses_per_1M_pages": stats["slow_per_1M"],
                "cache_accesses_per_sec": cache_sec,
                "ring_accesses_per_sec": ring_sec,
                "slow_accesses_per_sec": slow_sec,
                "iotlb_misses_per_page": iotlb,
                "l1_misses_per_page": l1,
                "l2_misses_per_page": l2,
                "l3_misses_per_page": l3,
            }
            rows.append(row)
        except Exception as e:
            print(f"Error in {subfolder}: {e}")

    df = pd.DataFrame(rows)
    if df.empty:
        print("No valid data found.")
        return

    df.sort_values("#_flows", inplace=True)

    print(df.to_string(index=False))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_summ.py <top-level-folder>")
        sys.exit(1)

    top_dir = sys.argv[1]
    if not os.path.isdir(top_dir):
        print(f"Error: {top_dir} is not a valid directory.")
        sys.exit(1)

    main(top_dir)
