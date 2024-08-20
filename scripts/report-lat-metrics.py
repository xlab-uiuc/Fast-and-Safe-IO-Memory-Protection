import os
import sys
import numpy as np
import pandas as pd


if len(sys.argv) != 2:
    print("Usage: python script.py <exp>")
    sys.exit(1)

# Get the directory where the script is located and change directory
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(script_dir)

# Get the filename from the user
exp_name = sys.argv[1]

# Combine the base path with the filename
full_path = os.path.join("../utils/reports/", exp_name, "lat_metrics.dat")

results = pd.read_csv(full_path)

# -------- Print out metrics from paper ----------- #

print(f"------- {exp_name} Run Latency (p50, p90, p99, p999, p9999) -------")

def print_lat(lat_list):
    lats = ["p50","p90","p99","p999","p9999"]
    for (lat, latency) in zip(lats, lat_list):
        print(f"\t{lat}: {latency}")

print(f"128B Request size")
print_lat(results['128'])
print(f"512B Request size")
print_lat(results['512'])
print(f"2KB Request size")
print_lat(results['2048'])
print(f"8KB Request size")
print_lat(results['8192'])
print(f"32KB Request size")
print_lat(results['32768'])
