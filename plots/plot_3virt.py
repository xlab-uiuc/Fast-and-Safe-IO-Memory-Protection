
import matplotlib.pyplot as plt
import numpy as np
import glob
import os


def parse_results(path):
    results = np.genfromtxt(path, dtype=float, delimiter=',', names=True)
    return results

def get_data(prefix, iommu_str, flows, suffix=""):

    folders = [
        prefix + f"flow{f}-" + iommu_str + suffix for f in flows
    ]

    files = [
        "../utils/reports/" + f + "/tput_metrics.dat" for f in folders
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

def get_misses_per_page(data):
    # tput = data['net_tput_mean']
    acks_page = []
    iotlb_miss_page = []
    l1_miss_page = []
    l2_miss_page = []
    l3_miss_page = []

    # acks_page = misses_per_page(sent_packets, tput)
    for idx in range(len(data)):
        tp = data[idx]['net_tput_mean']

        iotlb_miss_page.append(misses_per_page(data[idx]['iotlb_misses_mean'], tp))
        l1_miss_page.append(misses_per_page(data[idx]['l1_misses_mean'], tp))
        l2_miss_page.append(misses_per_page(data[idx]['l2_misses_mean'], tp))
        l3_miss_page.append(misses_per_page(data[idx]['l3_misses_mean'], tp))
        acks_page.append(misses_per_page(data[idx]['sent_packets_mean']/20, tp))

    return iotlb_miss_page, l1_miss_page, l2_miss_page, l3_miss_page, acks_page

def plot_iommu_misses_stats(iommu_on_data, x_labels, title, x_label):
    iotlb_miss_page, l1_miss_page, l2_miss_page, l3_miss_page, acks_page = get_misses_per_page(iommu_on_data)

    bar_width = 0.35
    x = np.arange(len(x_labels))
    plt.bar(x, iotlb_miss_page, bar_width, label='IOMMU TLB misses')
    plt.xlabel(x_label)

    plt.ylabel("IOTLB misses per page")
    plt.title(title + 'IOTLB-miss')
    plt.xticks(x, x_labels)
    plt.legend()
    plt.ylim(0, 3)


    file_name = title + 'IOTLB-miss.png'
    plt.savefig(file_name)
    print('Saved plot to ' + file_name)
    plt.close()


    # plot L1, L2, L3 misses

    x = np.arange(len(x_labels))
    plt.bar(x, acks_page, bar_width, label='ACKs per page')

    plt.xlabel(x_label)
    plt.ylabel("Acks per page")
    plt.title(title + 'Acks')
    plt.xticks(x, x_labels)
    plt.legend()
    plt.ylim(0, 0.15)


    file_name = title + 'Acks.png'
    plt.savefig(file_name)
    print('Saved plot to ' + file_name)
    plt.close()


    # plot L1, L2, L3 misses
    bar_width = 0.25

    plt.bar(x - bar_width,  l1_miss_page, bar_width, label='L1')
    plt.bar(x,              l2_miss_page, bar_width, label='L2')
    plt.bar(x + bar_width,  l3_miss_page, bar_width, label='L3')

    plt.xlabel(x_label)

    plt.ylabel("Misses per page")
    plt.title(title + 'L1-L2-L3-miss')
    plt.xticks(x, x_labels)
    plt.legend()
    plt.ylim(0, 1.0)

    file_name = title + 'L1-L2-L3-miss.png'
    plt.savefig(file_name)
    print('Saved plot to ' + file_name)
    plt.close()


def plot_bars3(host_strict_guest_off, host_strict_guest_shadow, host_strict_guest_nested, x_labels, title, xlabel, ylabel):
    
    print(host_strict_guest_off)
    print(host_strict_guest_shadow)
    print(host_strict_guest_nested)
    print(x_labels)
    print(title)
    print(xlabel)
    print(ylabel)
    bar_width = 0.3
    gap_factor = 1.5
    x = np.arange(len(x_labels)) * gap_factor
    plt.bar(x - bar_width, host_strict_guest_off, bar_width, label='Host IOMMU Strict; Guest IOMMU Off')
    plt.bar(x,              host_strict_guest_shadow, bar_width, label='Host IOMMU Strict; Guest IOMMU Shadow')
    plt.bar(x + bar_width,  host_strict_guest_nested, bar_width, label='Host IOMMU Strict; Guest IOMMU Nested')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x, x_labels)

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2)
    plt.subplots_adjust(bottom=0.25)

    plt.savefig(title + '.png', bbox_inches='tight')
    print('Saved plot to ' + title + '.png')
    plt.close()

def plot_all_subplots(host_strict_guest_off_data, host_strict_guest_shadow_data, host_strict_guest_nested_data, x_labels, title_key, xlabel):
    plot_bars3(
        host_strict_guest_off = [ r['net_tput_mean'] for r in host_strict_guest_off_data ],
        host_strict_guest_shadow =  [ r['net_tput_mean'] for r in host_strict_guest_shadow_data ],
        host_strict_guest_nested=[ r['net_tput_mean'] for r in host_strict_guest_nested_data ],
        x_labels = x_labels,
        title = title_key + '-tput',
        xlabel=xlabel,
        ylabel="Throughput (Gbps)",
    )
    plot_bars3(
        host_strict_guest_off = [ r['cpu_utils_mean'] for r in host_strict_guest_off_data ],
        host_strict_guest_shadow =  [ r['cpu_utils_mean'] for r in host_strict_guest_shadow_data ],
        host_strict_guest_nested=[ r['cpu_utils_mean'] for r in host_strict_guest_nested_data ],
        x_labels = x_labels,
        title = title_key + '-cpu-util',
        xlabel=xlabel,
        ylabel="% CPU Utilization",
    )
    plot_bars3(
        host_strict_guest_off = [ r['retx_rate_mean'] for r in host_strict_guest_off_data ],
        host_strict_guest_shadow =  [ r['retx_rate_mean'] for r in host_strict_guest_shadow_data ],
        host_strict_guest_nested=[ r['retx_rate_mean'] for r in host_strict_guest_nested_data ],
        x_labels = x_labels,
        title = title_key + '-drop-rate',
        xlabel=xlabel,
        ylabel="Drop rate",
    )
    plot_iommu_misses_stats(
        iommu_on_data = host_strict_guest_off_data,
        x_labels = x_labels,
        title = title_key +  '-host-strict-guest-off-misses',
        x_label=xlabel,
    )
    plot_iommu_misses_stats(
        iommu_on_data = host_strict_guest_shadow_data,
        x_labels = x_labels,
        title = title_key +  '-host-strict-guest-shadow-misses',
        x_label=xlabel,
    )
    plot_iommu_misses_stats(
        iommu_on_data = host_strict_guest_nested_data,
        x_labels = x_labels,
        title = title_key +  '-host-strict-guest-nested-misses',
        x_label=xlabel,
    )

#16-10_03-18-6.12.9-vanilla-flow05-iommu-on-host-strict-guest-strict-ofed24.10
#17-21_03-18-6.12.9-vanilla-flow05-iommu-on-host-strict-guest-off-ofed24.10
#18-43_03-18-6.12.9-vanilla-flow05-iommu-on-host-lazy-guest-lazy-ofed24.10
#20-13_03-18-6.12.9-vanilla-flow05-iommu-on-host-lazy-guest-off-ofed24.10
def plot_flows_exp():
    x_labels =  ["20", "40", "60", "80", "160"]
    host_strict_guest_off_data = get_data(
        prefix="2025-09-08-02-07-12-6.12.9-iommufd-",
        iommu_str="host-strict-guest-off",
        suffix="-ringbuf-512_sokcetbuf1_20cores",
        flows=x_labels)
    host_strict_guest_shadow_data = get_data(prefix="2025-09-08-01-37-40-6.12.9-iommufd-", iommu_str="host-strict-guest-on-shadow",
                                             suffix="-ringbuf-512_sokcetbuf1_20cores", flows=x_labels)
    host_strict_guest_nested_data = get_data(prefix="2025-09-08-02-39-18-6.12.9-iommufd-", iommu_str="host-strict-guest-on-nested",
                                             suffix="-ringbuf-512_sokcetbuf1_20cores", flows=x_labels)

    plot_all_subplots(host_strict_guest_off_data= host_strict_guest_off_data,
                        host_strict_guest_shadow_data=host_strict_guest_shadow_data,
                        host_strict_guest_nested_data=host_strict_guest_nested_data,
                        x_labels=x_labels,
                        title_key='Emerald-Rapids-CX7-6.12.9-iommufd',
                        xlabel="Number of Flows")

#6.12.9-vanilla-iommu-on-lazy-lazy-ring_buffer-0256
#6.12.9-vanilla-iommu-on-lazy-off-ring_buffer-0256
#6.12.9-vanilla-iommu-on-strict-off-ring_buffer-0256
#6.12.9-vanilla-iommu-on-strict-strict-ring_buffer-0256
def plot_ring_buf_exp():
    x_labels =  ["256", "512", "1024", "2048"]
    host_strict_guest_off_data = get_data_ring(prefix="", iommu_str="host-strict-guest-off")
    host_strict_guest_shadow_data = get_data_ring(prefix="", iommu_str="host-strict-guest-shadow")
    host_strict_guest_nested_data = get_data_ring(prefix="", iommu_str="host-strict-guest-nested")

    plot_all_subplots(host_strict_guest_off_data= host_strict_guest_off_data,
                        host_strict_guest_shadow_data=host_strict_guest_shadow_data,
                        host_strict_guest_nested_data=host_strict_guest_nested_data,
                        x_labels=x_labels,
                        title_key='6.12.9-ring-buffer',
                        xlabel="Ring Buffer Size")


# plot_ring_buf_exp()
plot_flows_exp()
