import sys

INPUT_FILE = sys.argv[1]

cpu_util = {}
num_samples = {}

header_len = None
cpu_index = None
idle_index = None

with open(INPUT_FILE) as f:
    for line in f:
        elements = line.split()
        if not elements or 'Linux' in elements[0] or 'CPU' not in elements:
            continue
        if '%idle' in elements:
            header_len = len(elements)
            cpu_index = elements.index('CPU')
            idle_index= elements.index('%idle')
            break

    if header_len is None or cpu_index is None or idle_index is None:
        print("ERROR: could not find SAR header with 'CPU' and '%idle'", file=sys.stderr)
        sys.exit(1)
    
    f.seek(0)

    for line in f:
        elements = line.split()
        if len(elements) == header_len and elements[cpu_index] != "CPU":
            cpu = int(elements[cpu_index])
            idle = float(elements[idle_index])
            
            if cpu not in cpu_util:
                cpu_util[cpu]    = 0.0
                num_samples[cpu] = 0
            
            cpu_util[cpu] += (100 - idle)
            num_samples[cpu] += 1

total_util = 0
num_cpus = 0
for cpu in cpu_util:
    if num_samples[cpu] != 0:
        cpu_util[cpu] /= num_samples[cpu]
        total_util += cpu_util[cpu]
        num_cpus += 1

print("cpu_utils: ",cpu_util)
print("num_samples: ",num_samples)
print("avg_cpu_util: ",total_util/num_cpus)
