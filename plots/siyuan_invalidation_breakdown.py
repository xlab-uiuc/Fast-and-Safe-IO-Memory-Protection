import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
from io import StringIO

plt.rcParams.update({
    'font.family':        'serif',
    'font.serif':         ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size':          8,
    'axes.labelsize':     8,
    'axes.titlesize':     9,
    'legend.fontsize':    7,
    'xtick.labelsize':    7,
    'ytick.labelsize':    7,
    'pdf.fonttype':       42,
    'ps.fonttype':        42,
    'axes.grid':          True,
    'axes.axisbelow':     True,
    'grid.alpha':         0.35,
    'grid.linestyle':     '--',
    'grid.linewidth':     0.5,
    'axes.linewidth':     0.7,
    'xtick.major.width':  0.6,
    'ytick.major.width':  0.6,
})

TARGET_CORES = [1, 4, 8, 12, 16, 20, 24]

exps = [
    f"/home/schai/viommu_siyuan/utils/reports/2026-03-24-15-08-11-6.12.9-iommufd-RX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-" for i in TARGET_CORES
]


def get_tput_from_dat(exp_name, run_id):
    exp_name = exp_name.rstrip('/')
    file = os.path.join(exp_name + "RUN-" + str(run_id), "iperf.bw.rpt")
    if not os.path.exists(file):
        return None

    tput = 0
    with open(file, 'r') as f1:
        for line in f1:
            if line.startswith('Avg_iperf_tput:'):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        tput = float(parts[-1])
                    except ValueError:
                        pass
                break
    if tput == 0:
        print(f"WARNING: Tput is 0 for experiment {exp_name} run {run_id}")
    return tput


def parse_aggregate_stats(csv_path):
    """Parse the '# Per-Function Latency Statistics' section and return
    a dict mapping function_name -> mean_ns."""
    with open(csv_path, 'r') as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("# Per-Function Latency Statistics"):
            start_idx = i + 1
        elif start_idx is not None and line.strip().startswith("#"):
            end_idx = i
            break

    if start_idx is None:
        raise ValueError(f"Could not find aggregate section in {csv_path}")
    if end_idx is None:
        end_idx = len(lines)

    import csv as csvmod
    header = lines[start_idx].strip()
    data_lines = [l.strip() for l in lines[start_idx + 1:end_idx]
                  if l.strip() and not l.strip().startswith("#")]
    reader = csvmod.DictReader(StringIO(header + "\n" + "\n".join(data_lines)))
    stats = {}
    for row in reader:
        stats[row['function']] = float(row['mean_ns'])
    return stats


ir_sub_vals = []
ir_prep_vals = []
lock_contention_vals = []
tput_vals = []

for idx, nc in enumerate(TARGET_CORES):
    csv_path = exps[idx] + "RUN-0/ebpf_guest_stats.csv"
    print(f"Parsing eBPF stats from {csv_path}")
    stats = parse_aggregate_stats(csv_path)

    tput = get_tput_from_dat(exps[idx], 0)
    tput_vals.append(tput)

    t_flush_range = stats['cache_tag_flush_range']
    t_qi_submit    = stats['qi_submit_sync']
    t_flush_iotlb  = stats['cache_tag_flush_iotlb']

    ir_sub  = t_qi_submit
    ir_prep = t_flush_iotlb
    lock_contention = max(t_flush_range - ir_sub - ir_prep, 0)

    ir_sub_vals.append(ir_sub)
    ir_prep_vals.append(ir_prep)
    lock_contention_vals.append(lock_contention)

    print(f"{nc:2d} cores | tput={tput}  flush_range={t_flush_range:.1f}  "
          f"qi_submit={t_qi_submit:.1f}  flush_iotlb={t_flush_iotlb:.1f}  "
          f"lock_contention={lock_contention:.1f}")

cores_labels = [f'{c} Core{"s" if c > 1 else ""}' for c in TARGET_CORES]
x = np.arange(len(TARGET_CORES))
width = 0.5

ir_sub_arr  = np.array(ir_sub_vals)
ir_prep_arr = np.array(ir_prep_vals)
lock_arr    = np.array(lock_contention_vals)

fig, (ax_top, ax_bot) = plt.subplots(2, 1, sharex=True, figsize=(7.0, 3.6),
                                     gridspec_kw={'height_ratios': [1, 2],
                                                  'hspace': 0.06})

break_lo = 100000
break_hi = 200000

colors  = ['#009E73', '#8bc4ac', '#961b4d']
hatches = ['', '', '']
labels  = ['Lock contention',
           'IR-PREP',
           'IR-SUB']

line_width = 0.1

for ax in (ax_bot, ax_top):
    ax.bar(x, lock_arr, width, label=labels[0], color=colors[0],
           edgecolor='black', linewidth=line_width, alpha=0.88, hatch=hatches[0])
    ax.bar(x, ir_prep_arr, width, bottom=lock_arr, label=labels[1], color=colors[1],
           edgecolor='black', linewidth=line_width, alpha=0.88, hatch=hatches[1])
    ax.bar(x, ir_sub_arr, width, bottom=lock_arr + ir_prep_arr, label=labels[2],
           color=colors[2], edgecolor='black', linewidth=line_width, alpha=0.88, hatch=hatches[2])

ax_bot.set_ylim(0, break_lo)
ax_top.set_ylim(break_hi, max(lock_arr + ir_prep_arr + ir_sub_arr) * 1.08)

ax_top.spines['bottom'].set_visible(False)
ax_bot.spines['top'].set_visible(False)
ax_top.tick_params(bottom=False)

d = 0.012
kwargs = dict(transform=ax_top.transAxes, color='k', clip_on=False, linewidth=0.8)
ax_top.plot((-d, +d), (0 - d, 0 + d), **kwargs)
ax_top.plot((1 - d, 1 + d), (0 - d, 0 + d), **kwargs)
kwargs.update(transform=ax_bot.transAxes)
ax_bot.plot((-d, +d), (1 - d, 1 + d), **kwargs)
ax_bot.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)

ax_bot.set_xticks(x)
ax_bot.set_xticklabels(cores_labels)
fig.text(0.01, 0.5, 'Execution Time (ns)', va='center', rotation='vertical', fontsize=8)

ax_top.legend(loc='upper left',
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
fig.subplots_adjust(hspace=0.06)

out_pdf = 'siyuan_invalidation_breakdown.pdf'
plt.savefig(out_pdf, bbox_inches='tight')
print(f"Saved and {out_pdf}")
plt.close()
