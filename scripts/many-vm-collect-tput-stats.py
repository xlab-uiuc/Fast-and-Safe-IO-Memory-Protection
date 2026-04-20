import sys
import numpy as np
import statistics
import subprocess
import os
import csv

# TODO: Leshna, Combine both vm and baremetal stat collector with file names as parameters.

EXP_NAME = sys.argv[1]
NUM_RUNS = int(sys.argv[2])
COLLECT_MLC_TPUT = int(sys.argv[3])

FILE_NAME = "../utils/reports/" + EXP_NAME
command = 'mkdir -p ' + FILE_NAME
result = subprocess.run(command, shell=True, capture_output=True, text=True)

net_tputs = []
retx_rates = []
sent_packets = []
mem_bws = []
cpu_utils = []
mlc_tputs = []

pcie_wr_tput = []
iotlb_first_lookup = []
iotlb_all_lookup = []
iotlb_miss = []
iommu_mem_access = []
iotlb_inv = []
pwt_occupancy = []
mem_used = []


# iotlb_hits = []
# ctx_lookup = []
# ctx_hits   = []
# ctxt_misses = []
# cache_lookup   = []
# cache_hit_256T = []
# cache_hit_512G = []
# cache_hit_1G   = []
# cache_hit_2M   = []
# cache_fills    = []

for i in range(NUM_RUNS):
    target_dir = FILE_NAME + '-RUN-' + str(i)
    target_file = target_dir + '/iperf.bw.rpt'

    print("\n=== DEBUGGING INFO ===")
    print(f"1. Current Working Directory (pwd): {os.getcwd()}")
    print(f"2. Target Directory: {target_dir}")
    print(f"3. Target File: {target_file}")

    # Check if the directory even exists
    if os.path.exists(target_dir):
        print(f"4. Directory EXISTS. Contents (ls):")
        try:
            files_in_dir = os.listdir(target_dir)
            if not files_in_dir:
                print("   [Directory is completely empty!]")
            else:
                for f in files_in_dir:
                    print(f"   - {f}")
        except Exception as e:
            print(f"   [Error trying to list directory contents: {e}]")
    else:
        print(f"4. CRITICAL: The directory {target_dir} DOES NOT EXIST at this exact moment!")

    print("======================\n")


    with open(target_file) as f1:
        for line in f1:
            tput = float(line.split()[-1])
            if (tput > 0):
                net_tputs.append(tput)
            break

    # with open(FILE_NAME + '-RUN-' + str(i) + '/client-retx.rpt') as f1:
    #     for line in f1:
    #         line_str = line.split()
    #         if (line_str[0] == 'Retx_percent:'):  # always come last so we can break
    #             retx_pct = float(line_str[-1])
    #             if (retx_pct >= 0):
    #                 retx_rates.append(retx_pct)
    #             break
    #         elif (line_str[0] == "Recv:"):
    #             sent = float(line_str[-1])
    #             sent_packets.append(sent)

    with open(FILE_NAME + '-RUN-' + str(i) + '/cpu_util.rpt') as f1:
        for line in f1:
            line_str = line.split()
            if (line_str[0] != 'avg_cpu_util:'):
                continue
            else:
                cpu_util = float(line_str[-1])
                if (cpu_util >= 0):
                    cpu_utils.append(cpu_util)
                break


def mean_or_zero(arr): return statistics.mean(arr) if arr else 0
def stdev_or_zero(arr): return statistics.stdev(arr) if len(arr) > 1 else 0
def max_or_zero(arr): return max(arr) if len(arr) > 1 else 0


cpu_utils_mean = mean_or_zero(cpu_utils);               cpu_utils_stddev = stdev_or_zero(cpu_utils)
net_tput_mean = mean_or_zero(net_tputs);                net_tput_stddev = stdev_or_zero(net_tputs)
# retx_rate_mean = mean_or_zero(retx_rates);              retx_rate_stddev = stdev_or_zero(retx_rates)
# sent_packets_mean = mean_or_zero(sent_packets);         sent_packets_stddev = stdev_or_zero(sent_packets)
# mem_bw_mean = mean_or_zero(mem_bws);                    mem_bw_stddev = stdev_or_zero(mem_bws)
# pcie_wr_tput_mean = mean_or_zero(pcie_wr_tput);         pcie_wr_tput_stddev = stdev_or_zero(pcie_wr_tput)

# iotlb_first_lookup_mean = mean_or_zero(iotlb_first_lookup);  iotlb_first_lookup_stddev = stdev_or_zero(iotlb_first_lookup)
# iotlb_all_lookup_mean  = mean_or_zero(iotlb_all_lookup);     iotlb_all_lookup_stddev  = stdev_or_zero(iotlb_all_lookup)
# iotlb_miss_mean        = mean_or_zero(iotlb_miss);           iotlb_miss_stddev        = stdev_or_zero(iotlb_miss)
# iommu_mem_access_mean  = mean_or_zero(iommu_mem_access);     iommu_mem_access_stddev  = stdev_or_zero(iommu_mem_access)
# iotlb_inv_mean         = mean_or_zero(iotlb_inv);            iotlb_inv_stddev         = stdev_or_zero(iotlb_inv)
# pwt_occupancy_mean     = mean_or_zero(pwt_occupancy);        pwt_occupancy_stddev     = stdev_or_zero(pwt_occupancy)
# mem_stats_mean = mean_or_zero(mem_used)
# mem_stats_max = max_or_zero(mem_used)

# mlc_tput_mean = 0
# mlc_tput_stddev = 0

# if (COLLECT_MLC_TPUT > 0):
#     mlc_tput_mean = statistics.mean(mlc_tputs)
#     if NUM_RUNS > 1:
#         mlc_tput_stddev = statistics.stdev(mlc_tputs)
#     else:
#         mlc_tput_stddev = 0

output_list = [
    ("cpu_utils_mean", cpu_utils_mean), ("cpu_utils_stddev", cpu_utils_stddev),
    ("net_tput_mean", net_tput_mean), ("net_tput_stddev", net_tput_stddev),
    # ("retx_rate_mean", retx_rate_mean), ("retx_rate_stddev", retx_rate_stddev),
    # ("mem_bw_mean", mem_bw_mean), ("mem_bw_stddev", mem_bw_stddev),
    # ("pcie_wr_tput_mean", pcie_wr_tput_mean), ("pcie_wr_tput_stddev", pcie_wr_tput_stddev),

    # ("iotlb_first_lookup_mean", iotlb_first_lookup_mean), ("iotlb_first_lookup_stddev", iotlb_first_lookup_stddev),
    # ("iotlb_all_lookup_mean",  iotlb_all_lookup_mean),   ("iotlb_all_lookup_stddev",  iotlb_all_lookup_stddev),
    # ("iotlb_miss_mean", iotlb_miss_mean), ("iotlb_miss_stddev", iotlb_miss_stddev),
    # ("iommu_mem_access_mean", iommu_mem_access_mean), ("iommu_mem_access_stddev", iommu_mem_access_stddev),
    # ("iotlb_inv_mean", iotlb_inv_mean), ("iotlb_inv_stddev", iotlb_inv_stddev),
    # ("pwt_occupancy_mean", pwt_occupancy_mean), ("pwt_occupancy_stddev", pwt_occupancy_stddev),

    # ("mlc_tput_mean", 0 if not mlc_tputs else mean_or_zero(mlc_tputs)),
    # ("mlc_tput_stddev", 0 if len(mlc_tputs) < 2 else stdev_or_zero(mlc_tputs)),
    # ("sent_packets_mean", sent_packets_mean), ("sent_packets_stddev", sent_packets_stddev),
    # ("mem_mean", mem_stats_mean), ("mem_max", mem_stats_max)
]

headers, outputs = zip(*output_list)
headers = ",".join(headers) 
outputs = list(outputs)

# Save array to DAT file
np.savetxt(FILE_NAME + '/tput_metrics.dat',
           [outputs], delimiter=",", header=headers, comments='', fmt='%.10f')
