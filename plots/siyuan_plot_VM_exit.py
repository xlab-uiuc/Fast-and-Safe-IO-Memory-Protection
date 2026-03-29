import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# ── Style ─────────────────────────────────────────────────────────────────────
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

# ── Experiment paths ──────────────────────────────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    'HLT':           '#009E73',
    'EPT_MISCONFIG': '#961b4d',
    'Other':         '#999999',
}

# ── Load data ─────────────────────────────────────────────────────────────────
perf_rows = []
unmap_counts = []

for cores, exp_dir in zip(TARGET_CORES, exps):
    # --- perf CSV ---
    perf_csv = os.path.join(exp_dir, "perf_kvm_nested_cores.csv")
    df = pd.read_csv(perf_csv)
    for _, row in df.iterrows():
        perf_rows.append({
            'cores':              cores,
            'exit_reason':        row['exit_reason'],
            'samples':            row['samples'],
            'exit_total_time_ns': row['exit_total_time_ns'],
        })

    # --- eBPF CSV (CPU 0 unmap count) ---
    ebpf_csv = os.path.join(exp_dir, "ebpf_guest_stats.csv")
    ebpf_df = pd.read_csv(ebpf_csv, comment='#')
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
x = np.arange(len(TARGET_CORES))
xlabels = [f"{c}" for c in TARGET_CORES]
bar_width = 0.6

def stacked_bar(ax, pivot, ylabel, scale=1.0, unit=''):
    bottoms = np.zeros(len(TARGET_CORES))
    for reason in list(EXIT_COLORS.keys()):
        if reason not in pivot.columns:
            continue
        vals = pivot.reindex(TARGET_CORES, fill_value=0)[reason].values / scale
        ax.bar(x, vals, bar_width, bottom=bottoms,
               color=EXIT_COLORS[reason], label=reason)
        bottoms += vals
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels)
    if unit:
        ax.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:.0f}{unit}")
        )

def make_single(pivot, ylabel, title, legend_loc, outfile, **kwargs):
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    stacked_bar(ax, pivot, ylabel, **kwargs)
    ax.set_title(title)
    ax.set_xlabel('Number of Cores (1 flow/core)')
    ax.legend(loc=legend_loc, ncol=2, fontsize=6, framealpha=0.85)
    plt.tight_layout(pad=0.4)
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
        2, 1, figsize=(7.0, 3.5), sharex=True,
        gridspec_kw={'height_ratios': list(ratio), 'hspace': 0.05}
    )

    for ax in (ax_top, ax_bot):
        stacked_bar(ax, pivot, '', **kwargs)
        ax.set_ylabel('')

    ax_top.set_ylim(break_high, totals.max() * 1.12)
    ax_bot.set_ylim(0, break_low)

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

    fig.text(0.01, 0.5, ylabel, va='center', rotation='vertical', fontsize=8)
    ax_bot.set_xlabel('Number of Cores (1 flow/core)')
    ax_top.set_title(title)
    ax_top.legend(loc=legend_loc, ncol=2, fontsize=6, framealpha=0.85)

    plt.tight_layout(pad=0.4)
    fig.subplots_adjust(left=0.12)
    plt.savefig(outfile, bbox_inches='tight')
    print(f"Saved {outfile}")
    plt.close()

make_single(samples_pivot,      '# VM Exits',                  'VM Exit Counts by Type',             'upper left',  'vm_exit_counts.pdf')
make_single(time_pivot,         'Total Exit Time (ns)',         'Total VM Exit Time by Type',          'upper left',  'vm_exit_time.pdf')
make_broken_axis(time_per_unmap_pivot, 'Exit Time / Unmap (ns) (CPU 0)', 'VM Exit Time per Unmap Call by Type', 'upper right', 'vm_exit_time_per_unmap.pdf')
