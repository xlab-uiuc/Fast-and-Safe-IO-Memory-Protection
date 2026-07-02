import os
import sys
import numpy as np
import pandas as pd

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

def __get_ebpf_stats(exp_name, run_id):
    run_dir = os.path.join("../utils/reports/", exp_name + f'-RUN-{run_id}')
    ebpf_path = os.path.join(run_dir, "ebpf_guest_stats.csv")
    if not os.path.exists(ebpf_path):
        # Fall back to host stats (e.g. bare-metal runs have no guest)
        ebpf_path = os.path.join(run_dir, "ebpf_host_stats.csv")
    if not os.path.exists(ebpf_path):
        return None
    print(f"Reading eBPF stats from {ebpf_path}")
    

#     # Per-Function Latency Statistics
# function,type,count,total_duration_ns,mean_ns,variance_us
# iommu_map,-1,171036,1139456425,6662.09,-4.24
# __iommu_map,-1,170998,185684984,1085.89,-0.69
# intel_iommu_iotlb_sync_map,-1,170922,686091943,4014.06,-3.05
# cache_tag_flush_range_np,-1,170866,498774037,2919.09,-2.03
# iommu_flush_write_buffer,-1,170811,118642694,694.58,-0.26
# __iommu_unmap,-1,170698,186294285,1091.37,-0.74
# intel_iommu_tlb_sync,-1,170646,2118537135,12414.81,385.33
# cache_tag_flush_range,-1,170591,1922281964,11268.37,383.70
# qi_submit_sync,-1,170362,1494422523,8772.04,378.01
# qi_batch_flush_descs,-1,340833,1807166455,5302.21,210.82
# trace_qi_submit_sync_cs,-1,170252,1294629687,7604.20,377.08
# page_pool_put_unrefed_netmem,-1,8695550,6395061571,735.44,-0.28
# page_pool_put_unrefed_page,-1,122,266038,2180.64,-1.07
# # Per-Function Per-CPU Counts

    # Read the ebpf_guest_stats.csv file and extract the lines between:
    #   "# Per-Function Latency Statistics" and "# Per-Function Per-CPU Counts"
    # Return as a pandas DataFrame with columns: function, type, count, total_duration_ns, mean_ns, variance_us

    with open(ebpf_path, 'r') as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("# Per-Function Latency Statistics"):
            start_idx = i + 1
        if line.strip().startswith("# Per-Function Per-CPU Counts"):
            end_idx = i
            break

    if start_idx is None or end_idx is None or end_idx <= start_idx:
        return None

    # The first line after start_idx is the header
    header = lines[start_idx].strip()
    data_lines = [l.strip() for l in lines[start_idx+1:end_idx] if l.strip() and not l.strip().startswith("#")]

    from io import StringIO
    csv_content = header + "\n" + "\n".join(data_lines)
    ebpf_results = pd.read_csv(StringIO(csv_content))

    # print(ebpf_results.to_string())
    # ebpf_results = pd.read_csv(ebpf_path)
    # # only show aggragete results
    # ebpf_results = ebpf_results[ebpf_results['core'] == -1]

    # return {key: ebpf_results[key] for key in ebpf_results.dtype.names}
    return ebpf_results

def get_tput_per_run(exp_name, run_id):
    tput_path = os.path.join("../utils/reports/", exp_name + f'-RUN-{run_id}', "iperf.bw.rpt")
    if not os.path.exists(tput_path):
        return None
    # print(f"Reading tput from {tput_path}")
    with open(tput_path, 'r') as f:
        lines = f.readlines()
    tput = float(lines[-1].split()[-1])
    print(f"Tput: {tput}")
    return tput

def get_ebpf_stats(exp_name, profile_duration=20):
    MAX_RUNS = 20
    ebpf_stats = {}
    for run_id in range(0, MAX_RUNS):
        run_stats = __get_ebpf_stats(exp_name, run_id)
        tput = get_tput_per_run(exp_name, run_id)
        if run_stats is None:
            continue
        total_data = tput * 1e9 / 8 * profile_duration  # bytes
        total_pages = total_data / 4096
        run_stats['count_per_page'] = run_stats['count'] / total_pages
        run_stats = run_stats.reset_index(drop=True)
        print(run_stats.to_string())

    return ebpf_stats

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
try:
    # Some runs won't have memory stats
    print(f"Mean Memory: {results['mem_mean']}")
    print(f"Max Memory: {results['mem_max']}")
except:
    pass
if "iommu" in metrics or "all" in metrics:
    print("Per page stats:")
    print(f"\tIOTLB Miss: {iotlb_miss_page}")
    print(f"\tIOTLB First Lookup: {iotlb_flkp_page}")
    print(f"\tIOTLB All Lookups: {iotlb_alllkp_page}")
    print(f"\tIOTLB Inv: {iotlb_inv_page}")
    print(f"\tIOMMU Mem Access: {iommu_mem_access_page}")

    # Also print the raw IOMMU/IOTLB counters you now export
    print(f"\tPWT Occupancy: {pwt}")

get_ebpf_stats(exp_name)
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
    print(f"Acks per page: {per_page(results['sent_packets_stddev'], tput)}")
print("")
