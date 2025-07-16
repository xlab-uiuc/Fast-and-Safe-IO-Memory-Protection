import sys
import csv
import os


EXPERIMENT = sys.argv[1]
os.system("mkdir -p " + "logs/" + EXPERIMENT)
os.system("mkdir -p " + "reports/" + EXPERIMENT)
INPUT_FILE = "logs/" + EXPERIMENT + '/tcp.trace.log'
OUTPUT_FILE = "reports/" + EXPERIMENT + '/tcp.trace.csv'

records = []

with open(INPUT_FILE) as f1:
    for line in f1:
        if line.startswith('#') or 'tcp_probe:' not in line:
            continue
        else:
            tokens  = line.split()
            record = {}

            ts = tokens[3].rstrip(':')
            record['time_s'] = float(ts)

            def get_val(key):
                tok = next((t for t in tokens if t.startswith(key + '=')), None)
                return tok.split('=',1)[1] if tok else None
            
            for end in ('src','dest'):
                val = get_val(end)
                if not val:
                    break  # malformed line
                clean = val.strip('[]')
                ip, port = clean.rsplit(':', 1)
                record[f'{end}_ip']   = ip
                record[f'{end}_port'] = int(port, 10)

            for key in ('snd_nxt','snd_una','snd_cwnd',
                    'ssthresh','snd_wnd','srtt','rcv_wnd'):
                val = get_val(key)
                if val is None:
                    continue
                record[key] = int(val, 0)

            records.append(record)

assert(len(records) > 0)
columns = list(records[0].keys())
csv_file = OUTPUT_FILE

try:
    with open(csv_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for data in records:
            writer.writerow(data)
except IOError:
    print("I/O error")

