import sys
import numpy as np
import statistics
import subprocess

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
    with open(FILE_NAME + '-RUN-' + str(i) + '/iperf.bw.rpt') as f1:
        for line in f1:
            tput = float(line.split()[-1])
            if (tput > 0):
                net_tputs.append(tput)
            break

    with open(FILE_NAME + '-RUN-' + str(i) + '/retx.rpt') as f1:
        for line in f1:
            line_str = line.split()
            if (line_str[0] == 'Retx_percent:'):  # always come last so we can break
                retx_pct = float(line_str[-1])
                if (retx_pct >= 0):
                    retx_rates.append(retx_pct)
                break
            elif (line_str[0] == "Recv:"):
                sent = float(line_str[-1])
                sent_packets.append(sent)

    with open(FILE_NAME + '-RUN-' + str(i) + '/membw.rpt') as f1:
        try:
            for line in f1:
                line_str = line.split()
                if (line_str[0] != 'Node0_total_bw:'):
                    continue
                else:
                    membw = float(line_str[-1])
                    if (membw >= 0):
                        mem_bws.append(membw)
                    break
        except Exception as e:
            mem_bws.append(0)

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
    try: 
        with open(FILE_NAME + '-RUN-' + str(i) + '/pcie.rpt') as f1:
            for line in f1:
                line_str = line.split()
                if (line_str[0] == 'PCIe_wr_tput:'):
                    pcie_tput = float(line_str[-1])
                    if (pcie_tput >= 0):
                        pcie_wr_tput.append(pcie_tput)
                elif (line_str[0] == 'IOTLB_first_lookup_avg:'):
                    iotlb_first_lookup_ = float(line_str[-1])
                    iotlb_first_lookup.append(iotlb_first_lookup_)
                elif (line_str[0] == 'IOTLB_all_lookup_avg:'):
                    iotlb_all_lookup_ = float(line_str[-1])
                    iotlb_all_lookup.append(iotlb_all_lookup_)
                elif (line_str[0] == 'IOTLB_miss_avg:'):
                    iotlb_miss_ = float(line_str[-1])
                    iotlb_miss.append(iotlb_miss_)
                elif (line_str[0] == 'IOMMU_mem_access:'):
                    iommu_mem_access_ = float(line_str[-1])
                    iommu_mem_access.append(iommu_mem_access_)
                elif (line_str[0] == 'IOTLB_inv_avg:'):
                    iotlb_inv_ = float(line_str[-1])
                    iotlb_inv.append(iotlb_inv_)
                elif (line_str[0] == 'PWT_occupancy_avg:'):
                    pwt_occupancy_ = float(line_str[-1])
                    pwt_occupancy.append(pwt_occupancy_)
    except Exception as e:
        pcie_wr_tput.append(0) 
        iotlb_first_lookup.append(0)
        iotlb_all_lookup.append(0)
        iotlb_miss.append(0)
        iommu_mem_access.append(0)
        iotlb_inv.append(0)
        pwt_occupancy.append(0)

    if (COLLECT_MLC_TPUT > 0 and False):
        with open(FILE_NAME + '-MLCRUN-' + str(i) + '/mlc.log') as f1:
            for line in f1:
                if line.startswith(' 00000'):
                    tput = float(line.split()[-1])
                    if (tput >= 0):
                        mlc_tputs.append(tput)
                    break

def mean_or_zero(arr): return statistics.mean(arr) if arr else 0
def stdev_or_zero(arr): return statistics.stdev(arr) if len(arr) > 1 else 0

cpu_utils_mean = mean_or_zero(cpu_utils);               cpu_utils_stddev = stdev_or_zero(cpu_utils)
net_tput_mean = mean_or_zero(net_tputs);                net_tput_stddev = stdev_or_zero(net_tputs)
retx_rate_mean = mean_or_zero(retx_rates);              retx_rate_stddev = stdev_or_zero(retx_rates)
sent_packets_mean = mean_or_zero(sent_packets);         sent_packets_stddev = stdev_or_zero(sent_packets)
mem_bw_mean = mean_or_zero(mem_bws);                    mem_bw_stddev = stdev_or_zero(mem_bws)
pcie_wr_tput_mean = mean_or_zero(pcie_wr_tput);         pcie_wr_tput_stddev = stdev_or_zero(pcie_wr_tput)

iotlb_first_lookup_mean = mean_or_zero(iotlb_first_lookup);  iotlb_first_lookup_stddev = stdev_or_zero(iotlb_first_lookup)
iotlb_all_lookup_mean  = mean_or_zero(iotlb_all_lookup);     iotlb_all_lookup_stddev  = stdev_or_zero(iotlb_all_lookup)
iotlb_miss_mean        = mean_or_zero(iotlb_miss);           iotlb_miss_stddev        = stdev_or_zero(iotlb_miss)
iommu_mem_access_mean  = mean_or_zero(iommu_mem_access);     iommu_mem_access_stddev  = stdev_or_zero(iommu_mem_access)
iotlb_inv_mean         = mean_or_zero(iotlb_inv);            iotlb_inv_stddev         = stdev_or_zero(iotlb_inv)
pwt_occupancy_mean     = mean_or_zero(pwt_occupancy);        pwt_occupancy_stddev     = stdev_or_zero(pwt_occupancy)

mlc_tput_mean = 0
mlc_tput_stddev = 0

if (COLLECT_MLC_TPUT > 0):
    mlc_tput_mean = statistics.mean(mlc_tputs)
    if NUM_RUNS > 1:
        mlc_tput_stddev = statistics.stdev(mlc_tputs)
    else:
        mlc_tput_stddev = 0

# TODO: convert to tuple list and use zip with unpacking to make it cleaner to read and less error prone
output_list = [
    ("cpu_utils_mean", cpu_utils_mean), ("cpu_utils_stddev", cpu_utils_stddev),
    ("net_tput_mean", net_tput_mean), ("net_tput_stddev", net_tput_stddev),
    ("retx_rate_mean", retx_rate_mean), ("retx_rate_stddev", retx_rate_stddev),
    ("mem_bw_mean", mem_bw_mean), ("mem_bw_stddev", mem_bw_stddev),
    ("pcie_wr_tput_mean", pcie_wr_tput_mean), ("pcie_wr_tput_stddev", pcie_wr_tput_stddev),

        ("iotlb_first_lookup_mean", iotlb_first_lookup_mean), ("iotlb_first_lookup_stddev", iotlb_first_lookup_stddev),
    ("iotlb_all_lookup_mean",  iotlb_all_lookup_mean),   ("iotlb_all_lookup_stddev",  iotlb_all_lookup_stddev),
    ("iotlb_miss_mean", iotlb_miss_mean), ("iotlb_miss_stddev", iotlb_miss_stddev),
    ("iommu_mem_access_mean", iommu_mem_access_mean), ("iommu_mem_access_stddev", iommu_mem_access_stddev),
    ("iotlb_inv_mean", iotlb_inv_mean), ("iotlb_inv_stddev", iotlb_inv_stddev),
    ("pwt_occupancy_mean", pwt_occupancy_mean), ("pwt_occupancy_stddev", pwt_occupancy_stddev),

    ("mlc_tput_mean", 0 if not mlc_tputs else mean_or_zero(mlc_tputs)),
    ("mlc_tput_stddev", 0 if len(mlc_tputs) < 2 else stdev_or_zero(mlc_tputs)),
    ("sent_packets_mean", sent_packets_mean), ("sent_packets_stddev", sent_packets_stddev),
]

headers, outputs = zip(*output_list)
headers = ",".join(headers) 
outputs = list(outputs)

# Save array to DAT file
np.savetxt(FILE_NAME + '/tput_metrics.dat',
           [outputs], delimiter=",", header=headers, comments='', fmt='%.10f')