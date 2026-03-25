import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set style for academic systems papers (SOSP/OSDI/EuroSys)
plt.rcParams.update({
    'font.family':        'serif',
    'font.serif':         ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size':          8,
    'axes.labelsize':     8,
    'axes.titlesize':     9,
    'legend.fontsize':    7,
    'xtick.labelsize':    7,
    'ytick.labelsize':    7,
    'pdf.fonttype':       42,   # Embed TrueType → camera-ready PDF
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

# Your specific data
cores = ['1 Core', '4 Cores', '8 Cores', '12 Cores', '16 Cores']

f1_vals = [4096, 7953.12, 20049.41, 58885.55, 14185042.7] # cache_tag_flush_range, outer lock
f2_vals = [3061.84, 3808.21, 3617.49, 5407.44, 3746.85] # qi_submit_sync, outer critical section
f3_vals = [12833.83, 14032.35, 16744.05, 18157.74, 18990.45] # trace_qi_submit_sync_cs, inner critical section

x = np.arange(len(cores))
width = 0.5

fig, ax = plt.subplots(figsize=(7.0, 3.2))  # ACM full text-width, compact height

# Professional colors and hatches for B&W readability
colors = ['#009E73', '#8bc4ac', '#961b4d']
hatches = ['', '', '', 'xx', '..', '++']
labels = ['cache_tag_flush_range', 'qi_submit_sync', 'trace_qi_submit_sync_cs']

# Linear scale with y-axis from 0 to 10^5
ax.set_ylim(0, 1e5)

ax.bar(x, f1_vals, width, label=labels[0], color=colors[0],
       edgecolor='black', linewidth=0.5, alpha=0.88, hatch=hatches[0])
ax.bar(x, f2_vals, width, bottom=f1_vals, label=labels[1], color=colors[1],
       edgecolor='black', linewidth=0.5, alpha=0.88, hatch=hatches[1])
ax.bar(x, f3_vals, width, bottom=np.array(f1_vals)+np.array(f2_vals), label=labels[2], color=colors[2],
       edgecolor='black', linewidth=0.5, alpha=0.88, hatch=hatches[2])

# Labels and formatting
ax.set_ylabel('Execution Time (ns)')
ax.set_xticks(x)
ax.set_xticklabels(cores)

# Legend
ax.legend(loc='upper left',
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

plt.savefig('linear_system_breakdown.png', bbox_inches='tight', dpi=300)
# plt.savefig('linear_system_breakdown.pdf', bbox_inches='tight')
print("Saved system_breakdown.pdf")
plt.close()