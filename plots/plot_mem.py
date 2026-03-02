import calendar
import csv
import sys
import time
import matplotlib.pyplot as plt
import numpy as np

# Name of the CSV file contaning memory stats
MEM_FILE = "memory_stats.csv"

# Contains name and file tuples
files = []

# All X data retrievd from the experiments
X_DATA = []

# Used stats for each experiment
USED = []

# Buff stats for each experiment
BUFF = []

def read_row(row):

    # Convert the timestamp into epoch

    time_str = row["timestamp"]

    utc_time = time.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f%z")

    print(utc_time)

    epoch = calendar.timegm(utc_time)

    return (epoch, int(int(row["mem_used"]) / (1024 ** 2)))

if len(sys.argv) % 2 == 0:
    raise Exception("Arguments must be name and file path!")

for i in range(1, len(sys.argv), 2):

    print(i)

    # Name of this experiment on the graph
    name = str(sys.argv[i])

    files.append(name)

    # Path to memory stats
    path = "../utils/reports/" + sys.argv[i+1] + "/" + MEM_FILE

    x_tmp = []
    y_tmp = []
    buff_tmp = []

    with open(path) as f:

        time_start = 0
        reader = csv.DictReader(f)

        for num, row in enumerate(reader):

            x, y = read_row(row)

            x_tmp.append(num)
            y_tmp.append(y)

            buff_tmp.append(int(int(row['mem_buff_cache']) / (1024 ** 2)))

    print(x_tmp)
    print(y_tmp)

    X_DATA.append(x_tmp)
    USED.append(y_tmp)
    BUFF.append(buff_tmp)

for num, exp in enumerate(USED):

    plt.plot(X_DATA[num], exp, label=files[num])

plt.ylabel("Memory Usage (MB)")
plt.xlabel("Samples")
plt.title("Memory Consumption Over Time")
plt.legend()
plt.savefig("mem_fig_use.png")

plt.clf()

for num, exp in enumerate(BUFF):

    plt.plot(X_DATA[num], exp, label=files[num])

plt.ylabel("Buffer Cache Usage (MB)")
plt.xlabel("Samples")
plt.title("Buffer Cache Usage Over Time")
plt.legend()
plt.savefig("mem_fig_buff.png")
