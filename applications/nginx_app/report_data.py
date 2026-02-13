import os
import sys
import numpy as np
import re

def convert_to_gigabits(size_str):
    regex = re.compile(r'(\d+(?:\.\d+)?)\s*([kmgtp]?b)', re.IGNORECASE)

    order = ['b', 'kb', 'mb', 'gb', 'tb', 'pb']

    for value, unit in regex.findall(size_str):
        bytes = int(float(value) * (1000**order.index(unit.lower())))

    # Convert the value to bytes
    #bytes = int(num_part * units[unit_part])
    return round((bytes/(1000000000)) * 8, 3)

# Check if the directory argument is provided
if len(sys.argv) != 2:
    print("Usage: python script.py <exp_name>")
    sys.exit(1)

# Get the directory from the command line argument
directory = f"logs/{sys.argv[1]}"
#req_size  = float(sys.argv[2])

# Initialize an empty list to store the data
data_list = []

# Loop through each file in the directory
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    # Read the CSV file into a NumPy array
    with open(file_path,'r') as file:
        for line in file:
            if "Transfer/sec" in line:
                transfer_rate = line.split()[-1]
                #print(convert_to_gigabits(transfer_rate))
                data_list.append(convert_to_gigabits(transfer_rate))
        #data_list.append(rps)


# calculate total requests per second
#rps = sum(data_list)
#print(rps)
#throughput = rps * req_size
print(f"throughput: {round(sum(data_list),3)} Gbps")
