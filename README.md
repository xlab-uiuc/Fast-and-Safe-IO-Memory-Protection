# F&S: Fast & Safe IO Memory Proction for Networked Systems
quick blurb...

## 1. Overview
### Repository overview
- *fands_kernel/* contains the F&S Kernel
- *utils/* contains tools to re-create IOMMU congestion scenarios and to log IOMMU, CPU and app level performance...
- *scripts/* contains scripts to run the experiments in the SOSP'24 paper. 

### System overview
For simplicity, we assume that users have two physical servers (Host and Target) connected with each other over networks. Target server has actual storage devices (e.g., RAM block device, NVMe SSD, etc.), and Host server accesses the Target-side storage devices via the remote storage stack (e.g., i10, nvme-tcp) over the networks. Then Host server runs latency-sensitive applications (L-apps) and throughput-bound applications (T-apps) using standard I/O APIs (e.g., Linux AIO). Meanwhile, blk-switch plays a role for providing μs-latency and high throughput at the kernel block device layer.

For simplicity, we assume that users have two physical servers (Host and Target) connected with each other over networks. The target server enables IOMMU, etc...

## Artifact Evaluation Instructions
To keep things convenient for artifact evaluators for SOSP'24, we have provided a setup on our servers with the F&S Kernel already installed. Thus artifact evaluators can skip the **Getting Started Guide** (link on github to the right place). Please refer to (scripts/sosp-artifact link) for instructions on running the experiments for the results in the paper.  

## 2. Getting Started Guide
The following sections provide instructions for:
 * building the F&S kernel
 * booting into the kernel 
 * Installing and configuring the utilities to run benchmarks


The detailed instructions to reproduce all individual results presented in our OSDI21 paper is provided in the "[osdi21_artifact](https://github.com/resource-disaggregation/blk-switch/tree/master/osdi21_artifact)" directory.

## Build F&S Kernel (with root) (Put amount of time)
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

One can run F&S by booting into the kernel module and enabling the IOMMU. 
```
instructions to do that...
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


## 3. Reproducing results in the SOSP '24 paper. 

For ease of use, we also provide wrapper scripts inside the *scripts/SIGCOMM23-experiments* directory which run identical experiments as in the SIGCOMM'23 paper in order to reproduce our key evaluation results. Refer the README in *scripts/SIGCOMM23-experiments/* directory for details on how to run the scripts. 

