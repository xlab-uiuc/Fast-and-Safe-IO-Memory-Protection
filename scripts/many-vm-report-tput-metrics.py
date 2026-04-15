import os
import sys
import numpy as np

if len(sys.argv) < 3:
    print("Usage: python script.py <base_exp_name> <metrics> [num_vms]")
    print("  metrics: comma-separated list of: tput,cpu,all")
    print("  num_vms: optional, auto-detected if omitted")
    sys.exit(1)

# Get the directory where the script is located and change directory
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(script_dir)

base_exp_name = sys.argv[1]
metrics = list(map(str.lower, sys.argv[2].split(",")))
num_vms = int(sys.argv[3]) if len(sys.argv) > 3 else None

reports_dir = os.path.join("../utils/reports/")

# Auto-detect VM directories matching the base experiment name
vm_dirs = []
for entry in sorted(os.listdir(reports_dir)):
    full_path = os.path.join(reports_dir, entry)
    if not os.path.isdir(full_path):
        continue
    # Match per-VM directories: must start with base_exp_name, have a suffix, and not be a RUN dir
    suffix = entry[len(base_exp_name):]
    if entry.startswith(base_exp_name) and suffix and not entry.endswith(("-RUN-0", "-RUN-1", "-RUN-2")):
        vm_dirs.append(entry)

if num_vms is not None:
    vm_dirs = vm_dirs[:num_vms]

if not vm_dirs:
    print(f"No VM directories found matching '{base_exp_name}' in {reports_dir}")
    sys.exit(1)

# Collect per-VM results
all_tputs = []
all_cpus = []
all_client_cpus = []

print(f"======= Multi-VM Results: {base_exp_name} =======")
print(f"VMs found: {len(vm_dirs)}")
print()

for vm_dir in vm_dirs:
    metrics_file = os.path.join(reports_dir, vm_dir, "tput_metrics.dat")
    if not os.path.exists(metrics_file):
        print(f"--- {vm_dir} ---")
        print(f"  WARNING: tput_metrics.dat not found")
        print()
        continue

    results = np.genfromtxt(metrics_file, dtype=float, delimiter=',', names=True)

    tput = float(results['net_tput_mean'])
    cpu = float(results['cpu_utils_mean'])
    # client_cpu_utils_mean is a newer column; fall back to 0 for older runs
    client_cpu = float(results['client_cpu_utils_mean']) if 'client_cpu_utils_mean' in results.dtype.names else 0.0
    all_tputs.append(tput)
    all_cpus.append(cpu)
    all_client_cpus.append(client_cpu)

    print(f"--- {vm_dir} ---")
    if "tput" in metrics or "all" in metrics:
        print(f"  Throughput:      {tput:.4f} Gbps")
    if "cpu" in metrics or "all" in metrics:
        print(f"  CPU Util:        {cpu:.4f} %")
        print(f"  Client CPU Util: {client_cpu:.4f} %")
    print()

# Aggregate summary
if all_tputs:
    print(f"======= Aggregate ({len(all_tputs)} VMs) =======")
    if "tput" in metrics or "all" in metrics:
        print(f"  Total Throughput:       {sum(all_tputs):.4f} Gbps")
        print(f"  Mean Throughput:        {np.mean(all_tputs):.4f} Gbps")
        if len(all_tputs) > 1:
            print(f"  Stddev Throughput:      {np.std(all_tputs, ddof=1):.4f} Gbps")
    if "cpu" in metrics or "all" in metrics:
        print(f"  Mean CPU Util:          {np.mean(all_cpus):.4f} %")
        if len(all_cpus) > 1:
            print(f"  Stddev CPU Util:        {np.std(all_cpus, ddof=1):.4f} %")
        print(f"  Mean Client CPU Util:   {np.mean(all_client_cpus):.4f} %")
        if len(all_client_cpus) > 1:
            print(f"  Stddev Client CPU Util: {np.std(all_client_cpus, ddof=1):.4f} %")
    print()
