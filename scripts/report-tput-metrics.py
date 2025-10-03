import os
import sys
import numpy as np

if len(sys.argv) != 3:
    print("Usage: python script.py <exp_name> <metrics>")
    sys.exit(1)

# Get the directory where the script is located and change directory
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(script_dir)

# Get the filename from the user
exp_name = sys.argv[1]
metrics_arg = sys.argv[2]
metrics = list(map(str.lower, metrics_arg.split(",")))

full_path = os.path.join("../utils/reports/", exp_name, "tput_metrics.dat")
results = np.genfromtxt(full_path, dtype=float, delimiter=',', names=True)

def per_page(value, tput_gbps_mean):
    tput_bps = tput_gbps_mean * 1e9
    tput_Bps = tput_bps / 8
    pages_ps = tput_Bps / 4096
    return value/pages_ps


tput = results['net_tput_mean']
sent_packets = results['sent_packets_mean'] / 20
drop_rate = results['retx_rate_mean']
cpu = results['cpu_utils_mean']
pwt = results['pwt_occupancy_mean']

acks_page = per_page(sent_packets, tput)
iotlb_miss_page = per_page(results['iotlb_miss_mean'], tput)
iotlb_flkp_page = per_page(results['iotlb_first_lookup_mean'], tput)
iotlb_alllkp_page = per_page(results['iotlb_all_lookup_mean'], tput)
iommu_mem_access_page = per_page(results['iommu_mem_access_mean'], tput)
iotlb_inv_page = per_page(results['iotlb_inv_mean'], tput)


print(f"------- {exp_name} Run Metrics -------")

if "tput" in metrics or "all" in metrics:
    print(f"Throughput: {tput}")
if "cpu" in metrics or "all" in metrics:
    print(f"CPU Util: {cpu}")
if "drops" in metrics or "all" in metrics:
    print(f"Drop rate: {drop_rate}")
if "acks" in metrics or "all" in metrics:
    print(f"Acks per page: {acks_page}")
if "iommu" in metrics or "all" in metrics:
    print("Per page stats:")
    print(f"\tIOTLB Miss: {iotlb_miss_page}")
    print(f"\tIOTLB First Lookup: {iotlb_flkp_page}")
    print(f"\tIOTLB All Lookups: {iotlb_alllkp_page}")
    print(f"\tIOTLB Inv: {iotlb_inv_page}")
    print(f"\tIOMMU Mem Access: {iommu_mem_access_page}")

    # Also print the raw IOMMU/IOTLB counters you now export
    print(f"\tPWT Occupancy: {pwt}")

# If no stddevs (single run), stop here
if not results['net_tput_stddev']:
    print("")
    sys.exit(0)

print(f"------- {exp_name} Run Metrics stddev -------")
if "tput" in metrics or "all" in metrics:
    print(f"Throughput: {results['net_tput_stddev']}")
if "cpu" in metrics or "all" in metrics:
    print(f"CPU Util: {results['cpu_utils_stddev']}")
if "drops" in metrics or "all" in metrics:
    print(f"Drop rate: {results['retx_rate_stddev']}")
if "acks" in metrics or "all" in metrics:
    print(f"Acks per page: {misses_per_page(results['sent_packets_stddev'], tput)}")
print("")
