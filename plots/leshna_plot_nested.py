
import matplotlib.pyplot as plt
import numpy as np
import glob
import os
import pandas as pd

color_off = '#0072B2'
color_nested = '#009E73'
color_shadow = '#CC79A7'
color_optimization ='#F0E442'

def calculate_plot_params(num_x_labels, num_series):
    """
    Dynamically calculate plot parameters based on data dimensions.
    
    Args:
        num_x_labels: Number of x-axis categories
        num_series: Number of data series being plotted
    
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
    base_font = 8   # 8pt matches ACM 9pt body text when figure is scaled
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
    figsize = (base_width * width_scale, base_height * height_scale)
    
    # Font size adjustments
    # Reduce font size for many labels or series
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

def plot_bars_dynamic(series_list, x_labels, title, xlabel, ylabel, 
                     output_dir=None, precision=1, show_value_labels=None):
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
    """
    if series_list is None or len(series_list) == 0 or x_labels is None:
        return
    
    num_series = len(series_list)
    num_x_labels = len(x_labels)
    
    # Get dynamic parameters
    params = calculate_plot_params(num_x_labels, num_series)
    
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
    
    # Legend with dynamic positioning
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
    #           ncol=params['legend_ncol'], fontsize=params['legend_fontsize'],
    #           frameon=True, shadow=True)
    plt.legend(loc='upper left',
              ncol=1,
              fontsize=params['legend_fontsize'],
              frameon=True,
              framealpha=0.85,
              edgecolor='#cccccc',
              borderpad=0.4,
              labelspacing=0.25,
              handlelength=1.4,
              handletextpad=0.4)


    # Add value labels on bars if requested
    if show_value_labels:
        ymax = max(series_max_values) if len(series_max_values) > 0 else 1
        ymax = max(ymax, 1e-6)
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
                    plt.text(
                        bar.get_x() + bar.get_width() / 2,
                        height + y_offset,
                        f"{height:.{precision}f}",
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

def get_data(x_labels, exps):
    files = [
        exp + "/tput_metrics.dat" for exp in exps
    ]

    data = [
        parse_results(f) for f in files
    ]

    tput = [d['net_tput_mean'] for d in data]
    ebpf_data = get_ebpf_stats(exps, tput)

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

def get_ebpf_single_run(exp_name, run_id, tput):
    """Get eBPF stats for a single run."""
    file = exp_name + "-RUN-" + str(run_id) + "/ebpf_guest_stats.csv"
    if not os.path.exists(file):
        print(f"File {file} does not exist")
        return None
    return get_ebpf_stats_from_csv(file, tput)

def get_ebpf_stats(exps, tput):
    """Get eBPF stats averaged across multiple runs for each experiment."""
    n_runs = 1
    ebpf_aggregated_data = []
    
    for idx, exp in enumerate(exps):
        ebpf_data_per_exp = []
        
        # Collect data from all runs
        for run_id in range(n_runs):
            ebpf_data = get_ebpf_single_run(exp, run_id, tput[idx])
            if ebpf_data is None:
                print(f"Failed to get eBPF data for {exp} run {run_id}")
                continue
            ebpf_data_per_exp.append(ebpf_data)
        
        if len(ebpf_data_per_exp) == 0:
            print(f"No eBPF data found for experiment {exp}")
            ebpf_aggregated_data.append(None)
            continue
        
        # Calculate mean and stddev across runs for each function
        # Group by function name and calculate statistics
        all_functions = ebpf_data_per_exp[0]['function'].unique()
        
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
        output_file = f"ebpf_aggregated_{exp.split('/')[-1]}.csv"
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

def plot_ebpf_selected_functions(datasets, x_labels, selected_functions, title_key, output_dir=None):
    """Plot selected eBPF functions' metrics across experiments for multiple setups.

    datasets: list of dicts with keys: 'setup_name' (str), 'ebpf' (list[pd.DataFrame]), 'color' (str)
    """
    if datasets is None or len(datasets) == 0:
        return

    num_experiments = len(x_labels) if x_labels is not None else 0
    for ds in datasets:
        ebpf_list = ds.get('ebpf', [])
        if len(ebpf_list) != num_experiments:
            print(f"eBPF data length mismatch for {ds.get('setup_name', 'unknown')}; skipping eBPF plots")
            return

    def extract_metric_series(ebpf_data_list, function_name, column_name):
        """Extract values for a specific metric column."""
        series_values = []
        for df in ebpf_data_list:
            if df is None or 'function' not in df.columns:
                series_values.append(0)
                continue
            row = df[df['function'] == function_name]
            if row.empty or column_name not in row.columns:
                series_values.append(0)
                continue
            value = row.iloc[0][column_name]
            try:
                series_values.append(float(value))
            except Exception:
                series_values.append(0)
        return series_values
    
    def extract_metric_with_stddev(ebpf_data_list, function_name, column_name):
        """Extract both values and stddev for a specific metric."""
        values = extract_metric_series(ebpf_data_list, function_name, column_name)
        stddev_col = f'{column_name}_stddev'
        errors = extract_metric_series(ebpf_data_list, function_name, stddev_col)
        return values, errors

    def sanitize(name):
        return str(name).replace('/', '_').replace(' ', '_')

    for func in selected_functions:
        # Count
        series_list = []
        for ds in datasets:
            values, errors = extract_metric_with_stddev(ds['ebpf'], func, 'count')
            series_list.append({
                'label': ds['setup_name'],
                'values': values,
                'errors': errors,
                'color': ds.get('color')
            })
        plot_bars_dynamic(series_list, x_labels,
                        title=f"{title_key}-{sanitize(func)}-count",
                        xlabel="Experiments",
                        ylabel="Count",
                        output_dir=output_dir,
                        precision=1)

        # Mean (ns)
        series_list = []
        for ds in datasets:
            values, errors = extract_metric_with_stddev(ds['ebpf'], func, 'mean_ns')
            series_list.append({
                'label': ds['setup_name'],
                'values': values,
                'errors': errors,
                'color': ds.get('color')
            })
        plot_bars_dynamic(series_list, x_labels,
                        title=f"{title_key}-{sanitize(func)}-mean_ns",
                        xlabel="Experiments",
                        ylabel="Mean (ns)",
                        output_dir=output_dir,
                        precision=1)

        # Count per page
        series_list = []
        for ds in datasets:
            values, errors = extract_metric_with_stddev(ds['ebpf'], func, 'count_per_page')
            series_list.append({
                'label': ds['setup_name'],
                'values': values,
                'errors': errors,
                'color': ds.get('color')
            })
        plot_bars_dynamic(series_list, x_labels,
                        title=f"{title_key}-{sanitize(func)}-count_per_page",
                        xlabel="Experiments",
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

    # nested_exps_extra_hook = [
    #     f"../utils/reports/2025-11-17-22-20-09-6.12.9-iommufd-extra-hooks-flow{i:02d}-host-strict-guest-strict-nested-{i}cores" for i in target_values
    # ]
    nested_exps = [
        f"../utils/reports/2025-11-15-17-53-09-6.12.9-iommufd-flow{i:02d}-host-strict-guest-strict-nested-ringbuf-512_sokcetbuf1_{i}cores" for i in target_values
    ]

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
                                 selected_functions=["cache_tag_flush_range_np", "cache_tag_flush_range", "qi_submit_sync",],
                                 title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
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

plot_flows_exp()
