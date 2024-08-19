# F&S: Fast & Safe IO Memory Proction for Networked Systems
quick blurb...

## 1. Overview
### Repository overview
- f&s.patch Kernel patch for applying F&S
- *utils/* contains tools to re-create IOMMU congestion scenarios and to log IOMMU, CPU and app level performance...
- *scripts/* contains scripts to run the experiments in the SOSP'24 paper. 

Replace src/ with fands.patch

### System overview
For simplicity, we assume that users have two physical servers (Host and Target) connected with each other over networks. The target server enables IOMMU, etc...

## Artifact Evaluation Instructions
To keep things convenient for artifact evaluators for SOSP'24, we have provided a setup on our servers with the F&S Kernel already installed. Please refer to (put the scripts/sosp-artifact path read me) for instructions on running the experiments for the results in the paper.  

### Getting Started Guide
Through the following three sections, we provide getting started instructions to install blk-switch and to run experiments.

   - **Build blk-switch Kernel (10 human-mins + 30 compute-mins + 5 reboot-mins):**  
blk-switch is currently implemented in the core part of Linux kernel storage stack (blk-mq at block device layer), so it requires kernel compilation and system reboot into the blk-switch kernel. This section covers how to build the blk-switch kernel and i10/nvme-tcp kernel modules. 
   - **Setup Remote Storage Devices (5 human-mins):**  
This section covers how to setup remote storage devices using i10/nvme-tcp kernel modules.
   - **Run Toy-experiments (5-10 compute-mins):**  
This section covers how to run experiments with the blk-switch kernel. 

The detailed instructions to reproduce all individual results presented in our OSDI21 paper is provided in the "[osdi21_artifact](https://github.com/resource-disaggregation/blk-switch/tree/master/osdi21_artifact)" directory.

## 2. Build F&S Kernel (with root)
blk-switch has been successfully tested on Ubuntu 16.04 LTS with kernel 5.4.43. Building the blk-switch kernel should be done on both Host and Target servers.

**(Don't forget to be root)**
1. Download Linux kernel source tree:
   ```
   sudo -s
   cd ~
   wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.4.43.tar.gz
   tar xzvf linux-5.4.43.tar.gz
   ```

2. Apply the F&S patch

   ```
   git clone https://github.com/resource-disaggregation/blk-switch.git
   cd blk-switch
   cp -rf block drivers include ~/linux-5.4.43/
   cd ~/linux-5.4.43/
   ```

3. Update kernel configuration:

   ```
   cp /boot/config-x.x.x .config
   make olddefconfig
   ```
   "x.x.x" is a kernel version. It can be your current kernel version or latest version your system has. Type "uname -r" to see your current kernel version.  
 
   Edit ".config" file to include your name in the kernel version.
   ```
   vi .config
   (in the file)
   ...
   CONFIG_LOCALVERSION="-fands"
   ...
   ```
   Save the .config file and exit.   

4. Make sure i10 and nvme-tcp modules are included in the kernel configuration:

   ```
   make menuconfig

   - Device Drivers ---> NVME Support ---> <M> NVM Express over Fabrics TCP host driver
   - Device Drivers ---> NVME Support ---> <M>   NVMe over Fabrics TCP target support
   - Device Drivers ---> NVME Support ---> <M> i10: A New Remote Storage I/O Stack (host)
   - Device Drivers ---> NVME Support ---> <M> i10: A New Remote Storage I/O Stack (target)
   ```
   Press "Save" and "Exit"

5. Compile and install:

   ```
   (See NOTE below for '-j24')
   make -j24 bzImage
   make -j24 modules
   make modules_install
   make install
   ```
   NOTE: The number 24 means the number of threads created for compilation. Set it to be the total number of cores of your system to reduce the compilation time. Type "lscpu | grep 'CPU(s)'" to see the total number of cores:
   
   ```
   CPU(s):                24
   On-line CPU(s) list:   0-23
   ```

6. Edit "/etc/default/grub" to boot with your new kernel by default. For example:

   ```
   ...
   #GRUB_DEFAULT=0 
   GRUB_DEFAULT="1>Ubuntu, with Linux 5.4.43-jaehyun"
   ...
   ```

7. Update the grub configuration and reboot into the new kernel.

   ```
   update-grub && reboot
   ```

8. Do the same steps 1--7 for both Host and Target servers.

9. When systems are rebooted, check the kernel version: Type "uname -r". It should be "5.4.43-(your name)".

### Running hostCC

One can run hostCC by simply loading the kernel module from within the src/ directory
```
sudo insmod hostcc-module.ko
```
hostCC can also take any user-specified values for IIO occupancy and PCIe bandwidth thresholds (I_T and B_T used in the [paper](https://www.cs.cornell.edu/~ragarwal/pubs/hostcc.pdf)) as command line input. More details provided in the README inside the src/ directory. 

To stop running hostCC simply unload the module
```
sudo rmmod hostcc-module
```

### Installing required utilities

Instructions to install required set of benchmarking applications and measurement tools (for running similar experiments in SIGCOMM'23 paper) is provided in the README in in *utils/* directory. 
+ Benchmarking applications: We use **iperf3** as network app generating throughput-bound traffic, **netperf** as network app generating latency-sensitive traffic, and **mlc** as the CPU app generating memory-intensive traffic.
+ Measurement tools: We use **Intel PCM** for measuring the host-level metrics and **Intel Memory Bandwidth Allocation** tool for performing host-local response. We also use **sar** utility to measure CPU utilization.

### Specifying desired experimental settings

Desired experiment settings, for eg., enabling DDIO, configuring MTU size, number of clients/servers used by the network-bound app, enabling TCP optimizations like TSO/GRO/aRFS (currently TCP optimizations can be configured using the provided script in this repo only for Mellanox CX5 NICs), etc can tuned using the script *utils/setup-envir.sh*. Run the script with -h flag to get list of all parameters, and their default values.  
```
sudo bash utils/setup-envir.sh -h
```



### Running benchmarking experiments

To help run experiments similar to those in SIGCOMM'23 paper, we provide following scripts in the *scripts/* directory:

+ *run-hostcc-tput-experiment.sh*
+ *run-hostcc-latency-experiment.sh*

Run these scripts with -h flag to get list of all possible input parameters, including specifying the home directory (which is assumed to contain hostCC repo), client/server IP addresses, experimental settings as discussed above. The output results are generated in *utils/reports/* directory, and measurement logs are stored in *utils/logs/*.


## Reproducing results in the [SIGCOMM'23 paper](www.google.com)

For ease of use, we also provide wrapper scripts inside the *scripts/SIGCOMM23-experiments* directory which run identical experiments as in the SIGCOMM'23 paper in order to reproduce our key evaluation results. Refer the README in *scripts/SIGCOMM23-experiments/* directory for details on how to run the scripts. 


### Factors affecting reproducibality of results
The results are sensitive to the setup, and any difference in the setup for following factors may lead to results different from the paper. A list of potential factors:
+ Processor: Number of NUMA nodes, whether hyperthreading is enabled, whether hardware prefetching is enabled, L1/L2/LLC sizes, CPU clock frequency, etc
+ Memory: DRAM generation (DDR3/DDR4/DDR5), DRAM frequency, number of DRAM channels per NUMA node
+ Network: NIC hardware (for eg., Mellanox CX5), NIC driver (for eg., OFED version for Mellanox NICs), MTU size
+ Topology: minimum RTT between the servers
+ Optimizations: whether Linux network stack optimizations like TSO/GRO/aRFS are enabed
+ DCTCP parameters: Tx/Rx socket buffer sizes, DCTCP alpha, whether delayed ACKs is enabled
+ Add more things I know of like MTU, ring buffer, etc. 

The scripts provided in *scripts/sosp24-experiments/* automatically set the Linux network stack optimizations and (say which parameters it does set) to be the same as in the F&S evaluation in our SOSP'24 paper. 


## Current limitations, and planned extensions

**IOMMU Interface** The current IOMMU DMA Mapping interface does not allow for the separation of IOVA allocation and DMA mapping and DMA unmapping. This means there is no way to allocate IOVAs at a different granularity than the DMA mapping and to DMA unmap at a different granularity than DMA mapping. We work around this interface to implement F&S and leave it as future work to redesign the interface to allow for F&S contiguous IOVA allocation.

**Additional hardware and driver support.** Current repo only includes support for the setup described in (paper). We plan to add support for additional Intel /AMD architectures.

