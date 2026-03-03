import calendar
import csv
import os
import sys
import time
import matplotlib.pyplot as plt
import numpy as np

# Name of the CSV file contaning memory stats
MEM_FILE = "memory_stats.csv"

# ACM paper-ready style (matches leshna_plot_nested.py)
plt.rcParams.update({
    'font.size':        8,
    'font.family':      'serif',
    'font.serif':       ['Times New Roman', 'DejaVu Serif', 'serif'],
    'pdf.fonttype':     42,
    'ps.fonttype':      42,
    'axes.grid':        True,
    'axes.axisbelow':   True,
    'grid.alpha':       0.35,
    'grid.linestyle':   '--',
    'grid.linewidth':   0.5,
    'axes.linewidth':   0.7,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
})

def read_row(row):

    # Convert the timestamp into epoch

    time_str = row["timestamp"]

    utc_time = time.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f%z")

    print(utc_time)

    epoch = calendar.timegm(utc_time)

    return (epoch, int(int(row["mem_used"]) / (1024 ** 2)))

if len(sys.argv) % 2 == 0:
    raise Exception("Arguments must be name and file path!")

def plot_fig(fig, output_dir=None):

    # All X data retrievd from the experiments
    X_DATA = []

    # Used stats for each experiment
    USED = []

    # Buff stats for each experiment
    BUFF = []

    for exp in fig:

        # Path to memory stats
        path = "../utils/reports/" + exp['tag'] + "/" + MEM_FILE

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

    # --- Memory Usage plot ---
    plt.figure(figsize=(7.0, 3.2))

    for num, exp in enumerate(USED):
        plt.plot(X_DATA[num], exp, label=fig[num]['name'], color=fig[num]['color'], linewidth=1.2)

    plt.ylabel("Memory Usage (MB)", fontsize=9)
    plt.xlabel("Samples", fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(loc='upper left',
               ncol=1,
               fontsize=7,
               frameon=True,
               framealpha=0.85,
               edgecolor='#cccccc',
               borderpad=0.4,
               labelspacing=0.25,
               handlelength=1.4,
               handletextpad=0.4)
    plt.tight_layout(pad=0.4)

    use_path = os.path.join(output_dir, "mem_fig_use.pdf") if output_dir else "mem_fig_use.pdf"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    plt.savefig(use_path, bbox_inches='tight', format='pdf')
    print(f'Saved plot to {use_path}')
    plt.close()

    # --- Buffer Cache plot ---
    plt.figure(figsize=(7.0, 3.2))

    for num, exp in enumerate(BUFF):
        plt.plot(X_DATA[num], exp, label=fig[num]['name'], color=fig[num]['color'], linewidth=1.2)

    plt.ylabel("Buffer Cache Usage (MB)", fontsize=9)
    plt.xlabel("Samples", fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(loc='upper left',
               ncol=1,
               fontsize=7,
               frameon=True,
               framealpha=0.85,
               edgecolor='#cccccc',
               borderpad=0.4,
               labelspacing=0.25,
               handlelength=1.4,
               handletextpad=0.4)
    plt.tight_layout(pad=0.4)

    buff_path = os.path.join(output_dir, "mem_fig_buff.pdf") if output_dir else "mem_fig_buff.pdf"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    plt.savefig(buff_path, bbox_inches='tight', format='pdf')
    print(f'Saved plot to {buff_path}')
    plt.close()

# TODO: Rerun with 24 cores in vanilla case 
plot_data = [
    {"name": "Async+DFP", "color": "#F0E442", "tag": "2026-03-02-17-51-36-6.12.9-iommufd-vanilla-nested-conf-call-flow24-host-strict-guest-strict-nested-24cores-RUN-0"},
    {"name": "Async", "color": "#56B4E9", "tag": "2026-03-02-17-57-43-6.12.9-iommufd-vanilla-nested-conf-call-flow24-host-strict-guest-strict-nested-24cores-RUN-0"},
    {"name": "Off", "color": "#0072B2", "tag": "2026-03-02-19-44-07-6.12.9-iommufd-flow24-host-strict-guest-off-off-24cores-ringbuf512-sockbuf1-RUN-0"},
    {"name": "Nested", "color": "#009E73", "tag": "2026-03-02-19-48-57-6.12.9-iommufd-flow24-host-strict-guest-strict-nested-24cores-ringbuf512-sockbuf1-RUN-0"}
]

plot_fig(plot_data)
