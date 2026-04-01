import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

default_colors = [
    '#6BAED6', '#E57373', '#F2A6A6', '#74C476', '#A1D99B', '#BDD7E7',
    '#D98880', '#8FD19E', '#9ECAE1', '#F28E8E', '#98D89E', '#C7A27C',
    '#9FD6D2', '#C6A0C9', '#F7B267', '#F3DD6D', '#D3D3D3', '#A3C76D',
    '#D8A2B0', '#A8C3C5'
]


def calculate_plot_params(num_x_labels, num_series, max_width=None):
    base_width = 7.0
    base_height = 3.2
    base_gap = 1.8

    width_scale = 1.0 + (num_x_labels - 3) * 0.10
    width_scale = max(width_scale, 1.0)
    width_scale = min(width_scale, 2.2)

    height_scale = 1.0 + (num_series - 2) * 0.1
    height_scale = max(height_scale, 1.0)
    height_scale = min(height_scale, 2.0)

    final_width = base_width * width_scale
    if max_width:
        final_width = min(final_width, max_width)

    gap_factor = base_gap
    if num_x_labels > 20:
        gap_factor = 1.0
    elif num_x_labels > 10:
        gap_factor = 1.2
    elif num_x_labels < 5:
        gap_factor = 2.0

    return {
        'figsize': (final_width, base_height * height_scale),
        'font_size': 15,
        'legend_fontsize': 15,
        'label_fontsize': 17,
        'gap_factor': gap_factor,
    }

# ── Experiment paths ──────────────────────────────────────────────────────────
SCRIPT_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REPO_ROOT = "/home/siyuanc3/Fast-and-Safe-IO-Memory-Protection"
REPO_ROOT = os.path.abspath(os.environ.get("FSIO_REPO_ROOT", DEFAULT_REPO_ROOT))

TARGET_CORES = [1, 4, 8, 12, 16, 20, 24]

# FOR some reason, we miss perf data for 4 cores
exps = [
    os.path.join(
        REPO_ROOT,
        f"utils/reports/2026-03-24-15-08-11-6.12.9-iommufd-RX-flow{i:02d}-"
        f"host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-"
        f"{'RUN-1' if i == 4 else 'RUN-0'}"
    )
    for i in TARGET_CORES
]

# ── Colors per exit reason ────────────────────────────────────────────────────
EXIT_COLORS = {
    'EPT_MISCONFIG': '#4E79A7',
    'HLT': '#F28E2B',
    'Other': '#59A14F',
}
EXIT_ORDER = ['EPT_MISCONFIG', 'HLT', 'Other']

# ── Load data ─────────────────────────────────────────────────────────────────
perf_rows = []
unmap_counts = []

for cores, exp_dir in zip(TARGET_CORES, exps):
    # --- perf CSV ---
    perf_csv = os.path.join(exp_dir, "perf_kvm_nested_cores.csv")
    try:
        df = pd.read_csv(perf_csv)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Missing perf CSV: {perf_csv}\n"
            f"Current REPO_ROOT={REPO_ROOT}\n"
            f"Set FSIO_REPO_ROOT to override it, for example:\n"
            f"FSIO_REPO_ROOT={SCRIPT_REPO_ROOT} python3 {os.path.basename(__file__)}"
        ) from exc
    except PermissionError as exc:
        raise PermissionError(
            f"Cannot read perf CSV: {perf_csv}\n"
            f"Current REPO_ROOT={REPO_ROOT}\n"
            f"Run this script as a user that can read that tree, or point "
            f"FSIO_REPO_ROOT at a readable copy."
        ) from exc
    for _, row in df.iterrows():
        perf_rows.append({
            'cores':              cores,
            'exit_reason':        row['exit_reason'],
            'samples':            row['samples'],
            'exit_total_time_ns': row['exit_total_time_ns'],
        })

    # --- eBPF CSV (CPU 0 unmap count) ---
    ebpf_csv = os.path.join(exp_dir, "ebpf_guest_stats.csv")
    try:
        ebpf_df = pd.read_csv(ebpf_csv, comment='#')
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Missing eBPF CSV: {ebpf_csv}\n"
            f"Current REPO_ROOT={REPO_ROOT}\n"
            f"Set FSIO_REPO_ROOT to override it if needed."
        ) from exc
    except PermissionError as exc:
        raise PermissionError(
            f"Cannot read eBPF CSV: {ebpf_csv}\n"
            f"Current REPO_ROOT={REPO_ROOT}\n"
            f"Run this script as a user that can read that tree, or point "
            f"FSIO_REPO_ROOT at a readable copy."
        ) from exc
    ebpf_df.columns = ebpf_df.columns.str.strip()
    mask = (ebpf_df['function'] == '__iommu_unmap') & (ebpf_df['cpu'].astype(str) == '0')
    counts = ebpf_df.loc[mask, 'count']
    counts = pd.to_numeric(counts, errors='coerce').dropna()
    unmap_counts.append(int(counts.iloc[0]) if len(counts) > 0 else 0)

perf_df = pd.DataFrame(perf_rows)

# Collapse minor exit reasons into 'Other'
TOP_EXITS = ['EPT_MISCONFIG', 'HLT']
perf_df['exit_group'] = perf_df['exit_reason'].apply(
    lambda r: r if r in TOP_EXITS else 'Other'
)
perf_df = perf_df.groupby(['cores', 'exit_group'], as_index=False).sum(numeric_only=True)

# Pivot tables: rows = cores, cols = exit_group
samples_pivot = perf_df.pivot(index='cores', columns='exit_group', values='samples').fillna(0)
time_pivot    = perf_df.pivot(index='cores', columns='exit_group', values='exit_total_time_ns').fillna(0)

# Total samples per core count (for vm-exits-per-unmap)
total_samples = samples_pivot.reindex(TARGET_CORES, fill_value=0).sum(axis=1).values

# Per-type time per unmap pivot
unmap_arr = np.array([uc if uc > 0 else np.nan for uc in unmap_counts])
time_per_unmap_pivot = time_pivot.reindex(TARGET_CORES, fill_value=0).div(unmap_arr, axis=0)

# ── Plot ──────────────────────────────────────────────────────────────────────
params = calculate_plot_params(len(TARGET_CORES), len(EXIT_COLORS), max_width=7.0)

plt.rcParams.update({
    'font.size': params['font_size'],
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.grid': True,
    'axes.axisbelow': True,
    'grid.alpha': 0.35,
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'axes.linewidth': 0.7,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
})

x = np.arange(len(TARGET_CORES)) * params['gap_factor']
xlabels = [f"{c}" for c in TARGET_CORES]
bar_width = 0.775
line_width = 0.8
hatches = {
    'EPT_MISCONFIG': '',
    'HLT': '..',
    'Other': 'xx',
}

def stacked_bar(ax, pivot, ylabel, scale=1.0, unit=''):
    bottoms = np.zeros(len(TARGET_CORES))
    for reason in EXIT_ORDER:
        if reason not in pivot.columns:
            continue
        vals = pivot.reindex(TARGET_CORES, fill_value=0)[reason].values / scale
        ax.bar(x, vals, bar_width, bottom=bottoms,
               color=EXIT_COLORS[reason], label=reason, alpha=0.88,
               edgecolor='black', linewidth=line_width, hatch=hatches[reason])
        bottoms += vals
    ax.set_ylabel(ylabel, fontsize=params['label_fontsize'])
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=params['font_size'])
    ax.tick_params(axis='y', labelsize=params['font_size'])
    if unit:
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}{unit}")
        )

def make_single(pivot, ylabel, title, legend_loc, outfile, **kwargs):
    fig, ax = plt.subplots(figsize=params['figsize'])
    stacked_bar(ax, pivot, ylabel, **kwargs)
    ax.set_xlabel('Number of Cores', fontsize=params['label_fontsize'])
    ax.legend(loc='lower center',
              bbox_to_anchor=(0.5, 1.0005),
              ncol=min(len(EXIT_COLORS), 3),
              fontsize=params['legend_fontsize'],
              frameon=True,
              framealpha=0.85,
              edgecolor='#cccccc',
              borderpad=0.4,
              labelspacing=0.25,
              handlelength=1.4,
              handletextpad=0.4,
              columnspacing=1.0)
    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.18, top=0.84)
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Saved {outfile}")
    plt.close()

def make_broken_axis(pivot, ylabel, title, legend_loc, outfile,
                     break_low=None, break_high=None, ratio=(2, 1), **kwargs):
    """Stacked bar with a broken y-axis to handle outlier values."""
    scale = kwargs.get('scale', 1.0)
    totals = pivot.reindex(TARGET_CORES, fill_value=0).sum(axis=1).values / scale

    # Auto-detect break point from largest gap between sorted totals
    if break_low is None or break_high is None:
        sorted_vals = np.sort(totals[totals > 0])
        if len(sorted_vals) >= 2:
            gaps = np.diff(sorted_vals)
            gap_idx = int(np.argmax(gaps))
            break_low  = sorted_vals[gap_idx] * 1.15
            break_high = sorted_vals[gap_idx + 1] * 0.85
        else:
            make_single(pivot, ylabel, title, legend_loc, outfile, **kwargs)
            return

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(params['figsize'][0], params['figsize'][1] * 1.1), sharex=True,
        gridspec_kw={'height_ratios': list(ratio), 'hspace': 0.05}
    )

    for ax in (ax_top, ax_bot):
        stacked_bar(ax, pivot, '', **kwargs)
        ax.set_ylabel('')

    ax_top.set_ylim(break_high, totals.max() * 1.12)
    ax_bot.set_ylim(0, break_low)
    ax_bot.set_yticks([50])
    ax_top.set_yticks([200, 300, 400, 500, 600])

    # Hide the spines at the break
    ax_top.spines['bottom'].set_visible(False)
    ax_bot.spines['top'].set_visible(False)
    ax_top.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    ax_bot.xaxis.tick_bottom()

    # Diagonal break marks on both sides
    d = 0.015
    kw_d = dict(color='k', clip_on=False, linewidth=0.8, zorder=10)
    ax_top.plot((-d, +d), (-d, +d), transform=ax_top.transAxes, **kw_d)
    ax_top.plot((1-d, 1+d), (-d, +d), transform=ax_top.transAxes, **kw_d)
    ax_bot.plot((-d, +d), (1-d, 1+d), transform=ax_bot.transAxes, **kw_d)
    ax_bot.plot((1-d, 1+d), (1-d, 1+d), transform=ax_bot.transAxes, **kw_d)

    ax_top.tick_params(axis='y', labelsize=params['font_size'])
    ax_bot.tick_params(axis='y', labelsize=params['font_size'])
    fig.text(0.005, 0.5, ylabel, va='center', rotation='vertical', fontsize=params['label_fontsize'])
    ax_bot.set_xlabel('Number of Cores', fontsize=params['label_fontsize'])
    ax_top.legend(loc='lower center',
                  bbox_to_anchor=(0.5, 1.0005),
                  ncol=min(len(EXIT_COLORS), 3),
                  fontsize=params['legend_fontsize'],
                  frameon=True,
                  framealpha=0.85,
                  edgecolor='#cccccc',
                  borderpad=0.4,
                  labelspacing=0.25,
                  handlelength=1.4,
                  handletextpad=0.4,
                  columnspacing=1.0)

    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.18, top=0.84, hspace=0.10)
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Saved {outfile}")
    plt.close()

make_single(samples_pivot,      '# VM Exits',                  'VM Exit Counts by Type',             'upper left',  'vm_exit_counts.pdf')
make_single(time_pivot,         'Total Exit Time (us)',          'Total VM Exit Time by Type',          'upper left',  'vm_exit_time.pdf', scale=1000.0)
make_broken_axis(time_per_unmap_pivot, 'VM exit time per unmap (us)', 'VM Exit Time per Unmap Call by Type', 'upper right', 'vm_exit_time_per_unmap.pdf', scale=1000.0, break_low=50, break_high=100)
