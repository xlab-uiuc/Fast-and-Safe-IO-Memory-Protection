
import matplotlib.pyplot as plt
import numpy as np

def get_tput(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
    
    # Extract the third number from the second line (index 2)
    if len(lines) > 1:  # Ensure there are at least two lines
        tput = lines[1].strip().split(",")[2]
        # print(tput)
        return float(tput)
    else:
        print("File does not contain enough lines.")

# get_tput("/home/benny/Fast-and-Safe-IO-Memory-Protection-Siyuan/utils/reports/6.12.9-vanilla-flow05-iommu-off/tput_metrics.dat")

def parse_results(path):
    results = np.genfromtxt(path, dtype=float, delimiter=',', names=True)
    return results

def get_data(prefix, iommu_str, suffix=""):
   
    # flows = ["05", "10", "20", "40"]
    flows = ["20", "40", "60", "160"]
    folders = [
        prefix + f"flow{f}-" + iommu_str + suffix for f in flows
    ]

    print(folders)
    files = [
        "../../utils/reports/" + f + "/tput_metrics.dat" for f in folders
    ]

    data = [
        parse_results(f) for f in files
    ]
    
    return data

def get_data_ring(prefix, iommu_str, x_labels, suffix=""):
   
    # x_labels =  ["0256", "0512", "1024", "2048"]
    folders = [
        prefix + iommu_str + "-ringbuf-"+ x + suffix for x in x_labels
    ]
    print(folders)
    files = [
        "../../utils/reports/" + f + "/tput_metrics.dat" for f in folders
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

def plot_tput(iommu_off_data, iommu_on_data, x_ticks, title, x_label):
    bar_width = 0.35
    # plt.plot(iommu_off_data, iommu_on_data)
    x = np.arange(len(x_ticks))
    plt.bar(x - bar_width/2, iommu_off_data, bar_width, label='Guest IOMMU off')
    plt.bar(x + bar_width/2, iommu_on_data, bar_width, label='Guest IOMMU on')

    plt.xlabel(x_label)

    plt.ylabel("Throughput (Gbps)")
    plt.title(title)
    plt.xticks(x, x_ticks)
    plt.legend()

    plt.savefig(title + '.png')
    print('Saved plot to ' + title + '.png')
    plt.close()

def plot_drop_rate(iommu_off_data, iommu_on_data, x_ticks, title, x_label):
    bar_width = 0.35
    # plt.plot(iommu_off_data, iommu_on_data)
    x = np.arange(len(x_ticks))
    plt.bar(x - bar_width/2, iommu_off_data, bar_width, label='IOMMU off')
    plt.bar(x + bar_width/2, iommu_on_data, bar_width, label='IOMMU on')

    plt.xlabel(x_label)

    plt.ylabel("Drop rate")
    plt.title(title)
    plt.xticks(x, x_ticks)
    plt.legend()

    plt.savefig(title + '.png')
    print('Saved plot to ' + title + '.png')
    plt.close()

def plot_iommu_misses_stats(iommu_on_data, x_ticks, title, x_label):
    iotlb_miss_page, l1_miss_page, l2_miss_page, l3_miss_page, acks_page = get_misses_per_page(iommu_on_data)

    bar_width = 0.35
    # plt.plot(iommu_off_data, iommu_on_data)
    x = np.arange(len(x_ticks))
    plt.bar(x, iotlb_miss_page, bar_width, label='IOMMU TLB misses')
    # plt.bar(x + bar_width/2, iommu_on_data, bar_width, label='IOMMU on')

    plt.xlabel(x_label)

    plt.ylabel("IOTLB misses per page")
    plt.title(title + 'IOTLB-miss')
    plt.xticks(x, x_ticks)
    plt.legend()
    plt.ylim(0, 3)


    file_name = title + 'IOTLB-miss.png'
    plt.savefig(file_name)
    print('Saved plot to ' + file_name)
    plt.close()


    # plot L1, L2, L3 misses

    x = np.arange(len(x_ticks))
    plt.bar(x, acks_page, bar_width, label='ACKs per page')
    # plt.bar(x + bar_width/2, iommu_on_data, bar_width, label='IOMMU on')

    plt.xlabel(x_label)

    plt.ylabel("Acks per page")
    plt.title(title + 'ACKs per page')
    plt.xticks(x, x_ticks)
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
    plt.xticks(x, x_ticks)
    plt.legend()
    plt.ylim(0, 1.0)

    file_name = title + 'L1-L2-L3-miss.png'
    plt.savefig(file_name)
    print('Saved plot to ' + file_name)
    plt.close()

def plot_all_subplots(iommu_off_all_data, iommu_on_all_data, x_ticks, x_label, title_key):
    plot_tput(
        iommu_off_data = [ r['net_tput_mean'] for r in iommu_off_all_data ],
        iommu_on_data = [ r['net_tput_mean'] for r in iommu_on_all_data ],
        x_ticks = x_ticks,
        x_label = x_label,
        title = title_key + '-tput'
    )

    plot_drop_rate(
        iommu_off_data = [ r['retx_rate_mean'] for r in iommu_off_all_data ],
        iommu_on_data = [ r['retx_rate_mean'] for r in iommu_on_all_data ],
        x_ticks = x_ticks,
        x_label = x_label,
        title = title_key + 'drop-rate'
    )

    plot_iommu_misses_stats(
        iommu_on_data = iommu_on_all_data,
        x_ticks = x_ticks,
        x_label = x_label,
        title = title_key + '-misses'
    )

def plot_throughput_subplots(iommu_off_all_data, iommu_on_all_data, x_labels, title_key):
    plot_tput(
        iommu_off_data = [ r['net_tput_mean'] for r in iommu_off_all_data ],
        iommu_on_data = [ r['net_tput_mean'] for r in iommu_on_all_data ],
        x_labels = x_labels,
        title = title_key + '-tput'
    )


def plot_tput_f_and_s():
    x_labels =  ["20", "40", "60", "160"]
    iommu_off_all_data = get_data(prefix="2025-09-07-13-42-13-6.12.9-iommufd-", iommu_str="iommu-off", suffix="-ringbuf-512_sokcetbuf1_20cores")
    iommu_on_all_data = get_data(prefix="2025-09-07-15-42-14-6.12.9-iommufd-", iommu_str="iommu-on",  suffix="-ringbuf-512_sokcetbuf1_20cores")
    
    plot_all_subplots(iommu_off_all_data, iommu_on_all_data, 
        x_ticks=x_labels, x_label="# of flows", title_key='Emerald-Rapids-CX7-6.12.9-iommufd')
    

def plot_tput_new_kernel():
    x_labels =  ["05", "10", "20", "40"]
    iommu_off_all_data = get_data(prefix="6.12.9-vanilla-", iommu_str="iommu-off")
    iommu_on_all_data = get_data(prefix="6.12.9-vanilla-", iommu_str="iommu-on")

    plot_all_subplots(iommu_off_all_data, iommu_on_all_data, x_labels, '6.12.9')
    
def plot_tput_new_ofed():
    x_labels =  ["05", "10", "20", "40"]
    iommu_off_all_data = get_data(prefix="6.12.9-vanilla-", iommu_str="iommu-off", suffix="-ofed24.10")
    iommu_on_all_data = get_data(prefix="6.12.9-vanilla-", iommu_str="iommu-on", suffix="-ofed24.10-paused")
    
    plot_all_subplots(iommu_off_all_data, iommu_on_all_data, x_labels, '6.12.9-ofed24.10')

def plot_tput_new_ofed2():
    x_labels =  ["05", "10", "20", "40"]
    iommu_off_all_data = get_data(prefix="6.12.9-vanilla-", iommu_str="iommu-off", suffix="-ofed24.10")
    iommu_on_all_data = get_data(prefix="6.12.9-vanilla-", iommu_str="iommu-on", suffix="-ofed24.10-paused3")
    
    plot_all_subplots(iommu_off_all_data, iommu_on_all_data, x_labels, '6.12.9-ofed24.10-paused3')

def plot_ring_buf_exp():
    # x_labels =  ["256", "512", "1024", "2048"]
    x_labels = ["512", "1024", "2048", "4096"]
    iommu_off_all_data = get_data_ring(
        prefix="2025-09-07-14-00-41-6.12.9-iommufd-flow20-", 
        iommu_str="iommu-off", 
        x_labels=x_labels,
        suffix="_sokcetbuf1_20cores")
    iommu_on_all_data = get_data_ring(
        prefix="2025-09-07-16-01-17-6.12.9-iommufd-flow20-", 
        iommu_str="iommu-on", 
        x_labels=x_labels,
        suffix="_sokcetbuf1_20cores")
    
    
    plot_all_subplots(iommu_off_all_data, iommu_on_all_data, 
        x_ticks=x_labels, x_label="Ring buffer size", title_key='Emerald-Rapids-CX7-6.12.9-iommufd')

# plot_tput_f_and_s()
plot_ring_buf_exp()
