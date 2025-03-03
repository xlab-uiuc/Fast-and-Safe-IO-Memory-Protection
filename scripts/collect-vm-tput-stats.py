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
pcie_wr_tput = []
iotlb_hits = []
iotlb_misses = []
ctxt_misses = []
l1_miss = []
l2_miss = []
l3_miss = []
mem_read = []
cpu_utils = []
mlc_tputs = []

for i in range(NUM_RUNS):
    with open(FILE_NAME + '-RUN-' + str(i) + '/iperf.bw.rpt') as f1:
        for line in f1:
            tput = float(line.split()[-1])
            if (tput > 0):
                net_tputs.append(tput)
            break


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

    if (COLLECT_MLC_TPUT > 0 and False):
        with open(FILE_NAME + '-MLCRUN-' + str(i) + '/mlc.log') as f1:
            for line in f1:
                if line.startswith(' 00000'):
                    tput = float(line.split()[-1])
                    if (tput >= 0):
                        mlc_tputs.append(tput)
                    break


net_tput_mean = statistics.mean(net_tputs)
cpu_utils_mean = statistics.mean(cpu_utils)

if NUM_RUNS > 1:
    net_tput_stddev = statistics.stdev(net_tputs)
    cpu_utils_stddev = statistics.stdev(cpu_utils)
else:
    net_tput_stddev = 0
    mem_bw_stddev = 0
    retx_rate_stddev = 0
    sent_packets_stddev = 0
    pcie_wr_tput_stddev = 0
    iotlb_hits_stddev = 0
    iotlb_misses_stddev = 0
    ctxt_misses_stddev = 0
    l1_misses_stddev = 0
    l2_misses_stddev = 0
    l3_misses_stddev = 0
    mem_read_stddev = 0
    cpu_utils_stddev = 0

mlc_tput_mean = 0
mlc_tput_stddev = 0

if (COLLECT_MLC_TPUT > 0):
    mlc_tput_mean = statistics.mean(mlc_tputs)
    if NUM_RUNS > 1:
        mlc_tput_stddev = statistics.stdev(mlc_tputs)
    else:
        mlc_tput_stddev = 0

# TODO: convert to tuple list and use zip with unpacking to make it cleaner to read and less error prone
output_list = [("cpu_utils_mean", cpu_utils_mean), ("cpu_utils_stddev", cpu_utils_stddev), ("net_tput_mean", net_tput_mean), ("net_tput_stddev", net_tput_stddev)]
headers, outputs = zip(*output_list)
headers = ",".join(headers) 
outputs = list(outputs)


# Save array to DAT file
np.savetxt(FILE_NAME + '/tput_metrics.dat',
           [outputs], delimiter=",", header=headers, comments='', fmt='%.10f')
