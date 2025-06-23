
import matplotlib.pyplot as plt
import numpy as np

def parse_results(path):
    results = np.genfromtxt(path, dtype=float, delimiter=',', names=True)
    return results

def get_data(prefix, iommu_str, suffix=""):

    flows = ["05", "10", "20", "40"]
    folders = [
        prefix + f"flow{f}-" + iommu_str + suffix for f in flows
    ]

    files = [
        "../../utils/reports/" + f + "/tput_metrics.dat" for f in folders
    ]

    data = [
        parse_results(f) for f in files
    ]

    return data


def get_data_ring(prefix, iommu_str, suffix=""):

    x_labels =  ["0256", "0512", "1024", "2048"]
    folders = [
        prefix + iommu_str + "-ring_buffer-"+ x for x in x_labels
    ]

    files = [
        "../../utils/reports/" + f + "/tput_metrics.dat" for f in folders
    ]

    data = [
        parse_results(f) for f in files
    ]

    return data


def plot_bars4(host_strict_guest_off, host_strict_guest_strict, host_lazy_guest_off, host_lazy_guest_lazy, x_labels, title, xlabel, ylabel):
    bar_width = 0.3
    gap_factor = 1.5
    # plt.plot(iommu_off_data, iommu_on_data)
    x = np.arange(len(x_labels)) * gap_factor
    plt.bar(x - bar_width/2- bar_width, host_lazy_guest_off, bar_width, label='Host IOMMU Lazy; Guest IOMMU Off')
    plt.bar(x - bar_width/2, host_strict_guest_off, bar_width, label='Host IOMMU Strict; Guest IOMMU Off')
    plt.bar(x + bar_width/2, host_lazy_guest_lazy, bar_width, label='Host IOMMU Lazy; Guest IOMMU Lazy')
    plt.bar(x + bar_width/2 + bar_width, host_strict_guest_strict, bar_width, label='Host IOMMU Strict; Guest IOMMU Strict')
    # plt.bar(x + bar_width/2, host_lazy_guest_off, bar_width, label='Host IOMMU Lazy; Guest IOMMU Off')
    # plt.bar(x + bar_width/2 + bar_width, host_lazy_guest_lazy, bar_width, label='Host IOMMU Lazy; Guest IOMMU Lazy')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, x_labels)
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    plt.subplots_adjust(bottom=0.25)
    
    #plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #plt.tight_layout()
    plt.savefig(title + '.png', bbox_inches='tight')
    print('Saved plot to ' + title + '.png')
    plt.close()

def plot_flows_subplots(host_strict_guest_off_data, host_strict_guest_strict_data, host_lazy_guest_off_data, host_lazy_guest_lazy_data, x_labels, title_key):
    plot_bars4(
        host_strict_guest_off = [ r['net_tput_mean'] for r in host_strict_guest_off_data ],
        host_strict_guest_strict=  [ r['net_tput_mean'] for r in host_strict_guest_strict_data ],
        host_lazy_guest_off=[ r['net_tput_mean'] for r in host_lazy_guest_off_data ],
        host_lazy_guest_lazy=[ r['net_tput_mean'] for r in host_lazy_guest_lazy_data ],
        x_labels = x_labels,
        title = title_key + '-tput',
        xlabel="Number of Flows",
        ylabel="Throughput (Gbps)",
    )
    plot_bars4(
        host_strict_guest_off = [ r['cpu_utils_mean'] for r in host_strict_guest_off_data ],
        host_strict_guest_strict=  [ r['cpu_utils_mean'] for r in host_strict_guest_strict_data ],
        host_lazy_guest_off=[ r['cpu_utils_mean'] for r in host_lazy_guest_off_data ],
        host_lazy_guest_lazy=[ r['cpu_utils_mean'] for r in host_lazy_guest_lazy_data ],
        x_labels = x_labels,
        title = title_key + '-cpu-util',
        xlabel="Number of Flows",
        ylabel="% CPU Utilization",
    )

def plot_ring_buffer_subplots(host_strict_guest_off_data, host_strict_guest_strict_data, host_lazy_guest_off_data, host_lazy_guest_lazy_data, x_labels, title_key):
    plot_bars4(
        host_strict_guest_off = [ r['net_tput_mean'] for r in host_strict_guest_off_data ],
        host_strict_guest_strict=  [ r['net_tput_mean'] for r in host_strict_guest_strict_data ],
        host_lazy_guest_off=[ r['net_tput_mean'] for r in host_lazy_guest_off_data ],
        host_lazy_guest_lazy=[ r['net_tput_mean'] for r in host_lazy_guest_lazy_data ],
        x_labels = x_labels,
        title = title_key + '-tput',
        xlabel="Ring Buffer Size",
        ylabel="Throughput (Gbps)",
    )
    plot_bars4(
        host_strict_guest_off = [ r['cpu_utils_mean'] for r in host_strict_guest_off_data ],
        host_strict_guest_strict=  [ r['cpu_utils_mean'] for r in host_strict_guest_strict_data ],
        host_lazy_guest_off=[ r['cpu_utils_mean'] for r in host_lazy_guest_off_data ],
        host_lazy_guest_lazy=[ r['cpu_utils_mean'] for r in host_lazy_guest_lazy_data ],
        x_labels = x_labels,
        title = title_key + '-cpu-util',
        xlabel="Ring Buffer Size",
        ylabel="% CPU Utilization",
    )


def plot_flows_exp():
    x_labels =  ["05", "10", "20", "40"]
    host_strict_guest_off_data =  get_data(prefix="10-07_03-03-6.12.9-vanilla-", iommu_str="iommu-on", suffix="-ofed24.10")
    host_lazy_guest_off_data =  get_data(prefix="11-27_03-03-6.12.9-vanilla-", iommu_str="iommu-on-lazy", suffix="-ofed24.10")

    host_strict_guest_strict_data = get_data(prefix="13-20_03-03-6.12.9-vanilla-", iommu_str="iommu-on-strict-strict",  suffix="-ofed24.10")
    host_lazy_guest_lazy_data = get_data(prefix="12-25_03-03-6.12.9-vanilla-", iommu_str="iommu-on-lazy-lazy",  suffix="-ofed24.10")

    plot_flows_subplots(host_strict_guest_off_data= host_strict_guest_off_data,
                        host_strict_guest_strict_data=host_strict_guest_strict_data,
                        host_lazy_guest_off_data=host_lazy_guest_off_data,
                        host_lazy_guest_lazy_data=host_lazy_guest_lazy_data,
                        x_labels=x_labels,
                        title_key='6.12.9-flows')

def plot_ring_buf_exp():
    x_labels =  ["256", "512", "1024", "2048"]
    host_strict_guest_off_data = get_data_ring(prefix="6.12.9-vanilla-", iommu_str="iommu-on")
    host_lazy_guest_off_data = get_data_ring(prefix="6.12.9-vanilla-", iommu_str="iommu-on-lazy")
    host_strict_guest_strict_data = get_data_ring(prefix="6.12.9-vanilla-", iommu_str="iommu-on-strict-strict")
    host_lazy_guest_lazy_data= get_data_ring(prefix="6.12.9-vanilla-", iommu_str="iommu-on-lazy-lazy")

    plot_ring_buffer_subplots(host_strict_guest_off_data= host_strict_guest_off_data,
                        host_strict_guest_strict_data=host_strict_guest_strict_data,
                        host_lazy_guest_off_data=host_lazy_guest_off_data,
                        host_lazy_guest_lazy_data=host_lazy_guest_lazy_data,
                        x_labels=x_labels,
                        title_key='6.12.9-ring-buffer')


plot_ring_buf_exp()
plot_flows_exp()
