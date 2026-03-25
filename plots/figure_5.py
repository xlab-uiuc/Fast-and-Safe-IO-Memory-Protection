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

# Your specific data
cores = ['1 Core', '4 Cores', '8 Cores', '12 Cores', '16 Cores', '20 Cores', '24 Cores']
# cores = ['1', '4', '8', '12', '16', '20', '24']

EPT_MISCONFIG =[93.97,97.07,93.84,75.53,14.29,2.69,2.17]
HLT=[0.89,0.4,3.65,18.79,81.96,96.38,97.09]

x = np.arange(len(cores))

fig, ax = plt.subplots(figsize=(7.0, 3.2))

ax.plot(x, HLT, color='#009E73', linewidth=1.4, marker='o', markersize=4,
        markeredgecolor='black', markeredgewidth=0.5, label='HLT')
ax.plot(x, EPT_MISCONFIG, color='#961b4d', linewidth=1.4, marker='s', markersize=4,
        markeredgecolor='black', markeredgewidth=0.5, label='EPT_MISCONFIG',
        linestyle='--')

for i, (hv, ev) in enumerate(zip(HLT, EPT_MISCONFIG)):
    ax.text(x[i], hv + 3, f"{hv:.1f}%", ha='right', va='bottom',
            fontsize=7, color='#009E73')
    ax.text(x[i], ev + 3, f"{ev:.1f}%", ha='left', va='bottom',
            fontsize=7, color='#961b4d')


# Shade the crossover region for emphasis
# ax.axvspan(2.5, 3.5, color='#999999', alpha=0.12, linewidth=0)
# ax.text(3.0, 52, 'crossover', ha='center', va='center',
#         fontsize=6, color='#555555', style='italic')

ax.set_ylabel('VM Exit Time Share (%)')
ax.set_xlabel('Number of Cores (1 flow/core)')
ax.set_ylim(0, 112)
ax.set_xticks(x)
ax.set_xticklabels(cores)

ax.legend(loc='center right',
          ncol=1,
          fontsize=7,
          frameon=True,
          framealpha=0.85,
          edgecolor='#cccccc',
          borderpad=0.4,
          labelspacing=0.25,
          handlelength=1.8,
          handletextpad=0.4)

# Remove top/right spines — standard in systems paper figures
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)

plt.tight_layout(pad=0.4)

plt.savefig('vm_exit_line_labelled.pdf', bbox_inches='tight')
print("Saved vm_exit_line.pdf")
plt.close()