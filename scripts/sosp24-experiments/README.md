# SOSP 2024 Artifact Evaluation

## Hardware Configuration
Our hardware configuration used in the paper is: 
* CPU: 4 socket Intel Xeon Gold 6234 3.3GHz with 8 cores per socket 
* RAM: 384GB
* NIC: 100Gbps NVIDIA Mellanox ConnectX-5

We run Ubuntu 20.04 (LTS) with Linux kernel v6.0.3. 

**[NOTE]:** If you have not followed the (link setup instructions), please do so before continuing. We have provided our setup to use by artifact evaluators, so you may skip the instructions and jump right to the section below on running experiments.

## Running Experiments
Make sure that each experiment downs and then ups the interface to reset. 

Many experiments require the same scripts to be run with different kernels and IOMMU configurations: Linux, Linux + IOMMU On, Linux + IOMMU On + F&S. We have included which configurations are required for each figure (e.g. **[Linux, Linux + IOMMU On]** or **[Linux, Linux + IOMMU On, Linux + IOMMU On + F&S]**). Instructions for booting into the correct kernel configuration are below. To save time, we recommend running all the scripts before changing the configuration and then running them all again rather than changing the configuration for each figure. 

#### Loading different kernel configurations
Assuming the kernels have already been compiled with the names in (link to getting started), the following instructions show how to setup each configuration.

**Linux (IOMMU Off):**
Edit `/etc/default/grub` to boot with Linux 6.0.3 as default. Comment all `GRUB_DEFAULT=` lines except for the 6.0.3+ version. For example:
```bash
#GRUB_DEFAULT="1>Ubuntu, with Linux 3.4.5"
GRUB_DEFAULT="1>Ubuntu, with Linux 6.0.3+"
#GRUB_DEFAULT="1>Ubuntu, with Linux 5.4.3"
```
At the bottom of the `/etc/default/grub` file, make sure the default kernel command line disables IOMMU (comment out the line that enables it). For example:
```bash
#GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu.strict=1"
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=off"
```
Reboot the machine and confirm that the correct kernel is being used and that the IOMMU is disabled
```bash
uname -r
dmesg | grep -i "iommu"
```
**Linux + IOMMU On:**
Edit `/etc/default/grub` to boot with Linux 6.0.3 as default. Comment all `GRUB_DEFAULT=` lines except for the 6.0.3+ version. For example:
```bash
#GRUB_DEFAULT="1>Ubuntu, with Linux 3.4.5"
GRUB_DEFAULT="1>Ubuntu, with Linux 6.0.3+"
#GRUB_DEFAULT="1>Ubuntu, with Linux 5.4.3"
```
At the bottom of the `/etc/default/grub` file, make sure the kernel command line enables the IOMMU in strict mode:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu.strict=1"
#GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=off"
```
Reboot the machine and confirm that the correct kernel is being used and that the IOMMU is enabled in strict mode
```bash
uname -r
dmesg | grep -i "iommu"
```
**Linux + IOMMU On + F&S:**
Edit `/etc/default/grub` to boot with Linux 6.0.3 + F&S as default. Comment all `GRUB_DEFAULT=` lines except for the 6.0.3sol+ version. For example:
```bash
#GRUB_DEFAULT="1>Ubuntu, with Linux 3.4.5"
GRUB_DEFAULT="1>Ubuntu, with Linux 6.0.3sol+"
#GRUB_DEFAULT="1>Ubuntu, with Linux 5.4.3"
```
At the bottom of the `/etc/default/grub` file, make sure the kernel command line enables the IOMMU in strict mode:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu.strict=1"
#GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=off"
```
Reboot the machine and confirm that the correct kernel is being used and that the IOMMU is enabled in strict mode
```bash
uname -r
dmesg | grep -i "iommu"
```

### Detailed Instructions 
Now we provide how to use our scripts to reproduce the results in the paper. All scripts assume the working directory is `linux_iommu/scripts/sosp24-experiments`.

TODO: I also need a python utility that will print each of the parts I use for the figure. So throughput, IOTLB and page table cache misses per page, etc. It shouold operate on the final report csv, so that they can use as many runs as they want. 


#### Figure 2 - Varying Number of Flows
**[Linux, Linux + IOMMU On]**
Note: Follow the (link to Loading different kernel modules...) instructions to change the configuration between **[Linux]** and **[Linux + IOMMU On]**.  

```bash
./flows_exp.sh
```

run utility that will read out all the values for each of (a), (b), (c), (d), (e). Except for the IOVA locality, since that's not part of the script and was a separate logging I did that shouldn't be used in production in testing


####  Figure 3 - Varying Ring Buffer Size
**[Linux, Linux + IOMMU On]**
```bash
./ringbuffer_exp.sh
```


#### Figure 5 - Varying Number of Flows
**[Linux + IOMMU On + F&S]**
Please re-use the Figure 2 results for Linux and Linux + IOMMU On configurations. Follow (link instruction) to change the kernel to F&S and enable the IOMMU before running the command below.
```bash
./flows_exp.sh
```

#### Figure 6 - Varying Ring Buffer Size
**[Linux + IOMMU On + F&S]**

Please re-use the Figure 3 results for Linux and Linux + IOMMU On configurations. 
```bash
./ringbuffer_exp.sh
```

#### Figure 7 - Latency
**[Linux, Linux + IOMMU On, Linux + IOMMU On + F&S]**
```bash
./latency_fig7.sh
```

### Figure 8 - hostCC
**IOMMU Off results**
For figure 8a, run the following with **[Linux]** (IOMMU Off):
```bash
./no_hcc_fig8.sh
./hcc_fig8.sh
```
**IOMMU On results**
For figure 8b run the following: [Note: the required kernel configuration is specified in bold next to the bar label]
Linux (red bar) **[Linux + IOMMU On]**
```bash
./no_hcc_fig8.sh
```
Linux + hostCC (pink bar) **[Linux + IOMMU On]**
```
./hcc_fig8.sh
```
Linux + hostCC + F&S (green bar) **[Linux + IOMMU On + F&S]**
```
./hcc_fig8.sh
```

### Figure 9 - F&S Performance Breakdown
For this experiment, we provide an additional kernel that only implements one of the F&S key ideas: preserving page table caches during IOTLB invalidations. Please follow the instructions to boot into it. 

Edit `/etc/default/grub` to boot with Linux 6.0.3 + Preserve as default. Comment all `GRUB_DEFAULT=` lines except for the 6.0.3preserve+ version. For example:
```bash
#GRUB_DEFAULT="1>Ubuntu, with Linux 3.4.5"
GRUB_DEFAULT="1>Ubuntu, with Linux 6.0.3preserve+"
#GRUB_DEFAULT="1>Ubuntu, with Linux 5.4.3"
```
At the bottom of the `/etc/default/grub` file, make sure the kernel command line enables the IOMMU in strict mode:
```bash
GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on iommu.strict=1"
#GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=off"
```
Reboot the machine and confirm that the correct kernel is being used and that the IOMMU is enabled in strict mode
```bash
uname -r
dmesg | grep -i "iommu"
```

```bash
./ringbuffer_exp.sh
```