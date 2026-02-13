import sys

# Check if a filename was provided
if len(sys.argv) < 2:
    print("Usage: python script.py <filename>")
    sys.exit(1)

# Get the filename from the command line
filename = sys.argv[1]

values = {
    '4':[],
    '8':[],
    '16':[],
    '32':[],
    '64':[],
    '128':[],
    '256':[],
    '512':[],
    '1000':[],
    '2000':[]
}

# Open and read the file line by line
with open(filename, 'r') as file:
    for line in file:
        if "new value" in line:
            value = line.split(" ")[2].strip()
        if "throughput:" in line:
            tput = float(line.split(" ")[1])
            values[value].append(tput)

best_list = []
for key,value in values.items():
    if value:
        best = max(value)
        best_list.append(best)
        print(f"{key}KB: {best} Gbps") 

print(best_list)

#print(values)

