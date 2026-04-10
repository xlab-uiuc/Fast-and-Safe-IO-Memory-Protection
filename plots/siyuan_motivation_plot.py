
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas as pd

default_colors = ['#0072B2', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00','#D55E00', '#999999', '#FF6600',
                     '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
                     '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']

color_off = default_colors[0]
color_nested = default_colors[1]
color_shadow = default_colors[2]    
color_optimization = default_colors[3]

def calculate_plot_params(num_x_labels, num_series, max_width=None):
    """
    Dynamically calculate plot parameters based on data dimensions.
    
    Args:
        num_x_labels: Number of x-axis categories
        num_series: Number of data series being plotted
        max_width: Optional maximum width for the figure
    
    Returns:
        dict with keys: 'figsize', 'font_size', 'bar_width', 'gap_factor', 
                       'legend_fontsize', 'label_fontsize', 'show_value_labels'
    """
    # # Base values for minimal case (2-3 labels, 2 series)
    # base_width = 10
    # base_height = 6
    # base_font = 10
    # base_bar_width = 0.38
    # base_gap = 1.5

    # Base values — ACM two-column text width is 7", keep height compact for papers
    base_width = 7.0   # full ACM text width
    base_height = 3.2  # compact height; tall figures waste column space
    base_font = 14   # 8pt matches ACM 9pt body text when figure is scaled
    base_bar_width = 0.38
    base_gap = 1.5
    
    # Calculate width scaling (more x-labels need more width)
    # Use moderate scaling for readability
    width_scale = 1.0 + (num_x_labels - 3) * 0.10
    width_scale = max(width_scale, 1.0)  # Minimum scale of 1.0
    width_scale = min(width_scale, 2.2)  # Tighter maximum scale
    
    # Calculate height scaling (more series need more height for legend)
    height_scale = 1.0 + (num_series - 2) * 0.1
    height_scale = max(height_scale, 1.0)
    height_scale = min(height_scale, 2.0)
    
    # Adjusted figure size
    final_width = base_width * width_scale
    if max_width:
        final_width = min(final_width, max_width)
        
    figsize = (final_width, base_height * height_scale)
    
    # Font size adjustments
    # Reduce font size for many labels or series
    # print('num_x_labels: ', num_x_labels)
    font_scale = 1.0
    if num_x_labels > 10:
        font_scale *= 0.95
    if num_x_labels > 20:
        font_scale *= 0.95
    if num_series > 5:
        font_scale *= 0.95
    
    font_size = int(base_font * font_scale)
    font_size = max(font_size, 7)  # Minimum readable font size
    
    # Bar width calculation
    # More series means narrower bars
    effective_width_per_group = 0.90  # Total width allocated to bars in each group
    bar_width = effective_width_per_group / max(num_series, 1)
    
    # Adjust bar width based on number of x-labels
    if num_x_labels > 15:
        bar_width *= 0.92  # Narrower for many categories
    
    # Gap factor: spacing between groups - tighter overall
    gap_factor = base_gap
    if num_x_labels > 20:
        gap_factor = 1.0  # Much tighter spacing for many categories
    elif num_x_labels > 10:
        gap_factor = 1.2
    elif num_x_labels < 5:
        gap_factor = 2.0  # More spacing for few categories
    
    # Legend and label font sizes
    legend_fontsize = max(font_size - 1, 6)
    label_fontsize = max(font_size + 1, 8)
    
    # Always show value labels, but adjust size
    show_value_labels = True

    font_size = font_size - 2
    
    print('font_size: ', font_size)
    return {
        'figsize': figsize,
        'font_size': font_size,
        'bar_width': bar_width,
        'gap_factor': gap_factor,
        'legend_fontsize': legend_fontsize,
        'label_fontsize': label_fontsize,
        'legend_ncol': min(3, max(2, num_series // 2)),  # Dynamic legend columns
        'show_value_labels': show_value_labels
    }

# def plot_bars_dynamic(series_list, x_labels, title, xlabel, ylabel, 
#                      output_dir=None, precision=1, show_value_labels=None, log_scale=False,
#                      scientific_labels=False):
#     """
#     Plot N-series grouped bar chart with dynamically adjusted layout.
    
#     Args:
#         series_list: list of dicts with keys: 'label' (str), 'values' (list[float]), 
#                     'color' (str, optional), 'errors' (list[float], optional for error bars)
#         x_labels: list of strings for x-axis categories
#         title: plot title
#         xlabel: x-axis label
#         ylabel: y-axis label
#         output_dir: optional directory to save plot
#         precision: decimal precision for value labels
#         show_value_labels: whether to show values on top of bars (None=auto-detect)
#         log_scale: if True, use log scale for y-axis
#         scientific_labels: if True, format value labels in scientific notation (e.g. 1.02e+04)
#     """
#     if series_list is None or len(series_list) == 0 or x_labels is None:
#         return
    
#     num_series = len(series_list)
#     num_x_labels = len(x_labels)
    
#     # Get dynamic parameters
#     params = calculate_plot_params(num_x_labels, num_series)
    
#     # Use dynamically determined value labels if not explicitly set
#     if show_value_labels is None:
#         show_value_labels = params['show_value_labels']
    
#     # Create figure with dynamic size
#     plt.figure(figsize=params['figsize'])
#     plt.rcParams.update({'font.size': params['font_size']})
    
#     # Calculate x positions
#     x = np.arange(num_x_labels) * params['gap_factor']
    
#     # Default color palette if not specified
#     default_colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', 
#                      '#F0E442', '#D55E00', '#999999', '#FF6600',
#                      '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
#                      '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']
    
#     bars_handles = []
#     series_max_values = []
    
#     for idx, series in enumerate(series_list):
#         offset = (idx - (num_series - 1) / 2) * params['bar_width']
#         color = series.get('color', default_colors[idx % len(default_colors)])
#         label = series.get('label', f"Series {idx+1}")
#         values = series.get('values', [])
#         errors = series.get('errors', None)  # Get error bar data if provided
        
#         # Ensure values match x_labels length
#         if len(values) != num_x_labels:
#             values = (values + [0] * num_x_labels)[:num_x_labels]
        
#         # Ensure errors match if provided
#         if errors is not None and len(errors) != num_x_labels:
#             errors = (errors + [0] * num_x_labels)[:num_x_labels]
        
#         # Create bars with error bars if errors are provided
#         if errors is not None:
#             bars = plt.bar(x + offset, values, params['bar_width'], 
#                           color=color, label=label, edgecolor='black', linewidth=0.5,
#                           yerr=errors, capsize=3, error_kw={'elinewidth': 1, 'capthick': 1})
#         else:
#             bars = plt.bar(x + offset, values, params['bar_width'], 
#                           color=color, label=label, edgecolor='black', linewidth=0.5)
#         bars_handles.append(bars)
        
#         if len(values) > 0:
#             # Account for error bars in max calculation
#             if errors is not None:
#                 series_max_values.append(max([v + e for v, e in zip(values, errors)]))
#             else:
#                 series_max_values.append(max(values))
    
#     # Set labels and title with dynamic font sizes
#     plt.xlabel(xlabel, fontsize=params['label_fontsize'])
#     plt.ylabel(ylabel, fontsize=params['label_fontsize'])
#     plt.title(title, fontsize=params['label_fontsize'] + 2, fontweight='bold')
    
#     # X-axis tick labels with rotation if needed
#     rotation = 0
#     ha = 'center'
#     if num_x_labels > 15:
#         rotation = 45
#         ha = 'right'
#     elif num_x_labels > 8:
#         rotation = 30
#         ha = 'right'
    
#     plt.xticks(x, x_labels, rotation=rotation, ha=ha, 
#               fontsize=params['font_size'])
#     plt.yticks(fontsize=params['font_size'])
    
#     # Grid
#     plt.grid(axis='y', linestyle='--', alpha=0.7)
#     if log_scale:
#         plt.yscale('log')
    
#     # Legend with dynamic positioning
#     plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
#               ncol=params['legend_ncol'], fontsize=params['legend_fontsize'],
#               frameon=True, shadow=True)
    
#     # Add value labels on bars if requested
#     if show_value_labels:
#         ymax = max(series_max_values) if len(series_max_values) > 0 else 1
        
#         # Adjust label font size and rotation for crowded plots
#         if num_x_labels > 25:
#             label_font = params['font_size']
#             label_rotation = 90
#             va_align = 'bottom'
#             y_offset = 0.01 * ymax
#         elif num_x_labels > 15:
#             label_font = params['font_size']
#             label_rotation = 0
#             va_align = 'bottom'
#             y_offset = 0.015 * ymax
#         else:
#             label_font = params['font_size']
#             label_rotation = 0
#             va_align = 'bottom'
#             y_offset = 0.02 * ymax
        
#         for bars in bars_handles:
#             for bar in bars:
#                 height = bar.get_height()
#                 if height > 0:  # Only label non-zero bars
#                     if scientific_labels:
#                         label_text = f"{height:.2e}"
#                     else:
#                         label_text = f"{height:.{precision}f}"
#                     # On log scale use multiplicative offset so label sits above bar
#                     if log_scale:
#                         y_pos = height * 1.08
#                     else:
#                         y_pos = height + y_offset
#                     plt.text(
#                         bar.get_x() + bar.get_width() / 2,
#                         y_pos,
#                         label_text,
#                         ha='center', va=va_align, fontsize=label_font,
#                     )
    
#     # Adjust layout
#     plt.tight_layout(rect=[0, 0, 1, 0.95])
    
#     # Save figure
#     if output_dir:
#         os.makedirs(output_dir, exist_ok=True)
#         file_path = os.path.join(output_dir, f"{title}.png")
#     else:
#         file_path = f"{title}.png"
    
#     plt.savefig(file_path, bbox_inches='tight', dpi=150)
#     print(f'Saved plot to {file_path}')
#     plt.close()

def plot_bars_dynamic(series_list, x_labels, title, xlabel, ylabel, 
                     output_dir=None, precision=1, show_value_labels=None,
                     log_scale=False, scientific_labels=False, max_width=None):
    """
    Plot N-series grouped bar chart with dynamically adjusted layout.
    
    Args:
        series_list: list of dicts with keys: 'label' (str), 'values' (list[float]), 
                    'color' (str, optional), 'errors' (list[float], optional for error bars)
        x_labels: list of strings for x-axis categories
        title: plot title
        xlabel: x-axis label
        ylabel: y-axis label
        output_dir: optional directory to save plot
        precision: decimal precision for value labels
        show_value_labels: whether to show values on top of bars (None=auto-detect)
        log_scale: if True, use log scale for y-axis
        scientific_labels: if True, format value labels in scientific notation
        max_width: optional maximum width for the figure
    """
    if series_list is None or len(series_list) == 0 or x_labels is None:
        return
    
    num_series = len(series_list)
    num_x_labels = len(x_labels)
    
    # Get dynamic parameters
    params = calculate_plot_params(num_x_labels, num_series, max_width=max_width)
    
    # Use dynamically determined value labels if not explicitly set
    if show_value_labels is None:
        show_value_labels = params['show_value_labels']
    
    # Create figure with dynamic size
    plt.figure(figsize=params['figsize'])
    plt.rcParams.update({
        'font.size':        params['font_size'],
        'font.family':      'serif',        # Match LaTeX Computer Modern
        'font.serif':       ['Times New Roman', 'DejaVu Serif', 'serif'],
        'pdf.fonttype':     42,             # Embed TrueType → camera-ready PDF
        'ps.fonttype':      42,
        'axes.grid':        True,
        'axes.axisbelow':   True,           # Grid lines behind bars
        'grid.alpha':       0.35,
        'grid.linestyle':   '--',
        'grid.linewidth':   0.5,
        'axes.linewidth':   0.7,
        'xtick.major.width': 0.6,
        'ytick.major.width': 0.6,
    })
    
    # Calculate x positions
    x = np.arange(num_x_labels) * params['gap_factor']
    
    # Default color palette if not specified
    default_colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', 
                     '#F0E442', '#D55E00', '#999999']
    
    bars_handles = []
    series_max_values = []
    
    for idx, series in enumerate(series_list):
        offset = (idx - (num_series - 1) / 2) * params['bar_width']
        color = series.get('color', default_colors[idx % len(default_colors)])
        label = series.get('label', f"Series {idx+1}")
        values = series.get('values', [])
        errors = series.get('errors', None)  # Get error bar data if provided
        
        # Ensure values match x_labels length
        if len(values) != num_x_labels:
            values = (values + [0] * num_x_labels)[:num_x_labels]
        
        # Ensure errors match if provided
        if errors is not None and len(errors) != num_x_labels:
            errors = (errors + [0] * num_x_labels)[:num_x_labels]
        
        # Create bars with error bars if errors are provided
        if errors is not None:
            bars = plt.bar(x + offset, values, params['bar_width'], 
                          color=color, alpha=0.88,
                          label=label, edgecolor='black', linewidth=0.5,
                          yerr=errors, capsize=2,
                          error_kw={'elinewidth': 0.8, 'capthick': 0.8, 'ecolor': '#333333'})
            # bars = plt.bar(x + offset, values, params['bar_width'], 
            #               color=color, label=label, edgecolor='black', linewidth=0.5,
            #               yerr=errors, capsize=3, error_kw={'elinewidth': 1, 'capthick': 1})
        else:
            bars = plt.bar(x + offset, values, params['bar_width'], 
                          color=color, alpha=0.88, label=label, edgecolor='black', linewidth=0.5)
        bars_handles.append(bars)
        
        if len(values) > 0:
            # Account for error bars in max calculation
            if errors is not None:
                series_max_values.append(max([v + e for v, e in zip(values, errors)]))
            else:
                series_max_values.append(max(values))
    

   
    # Set labels and title with dynamic font sizes
    plt.xlabel(xlabel, fontsize=params['label_fontsize'])
    plt.ylabel(ylabel, fontsize=params['label_fontsize'])
    # plt.title(title, fontsize=params['label_fontsize'] + 2, fontweight='bold')
    
    # X-axis tick labels with rotation if needed
    rotation = 0
    ha = 'center'
    if num_x_labels > 15:
        rotation = 45
        ha = 'right'
    elif num_x_labels > 8:
        rotation = 30
        ha = 'right'
    
    plt.xticks(x, x_labels, rotation=rotation, ha=ha, 
              fontsize=params['font_size'])
    plt.yticks(fontsize=params['font_size'])
    
    # Grid
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    if log_scale:
        plt.yscale('log')
    
    # Legend with dynamic positioning
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
    #           ncol=params['legend_ncol'], fontsize=params['legend_fontsize'],
    #           frameon=True, shadow=True)
    plt.legend(loc='upper center',
              bbox_to_anchor=(0.5, 1.22),
              ncol=min(num_series, 3),
              fontsize=params['legend_fontsize'],
              frameon=True,
              framealpha=0.85,
              edgecolor='#cccccc',
              borderpad=0.4,
              labelspacing=0.25,
              handlelength=1.4,
              handletextpad=0.4,
              columnspacing=1.0)


    # Add value labels on bars if requested
    if show_value_labels:
        ymax = max(series_max_values) if len(series_max_values) > 0 else 1
        ymax = max(ymax, 1e-6)
        if not log_scale:
            plt.ylim(0, ymax * 1.10)
        
        # Adjust label font size and rotation for crowded plots
        if num_x_labels > 25:
            label_font = params['font_size']
            label_rotation = 90
            va_align = 'bottom'
            y_offset = 0.0075 * ymax
        elif num_x_labels > 15:
            label_font = params['font_size']
            label_rotation = 0
            va_align = 'bottom'
            y_offset = 0.010 * ymax
        else:
            label_font = params['font_size']
            label_rotation = 0
            va_align = 'bottom'
            y_offset = 0.015 * ymax
        
        for bars in bars_handles:
            for bar in bars:
                height = bar.get_height()
                if height > 0:  # Only label non-zero bars
                    if scientific_labels:
                        label_text = f"{height:.1e}"
                    else:
                        label_text = f"{height:.{precision}f}"
                    
                    if log_scale:
                        y_pos = height * 1.15
                    else:
                        y_pos = height + y_offset

                    plt.text(
                        bar.get_x() + bar.get_width() / 2,
                        y_pos,
                        label_text,
                        ha='center', va=va_align, fontsize=label_font,
                    )
    
    # Adjust layout
    plt.tight_layout(pad=0.4)
    
    # Save figure
    file_name = f"{title.replace(' ', '_').lower()}.pdf"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, file_name)
    else:
        file_path = file_name
    
    plt.savefig(file_path, bbox_inches='tight',format='pdf')
    print(f'Saved plot to {file_path}')
    plt.close()

def parse_results(path):
    results = np.genfromtxt(path, dtype=float, delimiter=',', names=True)
    return results

def get_iperf_tput_from_log(log_path):
    """Read iperf.bw.log and return aggregate tput (Gbps) for 30-60s interval.

    Replicates: grep "60.*-90.*" iperf.bw.log | awk '{ sum += $7; n++ } END { if (n > 0) printf "%.3f", sum/1000 }'
    """
    if not os.path.exists(log_path):
        return None
    print(f"Reading iperf logs from {log_path}")
    total = 0.0
    n = 0
    with open(log_path) as f:
        for line in f:
            if "60." not in line or "-90." not in line:
                continue
            fields = line.split()
            if len(fields) < 7:
                continue
            try:
                total += float(fields[6])
                n += 1
            except ValueError:
                continue
    if n == 0:
        return None
    return total / 1000.0


def get_tput_from_iperf_logs(exp_path):
    """Compute net_tput mean/stddev across runs from iperf.bw.log files.

    Converts a reports path to the corresponding logs path, iterates over
    RUN-N directories, and averages the per-run 30-60s throughput.
    """
    log_base = exp_path.rstrip('/').replace('/reports/', '/logs/')

    tputs = []
    for run_id in range(20):
        log_file = os.path.join(f"{log_base}-RUN-{run_id}", "iperf.bw.log")
        tput = get_iperf_tput_from_log(log_file)
        if tput is not None:
            tputs.append(tput)

    if not tputs:
        return None, None
    # print
    return float(np.mean(tputs)), float(np.std(tputs))


def get_data(x_labels, exps, collect_ebpf=True):
    files = [
        os.path.join(exp, "tput_metrics.dat") for exp in exps
    ]

    data = [
        parse_results(f) for f in files
    ]

    # for i, exp in enumerate(exps):
    #     mean_tput, std_tput = get_tput_from_iperf_logs(exp)
    #     if mean_tput is not None:
    #         data[i]['net_tput_mean'] = mean_tput
    #         data[i]['net_tput_stddev'] = std_tput
    #         print(f"  iperf logs found for {os.path.basename(exp.rstrip('/'))}")
    #         print(f"  Recalculated net_tput from iperf logs: {mean_tput:.3f} Gbps (stddev {std_tput:.3f})")
    #     else:
    #         print(f"No iperf logs found for {os.path.basename(exp.rstrip('/'))}, using tput_metrics.dat value")

    # tput = [d['net_tput_mean'] for d in data]
    if collect_ebpf:
        ebpf_data = get_ebpf_stats(exps)
    else:
        ebpf_data = None     
    # ebpf_data = None
    return data, ebpf_data

def __get_ebpf_stats_from_csv(ebpf_path):
    if not os.path.exists(ebpf_path):
        return None
    # print(f"Reading eBPF stats from {ebpf_path}")

    with open(ebpf_path, 'r') as f:
        lines = f.readlines()

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("# Per-Function Latency Statistics"):
            start_idx = i + 1
        if line.strip().startswith("# Per-Function Per-CPU Counts"):
            end_idx = i
            break

    if start_idx is None or end_idx is None or end_idx <= start_idx:
        return None

    # The first line after start_idx is the header
    header = lines[start_idx].strip()
    data_lines = [l.strip() for l in lines[start_idx+1:end_idx] if l.strip() and not l.strip().startswith("#")]

    from io import StringIO
    csv_content = header + "\n" + "\n".join(data_lines)
    ebpf_results = pd.read_csv(StringIO(csv_content))

    # print(ebpf_results.to_string())
    # ebpf_results = pd.read_csv(ebpf_path)
    # # only show aggragete results
    # ebpf_results = ebpf_results[ebpf_results['core'] == -1]

    # return {key: ebpf_results[key] for key in ebpf_results.dtype.names}
    return ebpf_results


def get_ebpf_stats_from_csv(path, tput, profile_duration=20):
    run_stats = __get_ebpf_stats_from_csv(path)
    if run_stats is None:
        return None
    total_data = tput * 1e9 / 8 * profile_duration  # bytes
    total_pages = total_data / 4096
    run_stats['count_per_page'] = run_stats['count'] / total_pages
    run_stats = run_stats.reset_index(drop=True)
    
    return run_stats

# def get_ebpf_single_run(exp_name, run_id, tput):
#     """Get eBPF stats for a single run."""
#     file = exp_name + "-RUN-" + str(run_id) + "/ebpf_guest_stats.csv"
#     if not os.path.exists(file):
#         print(f"File {file} does not exist")
#         return None
#     return get_ebpf_stats_from_csv(file, tput)

# def get_ebpf_stats(exps, tput):
#     """Get eBPF stats averaged across multiple runs for each experiment."""
#     n_runs = 1
#     ebpf_aggregated_data = []
    
#     for idx, exp in enumerate(exps):
#         ebpf_data_per_exp = []
        
#         # Collect data from all runs
#         for run_id in range(n_runs):
#             ebpf_data = get_ebpf_single_run(exp, run_id, tput[idx])
#             if ebpf_data is None:
#                 print(f"Failed to get eBPF data for {exp} run {run_id}")
#                 continue
#             ebpf_data_per_exp.append(ebpf_data)
        
#         if len(ebpf_data_per_exp) == 0:
#             print(f"No eBPF data found for experiment {exp}")
#             ebpf_aggregated_data.append(None)
#             continue
        
#         # Calculate mean and stddev across runs for each function
#         # Group by function name and calculate statistics
#         all_functions = ebpf_data_per_exp[0]['function'].unique()
        
#         aggregated_df = pd.DataFrame()
#         for func_name in all_functions:
#             func_data_across_runs = []
#             for run_df in ebpf_data_per_exp:
#                 func_row = run_df[run_df['function'] == func_name]
#                 if not func_row.empty:
#                     func_data_across_runs.append(func_row.iloc[0])
            
#             if len(func_data_across_runs) > 0:
#                 # Convert to DataFrame for easier computation
#                 func_df = pd.DataFrame(func_data_across_runs)
                
#                 # Create aggregated row with mean values
#                 agg_row = {}
#                 agg_row['function'] = func_name
                
#                 # For numeric columns, calculate mean
#                 numeric_cols = func_df.select_dtypes(include=[np.number]).columns
#                 for col in numeric_cols:
#                     agg_row[col] = func_df[col].mean()
#                     # Also store stddev with _stddev suffix for future use
#                     agg_row[f'{col}_stddev'] = func_df[col].std()
                
#                 aggregated_df = pd.concat([aggregated_df, pd.DataFrame([agg_row])], ignore_index=True)
        
#         # Save for debugging/inspection
#         output_file = f"ebpf_aggregated_{exp.split('/')[-1]}.csv"
#         aggregated_df.to_csv(output_file, index=False)
#         print(f"Saved aggregated eBPF data to {output_file}")
        
#         ebpf_aggregated_data.append(aggregated_df)
    
#     return ebpf_aggregated_data

def get_tput_from_dat(exp_name, run_id):
    exp_name = exp_name.rstrip('/')
    file = os.path.join(exp_name + "-RUN-" + str(run_id), "iperf.bw.rpt")
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

def get_ebpf_single_run(exp_name, run_id):
    """Get eBPF stats for a single run."""
    exp_name = exp_name.rstrip('/')
    file = os.path.join(exp_name + "-RUN-" + str(run_id), "ebpf_guest_stats.csv")
    if not os.path.exists(file):
        # print(f"File {file} does not exist")
        return None
    tput = get_tput_from_dat(exp_name, run_id)
    if tput is None:
        return None
    print(f"Reading eBPF stats from {file} tput: {tput}")
    return get_ebpf_stats_from_csv(file, tput)

def get_ebpf_stats(exps):
    """Get eBPF stats averaged across multiple runs for each experiment."""
    MAX_RUN = 20
    ebpf_aggregated_data = []
    
    for idx, exp in enumerate(exps):
        ebpf_data_per_exp = []
        
        # Collect data from all runs
        for run_id in range(MAX_RUN):
            # ebpf_data = get_ebpf_single_run(exp, run_id, tput[idx])
            ebpf_data = get_ebpf_single_run(exp, run_id)
            if ebpf_data is None:
                continue
            ebpf_data_per_exp.append(ebpf_data)
        
        if len(ebpf_data_per_exp) == 0:
            print(f"No eBPF data found for experiment {exp}")
            ebpf_aggregated_data.append(None)
            continue
        
        # Calculate mean and stddev across runs for each function
        # Group by function name and calculate statistics
        all_functions = pd.unique(
            pd.concat([df['function'] for df in ebpf_data_per_exp if df is not None], ignore_index=True)
        )
        
        aggregated_df = pd.DataFrame()
        for func_name in all_functions:
            func_data_across_runs = []
            for run_df in ebpf_data_per_exp:
                func_row = run_df[run_df['function'] == func_name]
                if not func_row.empty:
                    func_data_across_runs.append(func_row.iloc[0])
            
            if len(func_data_across_runs) > 0:
                # Convert to DataFrame for easier computation
                func_df = pd.DataFrame(func_data_across_runs)
                
                # Create aggregated row with mean values
                agg_row = {}
                agg_row['function'] = func_name
                
                # For numeric columns, calculate mean
                numeric_cols = func_df.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    agg_row[col] = func_df[col].mean()
                    # Also store stddev with _stddev suffix for future use
                    agg_row[f'{col}_stddev'] = func_df[col].std()
                
                aggregated_df = pd.concat([aggregated_df, pd.DataFrame([agg_row])], ignore_index=True)
        
        # Save for debugging/inspection
        exp = exp.rstrip('/')
        output_file = f"csvs/ebpf_aggregated_{exp.split('/')[-1]}.csv"
        aggregated_df.to_csv(output_file, index=False)
        print(f"Saved aggregated eBPF data to {output_file}")
        
        ebpf_aggregated_data.append(aggregated_df)
    
    return ebpf_aggregated_data

def get_data_ring(prefix, iommu_str, suffix=""):

    x_labels =  ["0256", "0512", "1024", "2048"]
    folders = [
        prefix + iommu_str + "-ring_buffer-"+ x for x in x_labels
    ]

    files = [
        "../utils/reports/" + f + "/tput_metrics.dat" for f in folders
    ]

    data = [
        parse_results(f) for f in files
    ]
    
    return data

def misses_per_page(misses, tput_mean):
    # a bit of a round-a-bout way from when I used per desc, but it works so not touching it!
    mbs_per_second = tput_mean * 125
    descriptors_per_second = mbs_per_second * 4
    misses_per_page = misses / descriptors_per_second
    # GETTING MISSES PER PAGE
    misses_per_page = misses_per_page / 64
    return misses_per_page

def plot_ebpf_selected_functions(datasets, x_labels, selected_functions, title_key, xlabel="Experiments", output_dir=None):
    """Plot selected eBPF functions' metrics across experiments for multiple setups.

    datasets: list of dicts with keys: 'setup_name' (str), 'ebpf' (list[pd.DataFrame]), 'color' (str)
    selected_functions: dict mapping functionality name to list of function names, or list for backward compatibility
                       e.g., {"cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"]}
    xlabel: x-axis label for the plots
    """
    if datasets is None or len(datasets) == 0:
        return

    datasets = [ds for ds in datasets if ds.get('ebpf') is not None]
    if len(datasets) == 0:
        return

    num_experiments = len(x_labels) if x_labels is not None else 0
    for ds in datasets:
        ebpf_list = ds.get('ebpf', [])
        if len(ebpf_list) != num_experiments:
            print(f"eBPF data length mismatch for {ds.get('setup_name', 'unknown')}; skipping eBPF plots")
            return

    # Convert list format to dict format for backward compatibility
    if isinstance(selected_functions, list):
        selected_functions = {func: [func] for func in selected_functions}

    def extract_metric_series(ebpf_data_list, function_names, column_name):
        """Extract values for a specific metric column, trying multiple function names."""
        series_values = []
        for df in ebpf_data_list:
            if df is None or 'function' not in df.columns:
                series_values.append(0)
                continue
            
            # Try each function name in the list
            value_found = False
            for function_name in function_names:
                row = df[df['function'] == function_name]
                if not row.empty and column_name in row.columns:
                    value = row.iloc[0][column_name]
                    try:
                        series_values.append(float(value))
                        value_found = True
                        break
                    except Exception:
                        continue
            
            if not value_found:
                series_values.append(0)
        
        return series_values
    
    def extract_metric_with_stddev(ebpf_data_list, function_names, column_name):
        """Extract both values and stddev for a specific metric."""
        values = extract_metric_series(ebpf_data_list, function_names, column_name)
        stddev_col = f'{column_name}_stddev'
        errors = extract_metric_series(ebpf_data_list, function_names, stddev_col)
        return values, errors

    def sanitize(name):
        return str(name).replace('/', '_').replace(' ', '_')

    for functionality_name, function_names in selected_functions.items():
        # Count
        series_list = []
        for ds in datasets:
            values, errors = extract_metric_with_stddev(ds['ebpf'], function_names, 'count')
            series_list.append({
                'label': ds['setup_name'],
                'values': values,
                'errors': errors,
                'color': ds.get('color')
            })
        plot_bars_dynamic(series_list, x_labels,
                        title=f"{title_key}-{sanitize(functionality_name)}-count",
                        xlabel=xlabel,
                        ylabel="Count",
                        output_dir=output_dir,
                        precision=1)

        # Mean (ns)
        series_list = []
        for ds in datasets:
            values, errors = extract_metric_with_stddev(ds['ebpf'], function_names, 'mean_ns')
            series_list.append({
                'label': ds['setup_name'],
                'values': values,
                'errors': errors,
                'color': ds.get('color')
            })
        plot_bars_dynamic(series_list, x_labels,
                        title=f"{title_key}-{sanitize(functionality_name)}-mean_ns",
                        xlabel=xlabel,
                        ylabel="Mean (ns)",
                        output_dir=output_dir,
                        precision=1,
                        log_scale=True,
                        scientific_labels=True)

        # Total time (count * mean_ns)
        series_list = []
        for ds in datasets:
            counts = extract_metric_series(ds['ebpf'], function_names, 'count')
            means = extract_metric_series(ds['ebpf'], function_names, 'mean_ns')
            total_ns = [c * m for c, m in zip(counts, means)]
            total_ms = [t / 1e6 for t in total_ns]
            series_list.append({
                'label': ds['setup_name'],
                'values': total_ms,
                'color': ds.get('color')
            })
        plot_bars_dynamic(series_list, x_labels,
                        title=f"{title_key}-{sanitize(functionality_name)}-total_time",
                        xlabel=xlabel,
                        ylabel="Total time (ms)",
                        output_dir=output_dir,
                        precision=1,
                        log_scale=True,
                        scientific_labels=True)

        # Count per page
        series_list = []
        for ds in datasets:
            values, errors = extract_metric_with_stddev(ds['ebpf'], function_names, 'count_per_page')
            series_list.append({
                'label': ds['setup_name'],
                'values': values,
                'errors': errors,
                'color': ds.get('color')
            })
        plot_bars_dynamic(series_list, x_labels,
                        title=f"{title_key}-{sanitize(functionality_name)}-count_per_page",
                        xlabel=xlabel,
                        ylabel="Count per page",
                        output_dir=output_dir,
                        precision=4)

def plot_all_subplots(datasets, x_labels, title_key, xlabel, output_dir=None):
    """Plot throughput, CPU util, drop-rate for multiple setups.

    datasets: list of dicts with keys: 'setup_name' (str), 'data' (list[ndarray]), 'color' (str)
    """
    if datasets is None or len(datasets) == 0:
        return

    # Throughput
    series_list = []
    for ds in datasets:
        series_list.append({
            'label': ds['setup_name'],
            'values': [ r['net_tput_mean'] for r in ds['data'] ],
            'errors': [ r['net_tput_stddev'] for r in ds['data'] ],
            'color': ds.get('color')
        })
    plot_bars_dynamic(series_list, x_labels,
                    title=title_key + '-tput',
                    xlabel=xlabel,
                    ylabel="Throughput (Gbps)",
                    output_dir=output_dir,
                    precision=1)

    # CPU Utilization
    series_list = []
    for ds in datasets:
        series_list.append({
            'label': ds['setup_name'],
            'values': [ r['cpu_utils_mean'] for r in ds['data'] ],
            'errors': [ r['cpu_utils_stddev'] for r in ds['data'] ],
            'color': ds.get('color')
        })
    plot_bars_dynamic(series_list, x_labels,
                    title=title_key + '-cpu-util',
                    xlabel=xlabel,
                    ylabel="% CPU Utilization",
                    output_dir=output_dir,
                    precision=1)

    # Drop rate
    series_list = []
    for ds in datasets:
        series_list.append({
            'label': ds['setup_name'],
            'values': [ r['retx_rate_mean'] for r in ds['data'] ],
            'errors': [ r['retx_rate_stddev'] for r in ds['data'] ],
            'color': ds.get('color')
        })
    plot_bars_dynamic(series_list, x_labels,
                    title=title_key + '-drop-rate',
                    xlabel=xlabel,
                    ylabel="Drop rate",
                    output_dir=output_dir,
                    precision=3)

def plot_flows_exp():
    
    target_values = [1, 4, 8, 12, 16, 20, 24]
    # x_labels = [f"{i:02d}" for i in range(1, 33)]
    x_labels = [f"{i:02d}" for i in target_values]
    print(x_labels)


    off_exps = [
        f"/home/schai/viommu/utils/reports/2025-11-16-04-13-32-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-off-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]

    nested_exps_extra_hook = [
        f"../utils/reports/2025-11-17-22-20-09-6.12.9-iommufd-extra-hooks-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]

    # nested_exps = [
    #     f"../utils/reports/2025-11-15-17-53-09-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    # ]

    # siyuan_no_map_contention = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2025-11-27-22-47-54-6.12.9-iommufd-vanilla-based-no-map-contention-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]

    # siyuan_no_map_contention = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2025-12-05-04-01-47-6.12.9-iommufd-vanilla-based-no-map-contention-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]

    # siyuan_exp_one_core_invalid = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2025-12-05-02-15-06-6.12.9-iommufd-vanilla-based-no-map-contention-one-core-invalid-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]

    # siyuan_exp_async_invalid_wait = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2025-12-05-00-27-51-6.12.9-iommufd-vanilla-based-no-map-contention-AsyncInvalid-wait-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]

    # siyuan_exp_one_core_invalid = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2025-11-28-00-44-21-6.12.9-iommufd-vanilla-based-no-map-contention-one-core-invalid-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]
    

    shadow_exps = [
        f"../utils/reports/2025-11-16-16-40-49-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-shadow-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]
    
    # host_strict_guest_nested_siyuan_no_map_contention, extra_hooks_siyuan_no_map_contention_ebpf = get_data(x_labels, siyuan_no_map_contention)
    # host_strict_guest_nested_siyuan_one_core_invalid, extra_hooks_siyuan_one_core_invalid_ebpf = get_data(x_labels, siyuan_exp_one_core_invalid)
    host_strict_guest_nested_exta_hooks_data, extra_hooks_ebpf = get_data(x_labels, nested_exps)
    # host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    host_strict_guest_shadow_data, host_strict_guest_shadow_ebpf_data = get_data(x_labels, shadow_exps)

    # datasets = [
    #     { 'setup_name': 'Host Strict; Guest Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': '#0072B2' },
    #     { 'setup_name': 'Host Strict; Guest Nested', 'data': host_strict_guest_nested_exta_hooks_data, 'ebpf': extra_hooks_ebpf, 'color': '#009E73' },
    #     { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': '#FF6600' },
    #     # { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Async Invalid', 'data': host_strict_guest_nested_siyuan_one_core_invalid, 'ebpf': extra_hooks_siyuan_one_core_invalid_ebpf, 'color': '#CC79A7' },
    #     { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Combining', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': '#F0E442' },
    # ]

    datasets = [
        { 'setup_name': 'Host Strict; Guest Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': '#0072B2' },
        { 'setup_name': 'Host Strict; Guest Shadow', 'data': host_strict_guest_shadow_data, 'ebpf': host_strict_guest_shadow_ebpf_data, 'color': '#CC79A7' },
        { 'setup_name': 'Host Strict; Guest Nested', 'data': host_strict_guest_nested_exta_hooks_data, 'ebpf': extra_hooks_ebpf, 'color': '#009E73' },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': '#FF6600' },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Combining', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': '#F0E442' },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Off_vs_Shadow_leshna")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                 },
                                 title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
                                 xlabel="Number of Cores (1 flow/core)",
                                 output_dir="Off_vs_Shadow_leshna")

    # datasets = [
    #     { 'setup_name': 'Host Strict; Guest Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': '#0072B2' },
    #     { 'setup_name': 'Host Strict; Guest Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': '#009E73' },
    #     { 'setup_name': 'No Map Contention', 'data': no_contention_data, 'ebpf': no_contention_ebpf_data, 'color': '#CC79A7' },
    # ]

    # plot_all_subplots(datasets=datasets,
    #                   x_labels=x_labels,
    #                   title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
    #                   xlabel="Number of Cores (1 flow/core)",
    #                   output_dir="Nested_vs_Off_1_20_cores_no_contention")

    # plot_ebpf_selected_functions(datasets=datasets,
    #                              x_labels=x_labels,
    #                              selected_functions=["cache_tag_flush_range_np", "cache_tag_flush_range", "qi_submit_sync", "trace_qi_submit_sync_cs",],
    #                              title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
    #                              output_dir="Nested_vs_Off_1_20_cores_no_contention")

def siyuan_flows_exp_motivation():
    
    target_values = [1, 4, 8, 12, 16, 20, 24]
    # x_labels = [f"{i:02d}" for i in range(1, 33)]
    x_labels = [f"{i:02d}" for i in target_values]
    print(x_labels)


    off_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-02-10-38-6.12.9-iommufd-flow{i:02d}-host-strict-guest-off-off-{i}cores-ringbuf512-sockbuf1" for i in target_values
    ]

    nested_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-24-15-08-11-6.12.9-iommufd-RX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
    ]
    # nested_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-04-24-41-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1"  for i in target_values
    # ]

    # shadow_exps = [
    #     f"../utils/reports/2025-11-16-16-40-49-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-shadow-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    # ]
    
    # host_strict_guest_nested_siyuan_no_map_contention, extra_hooks_siyuan_no_map_contention_ebpf = get_data(x_labels, siyuan_no_map_contention)
    # host_strict_guest_nested_siyuan_one_core_invalid, extra_hooks_siyuan_one_core_invalid_ebpf = get_data(x_labels, siyuan_exp_one_core_invalid)
    host_strict_guest_nested_exta_hooks_data, extra_hooks_ebpf = get_data(x_labels, nested_exps)
    # host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    # host_strict_guest_shadow_data, host_strict_guest_shadow_ebpf_data = get_data(x_labels, shadow_exps)

    # datasets = [
    #     { 'setup_name': 'Host Strict; Guest Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': '#0072B2' },
    #     { 'setup_name': 'Host Strict; Guest Nested', 'data': host_strict_guest_nested_exta_hooks_data, 'ebpf': extra_hooks_ebpf, 'color': '#009E73' },
    #     { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': '#FF6600' },
    #     # { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Async Invalid', 'data': host_strict_guest_nested_siyuan_one_core_invalid, 'ebpf': extra_hooks_siyuan_one_core_invalid_ebpf, 'color': '#CC79A7' },
    #     { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Combining', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': '#F0E442' },
    # ]

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': '#0072B2' },
        # { 'setup_name': 'Host Strict; Guest Shadow', 'data': host_strict_guest_shadow_data, 'ebpf': host_strict_guest_shadow_ebpf_data, 'color': '#CC79A7' },
        { 'setup_name': 'vIOMMU on (nested)', 'data': host_strict_guest_nested_exta_hooks_data, 'ebpf': extra_hooks_ebpf, 'color': '#009E73' },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': '#FF6600' },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Combining', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': '#F0E442' },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='motivation_Rx',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Motivation_Rx")
    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                 },
                                 title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
                                 xlabel="Number of Cores (1 flow/core)",
                                 output_dir="Motivation_Rx")


def plot_motivation_Tx():        
    tx_target_values = [4, 8, 12, 16, 20, 24]
    x_labels = [f"{i:02d}" for i in [1, 4, 8, 12, 16, 20, 24]]
    tx_off_exps =[
        "/home/schai/viommu_siyuan/utils/reports/2026-03-28-17-40-35-6.12.9-iommufd-TX-flow01-host-strict-guest-off-off-1cores-ringbuf512-sockbuf1"] + [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-20-01-16-54-server-iommufd-off-6.12.9-iommufd-TX-flow{i:02d}-host-strict-guest-off-off-{i}cores-ringbuf512-sockbuf1" for i in tx_target_values
    ]

    tx_nested_exps = [
        "/home/schai/viommu_siyuan/utils/reports/2026-03-28-17-52-21-6.12.9-iommufd-TX-flow01-host-strict-guest-strict-nested-1cores-ringbuf512-sockbuf1",
    ] + [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-20-03-13-17-server-iommufd-nested-6.12.9-iommufd-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in tx_target_values
    ]

    tx_host_strict_guest_nested_exta_hooks_data, tx_extra_hooks_ebpf = get_data(x_labels, tx_nested_exps)
    # host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    tx_host_strict_guest_off_data, tx_host_strict_guest_off_ebpf_data = get_data(x_labels, tx_off_exps)


    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': tx_host_strict_guest_off_data, 'ebpf': tx_host_strict_guest_off_ebpf_data, 'color': '#0072B2' },
        { 'setup_name': 'vIOMMU on (nested)', 'data': tx_host_strict_guest_nested_exta_hooks_data, 'ebpf': tx_extra_hooks_ebpf, 'color': '#009E73' },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='motivation_Tx_varying_cores',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Motivation_Tx")

    # plot_ebpf_selected_functions(datasets=datasets,
    #                              x_labels=x_labels,
    #                              selected_functions={
    #                                  "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
    #                                  "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
    #                                  "qi_submit_sync": ["qi_submit_sync"],
    #                              },
    #                              title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
    #                              xlabel="Number of Cores (1 flow/core)",
    #                              output_dir="Off_vs_Shadow_leshna")

def siyuan_Evaluation_plot_flows_exp():
    
    target_values = [4, 8, 12, 16, 20, 24]
    # x_labels = [f"{i:02d}" for i in range(1, 33)]
    x_labels = [f"{i:02d}" for i in target_values]
    print(x_labels)

    # off_exps = [
    #     f"/home/schai/viommu/utils/reports/2025-11-16-04-13-32-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-off-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    # ]
    off_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-02-10-38-6.12.9-iommufd-flow{i:02d}-host-strict-guest-off-off-{i}cores-ringbuf512-sockbuf1" for i in target_values
    ]

    # nested_exps = [
    #     f"/home/schai/viommu/utils/reports/2025-11-15-17-53-09-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    # ]
    nested_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-04-24-41-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1"  for i in target_values
    ]


    siyuan_no_map_contention = [
        f"/home/schai/viommu_siyuan/utils/reports/2025-12-05-04-01-47-6.12.9-iommufd-vanilla-based-no-map-contention-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]

    
    siyuan_exp_async_invalid_wait = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-02-03-05-05-6.12.9-iommufd-vanilla-based-no-map-contention-AsyncInvalid-wait-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]

    """ NOTE: these exps may not run with client 6.12.9 """
    z_val_1 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    z_val_10 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    ]

    z_val_100 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    # z_val_1_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    # ]

    # z_val_10_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    # ]

    # z_val_100_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in target_values
    # ]

    z_val_1_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-06-39-57-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval1" for i in target_values
    ]

    z_val_10_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-06-39-57-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval10" for i in target_values
    ]

    z_val_100_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-06-39-57-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval100" for i in target_values
    ]


    z_val_3_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [4, 8, 12]
    ] + ["/home/schai/viommu_siyuan/utils/reports/2026-02-22-16-37-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow16-host-strict-guest-strict-nested-16cores"] + [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [20, 24]
    ]


    # archived data before deadlock bug fixed
    # z_val_1= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval1"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [20,24]
    # ]

    # z_val_10= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval10"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [20,24]
    # ]

    # z_val_100= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval100"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [20,24]
    # ]


    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    host_strict_guest_nested_data, host_strict_guest_nested_ebpf_data = get_data(x_labels, nested_exps)
    
    host_strict_guest_nested_siyuan_no_map_contention, extra_hooks_siyuan_no_map_contention_ebpf = get_data(x_labels, siyuan_no_map_contention)
    host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    
    # z_val_1_data, z_val_1_ebpf_data = get_data(x_labels, z_val_1)
    # z_val_10_data, z_val_10_ebpf_data = get_data(x_labels, z_val_10)
    # z_val_100_data, z_val_100_ebpf_data = get_data(x_labels, z_val_100)

    z_val_1_DFP_data, z_val_1_DFP_ebpf_data = get_data(x_labels, z_val_1_DFP)
    # z_val_10_DFP_data, z_val_10_DFP_ebpf_data = get_data(x_labels, z_val_10_DFP)
    # z_val_100_DFP_data, z_val_100_DFP_ebpf_data = get_data(x_labels, z_val_100_DFP)

    # z_val_3_DFP_data, z_val_3_DFP_ebpf_data = get_data(x_labels, z_val_3_DFP)
    # host_strict_guest_shadow_data, host_strict_guest_shadow_ebpf_data = get_data(x_labels, shadow_exps)

    # Default color palette if not specified
    # default_colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', 
    #                  '#F0E442', '#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']


    # default_colors = ['#0072B2', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00','#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
        { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': color_nested },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': default_colors[8] },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Async Invalid Wait', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': default_colors[5] },
        # { 'setup_name': 'Host Strict; Guest DLF z=1', 'data': z_val_1_data, 'ebpf': z_val_1_ebpf_data, 'color': default_colors[1] },
        # { 'setup_name': 'Host Strict; Guest DLF z=10', 'data': z_val_10_data, 'ebpf': z_val_10_ebpf_data, 'color': default_colors[3] },
        # { 'setup_name': 'Host Strict; Guest DLF z=100', 'data': z_val_100_data, 'ebpf': z_val_100_ebpf_data, 'color': default_colors[4] },

        { 'setup_name': 'vIOMMU Nested + vF&S', 'data': z_val_1_DFP_data, 'ebpf': z_val_1_DFP_ebpf_data, 'color': color_optimization },
        # { 'setup_name': 'Host Strict; Guest DLF z=10 (DFP)', 'data': z_val_10_DFP_data, 'ebpf': z_val_10_DFP_ebpf_data, 'color': default_colors[7] },
        # { 'setup_name': 'Host Strict; Guest DLF z=100 (DFP)', 'data': z_val_100_DFP_data, 'ebpf': z_val_100_DFP_ebpf_data, 'color': default_colors[8] },

        # { 'setup_name': 'Host Strict; Guest DLF z=3 (DFP)', 'data': z_val_3_DFP_data, 'ebpf': z_val_3_DFP_ebpf_data, 'color': default_colors[9] },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='eval_core_exp',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Siyuan_Evaluation_diff_cores")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                     "__iommu_dma_unmap": ["__iommu_dma_unmap_call", "__iommu_dma_unmap"],
                                 },
                                 xlabel="Number of Cores (1 flow/core)",
                                 title_key='eval_core_exp',
                                 output_dir="Siyuan_Evaluation_diff_cores")

def plot_flows_exp_stress():
    
    target_values = [1, 2, 4, 8]
    # x_labels = [f"{i:02d}" for i in range(1, 33)]
    x_labels = [f"{i:02d}" for i in target_values]

    n_cores = 24
    print(x_labels)

    off_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-03-42-26-6.12.9-iommufd-flow{i * n_cores}-host-strict-guest-off-off-{n_cores}cores-ringbuf512-sockbuf1/" for i in target_values
    ]

    nested_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-18-54-39-6.12.9-iommufd-flow{i * n_cores}-host-strict-guest-strict-nested-{n_cores}cores-ringbuf512-sockbuf1/" for i in target_values
    ]

    # nested_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-05-57-59-6.12.9-iommufd-flow{i * n_cores}-host-strict-guest-strict-nested-{n_cores}cores-ringbuf512-sockbuf1/" for i in target_values
    # ]

    # off_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-01-04-03-44-33-6.12.9-iommufd-flow{i * n_cores}-host-strict-guest-off-off-{n_cores}cores" for i in target_values
    # ]

    # nested_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-01-04-04-44-58-6.12.9-iommufd-flow{i * n_cores}-host-strict-guest-strict-nested-{n_cores}cores" for i in target_values
    # ]

    siyuan_exp_async_invalid_wait = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-02-03-57-04-6.12.9-iommufd-vanilla-based-no-map-contention-AsyncInvalid-wait-flow{i * n_cores}-host-strict-guest-strict-nested-{n_cores}cores" for i in target_values
    ]


    z_val_1_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-11-12-29-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i * n_cores}-host-strict-guest-strict-nested-{n_cores}cores-ringbuf512-sockbuf1-zval1/" for i in target_values
    ]

    z_val_10_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-11-12-29-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i * n_cores}-host-strict-guest-strict-nested-{n_cores}cores-ringbuf512-sockbuf1-zval1/" for i in target_values
    ]

    z_val_100_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-01-11-12-29-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i * n_cores}-host-strict-guest-strict-nested-{n_cores}cores-ringbuf512-sockbuf1-zval1/" for i in target_values
    ]
    
    # host_strict_guest_nested_siyuan_no_map_contention, extra_hooks_siyuan_no_map_contention_ebpf = get_data(x_labels, siyuan_no_map_contention)
    # host_strict_guest_nested_siyuan_one_core_invalid, extra_hooks_siyuan_one_core_invalid_ebpf = get_data(x_labels, siyuan_exp_one_core_invalid)
    host_strict_guest_nested_exta_hooks_data, extra_hooks_ebpf = get_data(x_labels, nested_exps)
    host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    # host_strict_guest_nested_data, host_strict_guest_nested_ebpf_data = get_data(x_labels, nested_exps)
    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    z_val_1_DFP_data, z_val_1_DFP_ebpf_data = get_data(x_labels, z_val_1_DFP)
    z_val_10_DFP_data, z_val_10_DFP_ebpf_data = get_data(x_labels, z_val_10_DFP)
    z_val_100_DFP_data, z_val_100_DFP_ebpf_data = get_data(x_labels, z_val_100_DFP)

    # host_strict_guest_shadow_data, host_strict_guest_shadow_ebpf_data = get_data(x_labels, shadow_exps)

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
        { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_exta_hooks_data, 'ebpf': extra_hooks_ebpf, 'color': color_nested },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': '#FF6600' },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Async Invalid', 'data': host_strict_guest_nested_siyuan_one_core_invalid, 'ebpf': extra_hooks_siyuan_one_core_invalid_ebpf, 'color': '#CC79A7' },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention + Async Invalid Wait', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': '#F0E442' },
    
        { 'setup_name': 'vIOMMU Nested + vF&S', 'data': z_val_1_DFP_data, 'ebpf': z_val_1_DFP_ebpf_data, 'color': color_optimization },
        # { 'setup_name': 'Host Strict; Guest vF&S (z=10)', 'data': z_val_10_DFP_data, 'ebpf': z_val_10_DFP_ebpf_data, 'color': default_colors[7] },
        # { 'setup_name': 'Host Strict; Guest vF&S (z=100)', 'data': z_val_100_DFP_data, 'ebpf': z_val_100_DFP_ebpf_data, 'color': default_colors[8] },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='stress_exp',
                      xlabel=f"Flows per core ({n_cores} cores)",
                      output_dir="Siyuan_Evaluation_stress_exp")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                     "__iommu_dma_unmap": ["__iommu_dma_unmap_call", "__iommu_dma_unmap"],
                                 },
                                 xlabel=f"Flows per core ({n_cores} cores)",
                                 title_key='stress_exp',
                                 output_dir="Siyuan_Evaluation_stress_exp")

def plot_tx_ebpf_exp():
    """Plot TX eBPF experiment results."""
    
    # TODO: Update these paths with your actual experiment directories
    # target_values = [4, 8, 12, 16, 20, 24]  # Adjust as needed
    target_values = [4, 8, 12, 16, 20, 24, 28]
    x_labels = [f"{i:02d}" for i in target_values]
    print(x_labels)

    # TODO: Replace with actual experiment paths
    # nested_exps = [
    #     f"/home/schai/viommu_iks_bkp/utils/reports/2026-01-16-08-19-26-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]

    # off_exps = [
    #     f"/home/schai/viommu_iks_bkp/utils/reports/2026-01-16-07-26-51-6.12.9-iommufd-flow{i:02d}-host-off-guest-strict-off-{i}cores" for i in target_values
    # ]

    # NOTE: Bad runs:
    # /home/schai/viommu_siyuan/utils/reports/2026-03-17-02-10-47-server-iommufd-off-6.12.9-iommufd-TX-flow04-host-strict-guest-off-off-4cores-ringbuf512-sockbuf1-RUN-2
    # /home/schai/viommu_siyuan/utils/reports/2026-03-17-02-10-47-server-iommufd-off-6.12.9-iommufd-TX-flow16-host-strict-guest-off-off-16cores-ringbuf512-sockbuf1-RUN-1
    # /home/schai/viommu_siyuan/utils/reports/2026-03-17-02-10-47-server-iommufd-off-6.12.9-iommufd-TX-flow20-host-strict-guest-off-off-20cores-ringbuf512-sockbuf1-RUN-2
    # /home/schai/viommu_siyuan/utils/reports/2026-03-17-02-10-47-server-iommufd-off-6.12.9-iommufd-TX-flow24-host-strict-guest-off-off-24cores-ringbuf512-sockbuf1-RUN-3


    # nested_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-17-04-12-01-server-iommufd-nested-6.12.9-iommufd-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
    # ]

    # off_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-17-02-10-47-server-iommufd-off-6.12.9-iommufd-TX-flow{i:02d}-host-strict-guest-off-off-{i}cores-ringbuf512-sockbuf1" for i in target_values
    # ]

    off_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-20-01-16-54-server-iommufd-off-6.12.9-iommufd-TX-flow{i:02d}-host-strict-guest-off-off-{i}cores-ringbuf512-sockbuf1" for i in target_values
    ]

    nested_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-20-03-13-17-server-iommufd-nested-6.12.9-iommufd-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
    ]


    # z = 1
    # optimization_exps = [
    #     f"/home/schai/viommu_iks_bkp/utils/reports/2026-02-24-23-29-59-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval{z}" for i in target_values
    # ]

    # # 2026-03-08-03-16-10-6.12.9-iommufd-batched-debug-lb-nested-TX-flow01-host-strict-guest-strict-nested-1cores-ringbuf512-sockbuf1-zval1
    # per_core_queue_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-08-03-16-10-6.12.9-iommufd-batched-debug-lb-nested-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval{z}" for i in target_values
    # ]

    # per_core_queue_pinned_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-08-05-15-02-6.12.9-iommufd-batched-debug-lb-nested-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
    # ]
    
    # # 2026-03-10-02-38-59-server-iommufd-vanilla-nested-conf-dlf-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow01-host-strict-guest-strict-nested-1cores-ringbuf512-sockbuf1-zval1
    # batch_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-10-02-38-59-server-iommufd-vanilla-nested-conf-dlf-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval{z}" for i in target_values
    # ]

    # batch_pinned_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-10-04-33-09-server-iommufd-vanilla-nested-conf-pinned-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
    # ]

    # 2026-03-17-07-03-51-server-iommufd-vanilla-nested-conf-dlf-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow04-host-strict-guest-strict-nested-4cores-ringbuf512-sockbuf1-zval1
    # dlf_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-17-07-03-51-server-iommufd-vanilla-nested-conf-dlf-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval1" for i in target_values
    # ]

    dlf_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-20-08-00-05-server-iommufd-nested-iova-contig-dlf-6.12.9-iommufd-nested-iova-contig-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval100" for i in target_values
    ]

    # DATA without pushed skip-map-inval and contiguous IOVA.
    # 2026-03-17-09-06-58-server-iommufd-vanilla-nested-conf-pinned-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow28-host-strict-guest-strict-nested-28cores-ringbuf512-sockbuf1
    # pinned_exps = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-03-17-09-06-58-server-iommufd-vanilla-nested-conf-pinned-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
    # ]

    pinned_exps = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-03-20-05-44-58-server-iommufd-nested-iova-contig-6.12.9-iommufd-nested-iova-contig-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
    ]
    

    # Get data
    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    host_strict_guest_nested_data, host_strict_guest_nested_ebpf_data = get_data(x_labels, nested_exps)
    # optimization_data, optimization_ebpf_data = get_data(x_labels, optimization_exps)

    # per_core_queue_data, per_core_queue_ebpf_data = get_data(x_labels, per_core_queue_exps)
    # per_core_queue_pinned_data, per_core_queue_pinned_ebpf_data = get_data(x_labels, per_core_queue_pinned_exps)

    dlf_data, dlf_ebpf_data = get_data(x_labels, dlf_exps,)
    batch_pinned_data, batch_pinned_ebpf_data = get_data(x_labels, pinned_exps)

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
        { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': color_nested },
        # { 'setup_name': 'vIOMMU Nested + vF&S', 'data': optimization_data, 'ebpf': optimization_ebpf_data, 'color': color_optimization },
        # { 'setup_name': 'vIOMMU Nested + Per Core Queue (DLF) ', 'data': per_core_queue_data, 'ebpf': per_core_queue_ebpf_data, 'color': default_colors[4] },
        # { 'setup_name': 'vIOMMU Nested + Per Core Queue Pinned', 'data': per_core_queue_pinned_data, 'ebpf': per_core_queue_pinned_ebpf_data, 'color': default_colors[5] },

        { 'setup_name': '+ Per Core Queue + Batch (DLF)', 'data': dlf_data, 'ebpf': dlf_ebpf_data, 'color': default_colors[6] },
        { 'setup_name': '+ Per Core Queue + Batch (Pinned)', 'data': batch_pinned_data, 'ebpf': batch_pinned_ebpf_data, 'color': default_colors[7] },
    ]
    
    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='tx-ebpf',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="TX_EBPF_Evaluation")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "intel_iommu_tlb_sync": ["intel_iommu_tlb_sync"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                     "trace_qi_submit_sync_cs": ["trace_qi_submit_sync_cs"],
                                 },
                                 title_key='tx-ebpf',
                                 xlabel="Number of Cores (1 flow/core)",
                                 output_dir="TX_EBPF_Evaluation")


# Archived data!!!!!

# def plot_tx_ebpf_exp():
#     """Plot TX eBPF experiment results."""
    
#     # TODO: Update these paths with your actual experiment directories
#     # target_values = [4, 8, 12, 16, 20, 24]  # Adjust as needed
#     target_values = [4, 8, 12, 16, 20, 24]
#     x_labels = [f"{i:02d}" for i in target_values]
#     print(x_labels)

#     # TODO: Replace with actual experiment paths
#     nested_exps = [
#         f"/home/schai/viommu_iks_bkp/utils/reports/2026-01-16-08-19-26-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
#     ]

#     off_exps = [
#         f"/home/schai/viommu_iks_bkp/utils/reports/2026-01-16-07-26-51-6.12.9-iommufd-flow{i:02d}-host-off-guest-strict-off-{i}cores" for i in target_values
#     ]

#     z = 1
#     optimization_exps = [
#         f"/home/schai/viommu_iks_bkp/utils/reports/2026-02-24-23-29-59-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval{z}" for i in target_values
#     ]

#     # 2026-03-08-03-16-10-6.12.9-iommufd-batched-debug-lb-nested-TX-flow01-host-strict-guest-strict-nested-1cores-ringbuf512-sockbuf1-zval1
#     per_core_queue_exps = [
#         f"/home/schai/viommu_siyuan/utils/reports/2026-03-08-03-16-10-6.12.9-iommufd-batched-debug-lb-nested-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval{z}" for i in target_values
#     ]

#     per_core_queue_pinned_exps = [
#         f"/home/schai/viommu_siyuan/utils/reports/2026-03-08-05-15-02-6.12.9-iommufd-batched-debug-lb-nested-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
#     ]
    
#     # 2026-03-10-02-38-59-server-iommufd-vanilla-nested-conf-dlf-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow01-host-strict-guest-strict-nested-1cores-ringbuf512-sockbuf1-zval1
#     batch_exps = [
#         f"/home/schai/viommu_siyuan/utils/reports/2026-03-10-02-38-59-server-iommufd-vanilla-nested-conf-dlf-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1-zval{z}" for i in target_values
#     ]

#     batch_pinned_exps = [
#         f"/home/schai/viommu_siyuan/utils/reports/2026-03-10-04-33-09-server-iommufd-vanilla-nested-conf-pinned-call-debug-batch-fix-iova-6.12.9-iommufd-batched-debug-lb-nested-fix-iova-TX-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-ringbuf512-sockbuf1" for i in target_values
#     ]

    

#     # Get data
#     host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
#     host_strict_guest_nested_data, host_strict_guest_nested_ebpf_data = get_data(x_labels, nested_exps)
#     optimization_data, optimization_ebpf_data = get_data(x_labels, optimization_exps)

#     per_core_queue_data, per_core_queue_ebpf_data = get_data(x_labels, per_core_queue_exps)
#     per_core_queue_pinned_data, per_core_queue_pinned_ebpf_data = get_data(x_labels, per_core_queue_pinned_exps)

#     batch_data, batch_ebpf_data = get_data(x_labels, batch_exps)
#     batch_pinned_data, batch_pinned_ebpf_data = get_data(x_labels, batch_pinned_exps)

#     datasets = [
#         { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
#         { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': color_nested },
#         # { 'setup_name': 'vIOMMU Nested + vF&S', 'data': optimization_data, 'ebpf': optimization_ebpf_data, 'color': color_optimization },
#         # { 'setup_name': 'vIOMMU Nested + Per Core Queue (DLF) ', 'data': per_core_queue_data, 'ebpf': per_core_queue_ebpf_data, 'color': default_colors[4] },
#         # { 'setup_name': 'vIOMMU Nested + Per Core Queue Pinned', 'data': per_core_queue_pinned_data, 'ebpf': per_core_queue_pinned_ebpf_data, 'color': default_colors[5] },

#         { 'setup_name': '+ Per Core Queue + Batch (DLF)', 'data': batch_data, 'ebpf': batch_ebpf_data, 'color': default_colors[6] },
#         { 'setup_name': '+ Per Core Queue + Batch (Pinned)', 'data': batch_pinned_data, 'ebpf': batch_pinned_ebpf_data, 'color': default_colors[7] },
#     ]
    
#     plot_all_subplots(datasets=datasets,
#                       x_labels=x_labels,
#                       title_key='tx-ebpf',
#                       xlabel="Number of Cores (1 flow/core)",
#                       output_dir="TX_EBPF_Evaluation")

#     plot_ebpf_selected_functions(datasets=datasets,
#                                  x_labels=x_labels,
#                                  selected_functions={
#                                      "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
#                                      "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
#                                      "qi_submit_sync": ["qi_submit_sync"],
#                                      "trace_qi_submit_sync_cs": ["trace_qi_submit_sync_cs"],
#                                  },
#                                  title_key='tx-ebpf',
#                                  xlabel="Number of Cores (1 flow/core)",
#                                  output_dir="TX_EBPF_Evaluation")


def siyuan_Evaluation_ablation():
    
    target_values = [4, 8, 12, 16, 20, 24]
    # x_labels = [f"{i:02d}" for i in range(1, 33)]
    x_labels = [f"{i:02d}" for i in target_values]
    print(x_labels)

    off_exps = [
        f"/home/schai/viommu/utils/reports/2025-11-16-04-13-32-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-off-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]


    nested_exps = [
        f"/home/schai/viommu/utils/reports/2025-11-15-17-53-09-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]


    siyuan_no_map_contention = [
        f"/home/schai/viommu_siyuan/utils/reports/2025-12-05-04-01-47-6.12.9-iommufd-vanilla-based-no-map-contention-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]

    
    siyuan_exp_async_invalid_wait = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-02-03-05-05-6.12.9-iommufd-vanilla-based-no-map-contention-AsyncInvalid-wait-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]


    pinned_async_DFP = [
        f"/home/schai/viommu_owen/utils/reports/2026-02-23-21-47-51-6.12.9-iommufd-vanilla-nested-conf-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]

    z_val_1 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    z_val_10 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    ]

    z_val_100 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    # z_val_1_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    # ]

    # z_val_10_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    # ]

    # z_val_100_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in target_values
    # ]

    z_val_1_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    z_val_10_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    ]

    z_val_100_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in target_values
    ]


    z_val_3_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [4, 8, 12]
    ] + ["/home/schai/viommu_siyuan/utils/reports/2026-02-22-16-37-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow16-host-strict-guest-strict-nested-16cores"] + [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [20, 24]
    ]


    # archived data before deadlock bug fixed
    # z_val_1= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval1"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [20,24]
    # ]

    # z_val_10= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval10"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [20,24]
    # ]

    # z_val_100= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval100"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [20,24]
    # ]


    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    host_strict_guest_nested_data, host_strict_guest_nested_ebpf_data = get_data(x_labels, nested_exps)
    
    host_strict_guest_nested_siyuan_no_map_contention, extra_hooks_siyuan_no_map_contention_ebpf = get_data(x_labels, siyuan_no_map_contention)
    host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    
    z_val_1_data, z_val_1_ebpf_data = get_data(x_labels, z_val_1)
    # z_val_10_data, z_val_10_ebpf_data = get_data(x_labels, z_val_10)
    # z_val_100_data, z_val_100_ebpf_data = get_data(x_labels, z_val_100)

    z_val_1_DFP_data, z_val_1_DFP_ebpf_data = get_data(x_labels, z_val_1_DFP)
    # pinned_async_DFP_data, pinned_async_DFP_ebpf_data = get_data(x_labels, pinned_async_DFP)
    # z_val_10_DFP_data, z_val_10_DFP_ebpf_data = get_data(x_labels, z_val_10_DFP)
    # z_val_100_DFP_data, z_val_100_DFP_ebpf_data = get_data(x_labels, z_val_100_DFP)

    # z_val_3_DFP_data, z_val_3_DFP_ebpf_data = get_data(x_labels, z_val_3_DFP)
    # host_strict_guest_shadow_data, host_strict_guest_shadow_ebpf_data = get_data(x_labels, shadow_exps)

    # Default color palette if not specified
    # default_colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', 
    #                  '#F0E442', '#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']


    # default_colors = ['#0072B2', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00','#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
        { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': color_nested },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': default_colors[8] },
        { 'setup_name': 'vIOMMU Nested + Async (pinned)', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': default_colors[5] },
        { 'setup_name': 'vIOMMU Nested + Async (DLF)', 'data': z_val_1_data, 'ebpf': z_val_1_ebpf_data, 'color': default_colors[4] },
        # { 'setup_name': 'Host Strict; Guest DLF z=10', 'data': z_val_10_data, 'ebpf': z_val_10_ebpf_data, 'color': default_colors[3] },
        # { 'setup_name': 'Host Strict; Guest DLF z=100', 'data': z_val_100_data, 'ebpf': z_val_100_ebpf_data, 'color': default_colors[4] },

        { 'setup_name': 'vIOMMU Nested + Async (DLF) + DFP', 'data': z_val_1_DFP_data, 'ebpf': z_val_1_DFP_ebpf_data, 'color': color_optimization },
        # { 'setup_name': 'vIOMMU Nested + Async (pinned) + DFP', 'data': pinned_async_DFP_data, 'ebpf': pinned_async_DFP_ebpf_data, 'color': default_colors[6] },
        # { 'setup_name': 'Host Strict; Guest DLF z=10 (DFP)', 'data': z_val_10_DFP_data, 'ebpf': z_val_10_DFP_ebpf_data, 'color': default_colors[7] },
        # { 'setup_name': 'Host Strict; Guest DLF z=100 (DFP)', 'data': z_val_100_DFP_data, 'ebpf': z_val_100_DFP_ebpf_data, 'color': default_colors[8] },

        # { 'setup_name': 'Host Strict; Guest DLF z=3 (DFP)', 'data': z_val_3_DFP_data, 'ebpf': z_val_3_DFP_ebpf_data, 'color': default_colors[9] },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='eval_core_exp',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Siyuan_Evaluation_ablation")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                 },
                                 xlabel="Number of Cores (1 flow/core)",
                                 title_key='eval_core_exp',
                                 output_dir="Siyuan_Evaluation_ablation")

def siyuan_Evaluation_ablation():
    
    target_values = [4, 8, 12, 16, 20, 24]
    # x_labels = [f"{i:02d}" for i in range(1, 33)]
    x_labels = [f"{i:02d}" for i in target_values]
    print(x_labels)

    off_exps = [
        f"/home/schai/viommu/utils/reports/2025-11-16-04-13-32-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-off-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]


    nested_exps = [
        f"/home/schai/viommu/utils/reports/2025-11-15-17-53-09-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]


    siyuan_no_map_contention = [
        f"/home/schai/viommu_siyuan/utils/reports/2025-12-05-04-01-47-6.12.9-iommufd-vanilla-based-no-map-contention-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]

    
    siyuan_exp_async_invalid_wait = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-02-03-05-05-6.12.9-iommufd-vanilla-based-no-map-contention-AsyncInvalid-wait-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]


    pinned_async_DFP = [
        f"/home/schai/viommu_owen/utils/reports/2026-02-23-21-47-51-6.12.9-iommufd-vanilla-nested-conf-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    ]

    z_val_1 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    z_val_10 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    ]

    z_val_100 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    # z_val_1_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    # ]

    # z_val_10_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    # ]

    # z_val_100_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in target_values
    # ]

    z_val_1_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    z_val_10_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    ]

    z_val_100_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in target_values
    ]


    z_val_3_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [4, 8, 12]
    ] + ["/home/schai/viommu_siyuan/utils/reports/2026-02-22-16-37-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow16-host-strict-guest-strict-nested-16cores"] + [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [20, 24]
    ]


    # archived data before deadlock bug fixed
    # z_val_1= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval1"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [20,24]
    # ]

    # z_val_10= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval10"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [20,24]
    # ]

    # z_val_100= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval100"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [20,24]
    # ]


    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    host_strict_guest_nested_data, host_strict_guest_nested_ebpf_data = get_data(x_labels, nested_exps)
    
    host_strict_guest_nested_siyuan_no_map_contention, extra_hooks_siyuan_no_map_contention_ebpf = get_data(x_labels, siyuan_no_map_contention)
    host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    
    z_val_1_data, z_val_1_ebpf_data = get_data(x_labels, z_val_1)
    # z_val_10_data, z_val_10_ebpf_data = get_data(x_labels, z_val_10)
    # z_val_100_data, z_val_100_ebpf_data = get_data(x_labels, z_val_100)

    z_val_1_DFP_data, z_val_1_DFP_ebpf_data = get_data(x_labels, z_val_1_DFP)
    pinned_async_DFP_data, pinned_async_DFP_ebpf_data = get_data(x_labels, pinned_async_DFP)
    # z_val_10_DFP_data, z_val_10_DFP_ebpf_data = get_data(x_labels, z_val_10_DFP)
    # z_val_100_DFP_data, z_val_100_DFP_ebpf_data = get_data(x_labels, z_val_100_DFP)

    # z_val_3_DFP_data, z_val_3_DFP_ebpf_data = get_data(x_labels, z_val_3_DFP)
    # host_strict_guest_shadow_data, host_strict_guest_shadow_ebpf_data = get_data(x_labels, shadow_exps)

    # Default color palette if not specified
    # default_colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', 
    #                  '#F0E442', '#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']


    # default_colors = ['#0072B2', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00','#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
        { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': color_nested },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': default_colors[8] },
        # { 'setup_name': 'vIOMMU Nested + Async (pinned)', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': default_colors[5] },
        { 'setup_name': 'vIOMMU Nested + Async (DLF)', 'data': z_val_1_data, 'ebpf': z_val_1_ebpf_data, 'color': default_colors[4] },
        # { 'setup_name': 'Host Strict; Guest DLF z=10', 'data': z_val_10_data, 'ebpf': z_val_10_ebpf_data, 'color': default_colors[3] },
        # { 'setup_name': 'Host Strict; Guest DLF z=100', 'data': z_val_100_data, 'ebpf': z_val_100_ebpf_data, 'color': default_colors[4] },

        { 'setup_name': 'vIOMMU Nested + Async (DLF) + DFP', 'data': z_val_1_DFP_data, 'ebpf': z_val_1_DFP_ebpf_data, 'color': color_optimization },
        # { 'setup_name': 'vIOMMU Nested + Async (pinned) + DFP', 'data': pinned_async_DFP_data, 'ebpf': pinned_async_DFP_ebpf_data, 'color': default_colors[6] },
        # { 'setup_name': 'Host Strict; Guest DLF z=10 (DFP)', 'data': z_val_10_DFP_data, 'ebpf': z_val_10_DFP_ebpf_data, 'color': default_colors[7] },
        # { 'setup_name': 'Host Strict; Guest DLF z=100 (DFP)', 'data': z_val_100_DFP_data, 'ebpf': z_val_100_DFP_ebpf_data, 'color': default_colors[8] },

        # { 'setup_name': 'Host Strict; Guest DLF z=3 (DFP)', 'data': z_val_3_DFP_data, 'ebpf': z_val_3_DFP_ebpf_data, 'color': default_colors[9] },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='eval_ablation_core_exp',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Siyuan_Evaluation_ablation")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                 },
                                 xlabel="Number of Cores (1 flow/core)",
                                 title_key='eval_ablation_core_exp',
                                 output_dir="Siyuan_Evaluation_ablation")

def siyuan_Evaluation_sensitivity():
    
    target_values = [4, 8, 12, 16, 20, 24]
    # x_labels = [f"{i:02d}" for i in range(1, 33)]
    x_labels = [f"{i:02d}" for i in target_values]
    print(x_labels)

    off_exps = [
        f"/home/schai/viommu/utils/reports/2025-11-16-04-13-32-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-off-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]


    nested_exps = [
        f"/home/schai/viommu/utils/reports/2025-11-15-17-53-09-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]


    # siyuan_no_map_contention = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2025-12-05-04-01-47-6.12.9-iommufd-vanilla-based-no-map-contention-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]

    
    # siyuan_exp_async_invalid_wait = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-01-02-03-05-05-6.12.9-iommufd-vanilla-based-no-map-contention-AsyncInvalid-wait-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]


    # pinned_async_DFP = [
    #     f"/home/schai/viommu_owen/utils/reports/2026-02-23-21-47-51-6.12.9-iommufd-vanilla-nested-conf-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]

    z_val_1 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    z_val_10 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    ]

    z_val_100 = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-01-22-19-38-46-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    # z_val_1_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    # ]

    # z_val_10_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    # ]

    # z_val_100_DFP = [
    #     f"/home/schai/viommu_siyuan/utils/reports/2026-02-12-03-47-18-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in target_values
    # ]

    z_val_1_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in target_values
    ]

    z_val_10_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in target_values
    ]

    z_val_100_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-23-01-47-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in target_values
    ]


    z_val_3_DFP = [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [4, 8, 12]
    ] + ["/home/schai/viommu_siyuan/utils/reports/2026-02-22-16-37-19-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow16-host-strict-guest-strict-nested-16cores"] + [
        f"/home/schai/viommu_siyuan/utils/reports/2026-02-22-00-46-43-6.12.9-iommufd-vanilla-nested-distributed-leader-follower-call-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in [20, 24]
    ]


    # archived data before deadlock bug fixed
    # z_val_1= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval1"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval1" for i in [20,24]
    # ]

    # z_val_10= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval10"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval10" for i in [20,24]
    # ]

    # z_val_100= [
    #      f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [8,12]
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-08-16-46-53-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow16-host-strict-guest-strict-nested-16cores-zval100"
    # ] + [
    #     f"/home/schai/viommu_owen/utils/reports/2026-01-09-00-13-06-6.12.9-iommufd-vanilla-based-distributed-leader-follower-flow{i:02d}-host-strict-guest-strict-nested-{i}cores-zval100" for i in [20,24]
    # ]


    host_strict_guest_off_data, host_strict_guest_off_ebpf_data = get_data(x_labels, off_exps)
    host_strict_guest_nested_data, host_strict_guest_nested_ebpf_data = get_data(x_labels, nested_exps)
    
    # host_strict_guest_nested_siyuan_no_map_contention, extra_hooks_siyuan_no_map_contention_ebpf = get_data(x_labels, siyuan_no_map_contention)
    # host_strict_guest_nested_siyuan_async_invalid_wait, extra_hooks_siyuan_async_invalid_wait_ebpf = get_data(x_labels, siyuan_exp_async_invalid_wait)
    
    z_val_1_data, z_val_1_ebpf_data = get_data(x_labels, z_val_1)
    z_val_10_data, z_val_10_ebpf_data = get_data(x_labels, z_val_10)
    z_val_100_data, z_val_100_ebpf_data = get_data(x_labels, z_val_100)

    z_val_1_DFP_data, z_val_1_DFP_ebpf_data = get_data(x_labels, z_val_1_DFP)
    # pinned_async_DFP_data, pinned_async_DFP_ebpf_data = get_data(x_labels, pinned_async_DFP)
    z_val_10_DFP_data, z_val_10_DFP_ebpf_data = get_data(x_labels, z_val_10_DFP)
    z_val_100_DFP_data, z_val_100_DFP_ebpf_data = get_data(x_labels, z_val_100_DFP)

    # z_val_3_DFP_data, z_val_3_DFP_ebpf_data = get_data(x_labels, z_val_3_DFP)
    # host_strict_guest_shadow_data, host_strict_guest_shadow_ebpf_data = get_data(x_labels, shadow_exps)

    # Default color palette if not specified
    # default_colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', 
    #                  '#F0E442', '#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']


    # default_colors = ['#0072B2', '#009E73', '#CC79A7', '#F0E442', '#56B4E9', '#E69F00','#D55E00', '#999999', '#FF6600',
    #                  '#882255', '#332288', '#117733', '#AA4499', '#44AA99',
    #                  '#DDAA33', '#88CCEE', '#BBBBBB', '#661100', '#6699CC']

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
        { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': color_nested },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': default_colors[8] },
        # { 'setup_name': 'vIOMMU Nested + Async (pinned)', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': default_colors[5] },
        { 'setup_name': 'Async (DLF) z=1', 'data': z_val_1_data, 'ebpf': z_val_1_ebpf_data, 'color': default_colors[4] },
        { 'setup_name': 'Async (DLF) z=10', 'data': z_val_10_data, 'ebpf': z_val_10_ebpf_data, 'color': default_colors[5] },
        { 'setup_name': 'Async (DLF) z=100', 'data': z_val_100_data, 'ebpf': z_val_100_ebpf_data, 'color': default_colors[6] },

        # { 'setup_name': 'Async (DLF) z=100 + DFP', 'data': z_val_1_DFP_data, 'ebpf': z_val_1_DFP_ebpf_data, 'color': color_optimization },
        # { 'setup_name': 'vIOMMU Nested + Async (pinned) + DFP', 'data': pinned_async_DFP_data, 'ebpf': pinned_async_DFP_ebpf_data, 'color': default_colors[6] },
        # { 'setup_name': 'Async (DLF) z=100 + DFP', 'data': z_val_10_DFP_data, 'ebpf': z_val_10_DFP_ebpf_data, 'color': default_colors[7] },
        # { 'setup_name': 'Async (DLF) z=100 + DFP', 'data': z_val_100_DFP_data, 'ebpf': z_val_100_DFP_ebpf_data, 'color': default_colors[8] },

        # { 'setup_name': 'Host Strict; Guest DLF z=3 (DFP)', 'data': z_val_3_DFP_data, 'ebpf': z_val_3_DFP_ebpf_data, 'color': default_colors[9] },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='eval_sensitivity_core_exp',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Siyuan_Evaluation_sensitivity")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                 },
                                 xlabel="Number of Cores (1 flow/core)",
                                 title_key='eval_sensitivity_core_exp',
                                 output_dir="Siyuan_Evaluation_sensitivity")

    datasets = [
        { 'setup_name': 'vIOMMU Off', 'data': host_strict_guest_off_data, 'ebpf': host_strict_guest_off_ebpf_data, 'color': color_off },
        { 'setup_name': 'vIOMMU Nested', 'data': host_strict_guest_nested_data, 'ebpf': host_strict_guest_nested_ebpf_data, 'color': color_nested },
        # { 'setup_name': 'Host Strict; Guest Nested No Map Contention', 'data': host_strict_guest_nested_siyuan_no_map_contention, 'ebpf': extra_hooks_siyuan_no_map_contention_ebpf, 'color': default_colors[8] },
        # { 'setup_name': 'vIOMMU Nested + Async (pinned)', 'data': host_strict_guest_nested_siyuan_async_invalid_wait, 'ebpf': extra_hooks_siyuan_async_invalid_wait_ebpf, 'color': default_colors[5] },
        # { 'setup_name': 'Async (DLF) z=1', 'data': z_val_1_data, 'ebpf': z_val_1_ebpf_data, 'color': default_colors[4] },
        # { 'setup_name': 'Async (DLF) z=10', 'data': z_val_10_data, 'ebpf': z_val_10_ebpf_data, 'color': default_colors[5] },
        # { 'setup_name': 'Async (DLF) z=100', 'data': z_val_100_data, 'ebpf': z_val_100_ebpf_data, 'color': default_colors[6] },

        { 'setup_name': 'Async (DLF) z=100 + DFP', 'data': z_val_1_DFP_data, 'ebpf': z_val_1_DFP_ebpf_data, 'color': color_optimization },
        # { 'setup_name': 'vIOMMU Nested + Async (pinned) + DFP', 'data': pinned_async_DFP_data, 'ebpf': pinned_async_DFP_ebpf_data, 'color': default_colors[6] },
        { 'setup_name': 'Async (DLF) z=100 + DFP', 'data': z_val_10_DFP_data, 'ebpf': z_val_10_DFP_ebpf_data, 'color': default_colors[7] },
        { 'setup_name': 'Async (DLF) z=100 + DFP', 'data': z_val_100_DFP_data, 'ebpf': z_val_100_DFP_ebpf_data, 'color': default_colors[8] },

        # { 'setup_name': 'Host Strict; Guest DLF z=3 (DFP)', 'data': z_val_3_DFP_data, 'ebpf': z_val_3_DFP_ebpf_data, 'color': default_colors[9] },
    ]

    plot_all_subplots(datasets=datasets,
                      x_labels=x_labels,
                      title_key='eval_sensitivity_core_exp_dlf',
                      xlabel="Number of Cores (1 flow/core)",
                      output_dir="Siyuan_Evaluation_sensitivity")

    plot_ebpf_selected_functions(datasets=datasets,
                                 x_labels=x_labels,
                                 selected_functions={
                                     "cache_tag_flush_range_np": ["cache_tag_flush_range_np"],
                                     "cache_tag_flush_range": ["cache_tag_flush_range", "cache_tag_flush_range_call"],
                                     "qi_submit_sync": ["qi_submit_sync"],
                                 },
                                 xlabel="Number of Cores (1 flow/core)",
                                 title_key='eval_sensitivity_core_exp_dlf',
                                 output_dir="Siyuan_Evaluation_sensitivity")
                                

if __name__ == "__main__":
    # plot_flows_exp()
    # siyuan_Evaluation_plot_flows_exp()
    # plot_flows_exp_stress()
    # siyuan_Evaluation_ablation()
    # siyuan_Evaluation_sensitivity()
    # plot_tx_ebpf_exp()  # Uncomment when ready to use
    siyuan_flows_exp_motivation()