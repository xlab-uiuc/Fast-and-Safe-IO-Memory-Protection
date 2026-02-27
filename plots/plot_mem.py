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

def read_row(row) -> tuple[int, int]:

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

    # Path to memory stats
    path = "../utils/reports/" + sys.argv[i+1] + "/" + MEM_FILE

    x_tmp = []
    y_tmp = []

    with open(path) as f:

        time_start = 0
        reader = csv.DictReader(f)

        for num, row in enumerate(reader):

            x, y = read_row(row)

            x_tmp.append(num)
            y_tmp.append(y)

    print(x_tmp)
    print(y_tmp)

    plt.plot(x_tmp, y_tmp, label=name)

plt.ylabel("Memory Usage (MB)")
plt.xlabel("Samples")
plt.title("Memory Consumption Over Time")
plt.legend()
plt.savefig("mem_fig.png")
