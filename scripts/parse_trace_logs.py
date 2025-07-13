import os
import re
import csv
import numpy as np

def parse_trace_file(filepath):
    active_pages = []
    cache_occ = []
    ring_occ = []
    cache_count_total = 0
    ring_count_total = 0
    slow_count_total = 0
    total_count_sum = 0

    active_re = re.compile(r'active pages = (\d+), cache occ = (\d+), ring occ = (\d+)')
    count_re = re.compile(r'cache_count = (\d+), ring_count = (\d+), slow_count = (\d+), total = (\d+)')

    with open(filepath, 'r') as f:
        for line in f:
            if (active_match := active_re.search(line)):
                active_pages.append(int(active_match.group(1)))
                cache_occ.append(int(active_match.group(2)))
                ring_occ.append(int(active_match.group(3)))

            if (count_match := count_re.search(line)):
                cache_count_total += int(count_match.group(1))
                ring_count_total += int(count_match.group(2))
                slow_count_total += int(count_match.group(3))
                total_count_sum += int(count_match.group(4))

    return {
        "active_pages": active_pages,
        "cache_occ": cache_occ,
        "ring_occ": ring_occ,
        "cache_count": cache_count_total,
        "ring_count": ring_count_total,
        "slow_count": slow_count_total,
        "total_count": total_count_sum
    }

def parse_tcp_trace_file(filepath):
    rcv_wnd_values = []
    rcv_re = re.compile(r'rcv_wnd=(\d+)')

    with open(filepath, 'r') as f:
        for line in f:
            if (match := rcv_re.search(line)):
                rcv_wnd_values.append(int(match.group(1)))

    return rcv_wnd_values

def compute_stats(values):
    arr = np.array(values)
    return {
        "mean": np.mean(arr),
        "std": np.std(arr),
        "50th": np.percentile(arr, 50),
        "90th": np.percentile(arr, 90),
        "99th": np.percentile(arr, 99),
    }

def write_csv(trace_stats, rcv_wnd_values, out_path):
    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Metric', 'Mean', 'Std', '50th', '90th', '99th'])

        for key in ["active_pages", "cache_occ", "ring_occ"]:
            values = trace_stats[key]
            if values:
                stat = compute_stats(values)
                writer.writerow([
                    key, f"{stat['mean']:.2f}", f"{stat['std']:.2f}",
                    f"{stat['50th']:.2f}", f"{stat['90th']:.2f}", f"{stat['99th']:.2f}"
                ])
            else:
                writer.writerow([key] + ['NA'] * 5)

        if rcv_wnd_values:
            rcv_stats = compute_stats(rcv_wnd_values)
            writer.writerow([
                "rcv_wnd",
                f"{rcv_stats['mean'] / (1024*1024):.4f} MB",
                f"{rcv_stats['std'] / 1024:.2f} KB",
                f"{rcv_stats['50th'] / (1024*1024):.4f}",
                f"{rcv_stats['90th'] / (1024*1024):.4f}",
                f"{rcv_stats['99th'] / (1024*1024):.4f}"
            ])
        else:
            writer.writerow(["rcv_wnd"] + ['NA'] * 5)

        writer.writerow(["cache_count", trace_stats['cache_count']] + [''] * 5)
        writer.writerow(["ring_count", trace_stats['ring_count']] + [''] * 5)
        writer.writerow(["slow_count", trace_stats['slow_count']] + [''] * 5)
        writer.writerow(["total_count", trace_stats['total_count']] + [''] * 5)

        n = trace_stats['total_count']
        norm = lambda x: x / n if n > 0 else 0
        writer.writerow(["normalized_cache_count", f"{norm(trace_stats['cache_count']):.3f}"] + [''] * 5)
        writer.writerow(["normalized_ring_count", f"{norm(trace_stats['ring_count']):.3f}"] + [''] * 5)
        writer.writerow(["normalized_slow_count", f"{norm(trace_stats['slow_count']):.5f}"] + [''] * 5)

def write_human_readable(trace_stats, rcv_wnd_values, out_path):
    with open(out_path, 'w') as f:
        for key in ["active_pages", "cache_occ", "ring_occ"]:
            values = trace_stats[key]
            f.write(f"{key}:\n")
            if values:
                stat = compute_stats(values)
                f.write(f"    mean: {stat['mean']:.2f}\n")
                f.write(f"    standard deviation: {stat['std']:.2f}\n")
                f.write(f"    50th percentile: {stat['50th']:.2f}\n")
                f.write(f"    90th percentile: {stat['90th']:.2f}\n")
                f.write(f"    99th percentile: {stat['99th']:.2f}\n\n")
            else:
                f.write("    no data available\n\n")

        f.write("rcv_wnd:\n")
        if rcv_wnd_values:
            rcv_stats = compute_stats(rcv_wnd_values)
            f.write(f"    mean: {rcv_stats['mean'] / (1024*1024):.4f} MB\n")
            f.write(f"    std: {rcv_stats['std'] / 1024:.2f} KB\n")
            f.write(f"    50th: {rcv_stats['50th'] / (1024*1024):.4f} MB\n")
            f.write(f"    90th: {rcv_stats['90th'] / (1024*1024):.4f} MB\n")
            f.write(f"    99th: {rcv_stats['99th'] / (1024*1024):.4f} MB\n\n")
        else:
            f.write("    no data available\n\n")

        f.write(f"cache_count: {trace_stats['cache_count']}\n")
        f.write(f"ring_count: {trace_stats['ring_count']}\n")
        f.write(f"slow_count: {trace_stats['slow_count']}\n")
        f.write(f"total_count: {trace_stats['total_count']}\n")

        n = trace_stats['total_count']
        norm = lambda x: 1_000_000 * x / n if n > 0 else 0
        f.write(f"normalized_cache_count: {norm(trace_stats['cache_count']):.5f}\n")
        f.write(f"normalized_ring_count: {norm(trace_stats['ring_count']):.5f}\n")
        f.write(f"normalized_slow_count: {norm(trace_stats['slow_count']):.5f}\n")

def main():
    cwd = os.getcwd()
    trace_path = os.path.join(cwd, "trace.log")
    tcp_path = os.path.join(cwd, "tcp_trace.log")
    out_csv = os.path.join(cwd, "trace_stats.csv")
    out_txt = os.path.join(cwd, "trace_stats.txt")

    if not os.path.isfile(trace_path):
        print("Error: trace.log not found in current directory.")
        return
    if not os.path.isfile(tcp_path):
        print("Error: tcp_trace.log not found in current directory.")
        return

    trace_stats = parse_trace_file(trace_path)
    rcv_wnd_values = parse_tcp_trace_file(tcp_path)
    write_csv(trace_stats, rcv_wnd_values, out_csv)
    write_human_readable(trace_stats, rcv_wnd_values, out_txt)

if __name__ == "__main__":
    main()
