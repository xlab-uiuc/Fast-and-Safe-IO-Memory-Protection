#!/usr/bin/env python3
"""
Parse KVM perf stat data from perf.data.guest files.

Usage:
    sudo python3 parse_kvm_perf.py <perf.data.guest>
    sudo python3 parse_kvm_perf.py <dir_containing_perf.data.guest>
    sudo python3 parse_kvm_perf.py <dir1> <dir2> ...  [--csv output.csv] [--json output.json]

Runs `perf kvm stat report` on each input and emits a structured summary.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys


PERF_BINARY = os.environ.get("PERF", "perf")
PERF_DATA_FILENAME = "perf.data.guest"

# Matches lines like:
#   HLT     17628    85.72%    97.06%    0.27us   281.62us    55.74us ( +- 0.37%)
#   EPT_MISCONFIG   987   4.80%    2.15%   0.26us   73.14us   11.07us ( +- 5.83%)
_ROW_RE = re.compile(
    r"^\s*(?P<exit_reason>\S+)"          # VM-EXIT name
    r"\s+(?P<samples>\d+)"               # sample count
    r"\s+(?P<samples_pct>[\d.]+)%"       # samples %
    r"\s+(?P<time_pct>[\d.]+)%"          # time %
    r"\s+(?P<min_time>[\d.]+)us"         # min time
    r"\s+(?P<max_time>[\d.]+)us"         # max time
    r"\s+(?P<avg_time>[\d.]+)us"         # avg time
    r".*$"
)

# Matches: Total Samples:20563, Total events handled time:1142.17ms.
_TOTAL_RE = re.compile(
    r"Total Samples:(?P<total_samples>\d+)"
    r",\s*Total events handled time:(?P<total_time_us>[\d.]+)us"
)


def resolve_data_file(path: str) -> str:
    """Return path to perf.data.guest, whether path is a file or directory."""
    if os.path.isdir(path):
        candidate = os.path.join(path, PERF_DATA_FILENAME)
        if not os.path.exists(candidate):
            raise FileNotFoundError(
                f"No {PERF_DATA_FILENAME} found in directory: {path}"
            )
        return candidate
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return path


def run_perf_report(data_file: str) -> str:
    """Run `perf kvm stat report` from the data file's directory and return output."""
    cmd = ["sudo", PERF_BINARY, "kvm", "stat", "report", "--stdio", "--vcpu", "0", "-k", "time"]
    print(f"Running: {' '.join(cmd)}  (cwd: {os.path.dirname(data_file)})")
    result = subprocess.run(
        cmd,
        cwd=os.path.dirname(data_file),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def parse_perf_output(raw: str) -> dict:
    """Parse perf kvm stat report output into a structured dict."""
    exits = []
    total_samples = None
    total_time_ns = None

    for line in raw.splitlines():
        m = _ROW_RE.match(line)
        if m:
            exits.append({
                "exit_reason":  m.group("exit_reason"),
                "samples":      int(m.group("samples")),
                "samples_pct":  float(m.group("samples_pct")),
                "time_pct":     float(m.group("time_pct")),
                "min_time_ns":   float(m.group("min_time")) * 1000,
                "max_time_ns":   float(m.group("max_time")) * 1000,
                "avg_time_ns":   float(m.group("avg_time")) * 1000,
                "exit_total_time_ns": float(m.group("avg_time")) * 1000 * int(m.group("samples")),
            })
            continue

        m = _TOTAL_RE.search(line)
        if m:
            total_samples = int(m.group("total_samples"))
            total_time_ns = float(m.group("total_time_us")) * 1000

    return {
        "exits": exits,
        "total_samples": total_samples,
        "total_time_ns": total_time_ns,
    }


def process_one(path: str, label: str | None = None) -> dict:
    data_file = resolve_data_file(path)
    raw = run_perf_report(data_file)
    parsed = parse_perf_output(raw)
    parsed["source"] = data_file
    parsed["label"] = label or os.path.basename(os.path.dirname(data_file))
    return parsed


def print_table(result: dict) -> None:
    label = result.get("label", result["source"])
    print(f"\n=== {label} ===")
    print(f"  Source: {result['source']}")
    if result["total_samples"] is not None:
        print(
            f"  Total samples: {result['total_samples']:,}  "
            f"Total time: {result['total_time_ns']:.2f} ns"
        )
    if not result["exits"]:
        print("  (no VM-exit rows parsed)")
        return
    hdr = f"  {'VM-EXIT':<24} {'Samples':>10} {'Samples%':>10} {'Time%':>8} {'Min(ns)':>12} {'Max(ns)':>12} {'Avg(ns)':>12} {'Total(ns)':>16}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for e in result["exits"]:
        print(
            f"  {e['exit_reason']:<24} {e['samples']:>10,} {e['samples_pct']:>9.2f}%"
            f" {e['time_pct']:>7.2f}% {e['min_time_ns']:>12.2f}"
            f" {e['max_time_ns']:>12.2f} {e['avg_time_ns']:>12.2f}"
            f" {e['exit_total_time_ns']:>16.2f}"
        )


def write_csv(results: list[dict], out_path: str) -> None:
    fieldnames = [
        "label", "source",
        "exit_reason", "samples", "samples_pct", "time_pct",
        "min_time_ns", "max_time_ns", "avg_time_ns", "exit_total_time_ns",
        "total_samples", "total_time_ns",
    ]
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for result in results:
            for exit_row in result["exits"]:
                row = {**exit_row,
                       "label": result["label"],
                       "source": result["source"],
                       "total_samples": result["total_samples"],
                       "total_time_ns": result["total_time_ns"]}
                writer.writerow(row)
    print(f"CSV written to: {out_path}")


def write_json(results: list[dict], out_path: str) -> None:
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"JSON written to: {out_path}")


def main() -> None:
    global PERF_BINARY
    parser = argparse.ArgumentParser(
        description="Parse KVM perf stat data from perf.data.guest files."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="PATH",
        help=f"Path(s) to {PERF_DATA_FILENAME} files or directories containing them.",
    )
    parser.add_argument(
        "--csv",
        metavar="FILE",
        help="Write results to a CSV file.",
    )
    parser.add_argument(
        "--json",
        metavar="FILE",
        help="Write results to a JSON file.",
    )
    parser.add_argument(
        "--perf",
        metavar="BINARY",
        default=PERF_BINARY,
        help=f"Path to the perf binary (default: {PERF_BINARY}, or $PERF env var).",
    )
    args = parser.parse_args()

    PERF_BINARY = args.perf

    results = []
    for path in args.inputs:
        try:
            result = process_one(path)
            results.append(result)
            print_table(result)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    if args.csv:
        write_csv(results, args.csv)

    if args.json:
        write_json(results, args.json)


if __name__ == "__main__":
    main()
