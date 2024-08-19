# SOSP 2024 Artifact Evaluation

## Hardware Configuration
(list hardware details from paper)

**[NOTE]:** We have provided our setup to use by artifact evaluators, so you may skip the (link setup instructions) and jump right to the section below on running experiments.

## Running Experiments
Make sure that each experiment downs and then ups the interface to reset. 

Many experiments require the same scripts to be run with different kernels and IOMMU configurations: Linux, Linux + IOMMU On, Linux + IOMMU On + F&S. We have included which configurations are required for each figure (e.g. **[Linux, Linux + IOMMU On]** or **[Linux, Linux + IOMMU On, Linux + IOMMU On + F&S]**). Instructions for booting into the correct kernel configuration are below. To save time, we recommend running all the scripts before changing the configuration rather than changing the configuration for each figure. 

#### Loading different kernel configurations
*put instructions for setting iommu on/off and selecting the right kernel. Put real lines of code to make it easy*
**Linux (IOMMU Off):**
**Linux + IOMMU On:**
**Linux + IOMMU On + F&S:**

### Detailed Instructions 
Now we provide how to use our scripts to reproduce the results in the paper.

I also need a python utility that will print each of the parts I use for the figure. So throughput, IOTLB and page table cache misses per page, etc. It shouold operate on the final report csv, so that they can use as many runs as they want. 

Figures to figure out:
* partial solution figures
* hostCC figures
* latency figure


#### Figure 2
**[Linux, Linux + IOMMU On]**
Instructions to use the right linux kernel and turn off IOMMU

script that will run all the run-dctcp for flows (in same sosp-experiments directory)
run utility that will read out all the values for each of (a), (b), (c), (d), (e). Except for the IOVA locality, since that's not part of the script and was a separate logging I did that shouldn't be used in production in testing


####  Figure 3
*for each of the 3 configurations below*
same script that runs run-dctcp for ring buffer
then run same utility that gets it from reports


#### Fiure 5
**[Linux + IOMMU On + F&S]**
**[Note]:** Please re-use the Figure 2 results for Linux and Linux + IOMMU On configurations. 

reminder of instructions to boot into the F&S Kernel
and then run the same flows script and printing utility

#### Figure 6
Reuse IOMMU On and IOMMU Off results
### IOMMU On + F&S
instructions to boot into the F&S Kernel
and then run the same ring buffer script and printing utility


#### Figure 7
**[Linux, Linux + IOMMU On, Linux + IOMMU On + F&S]**
Need to figure this one out

## Running HostCC
instructions for running hostcc... (included in the script but just explain). Make sure it removes the hostCC module after 

#### Figure 8

## F&S Performance Breakdown
instructions for other kernels. Make sure to keep IOMMU On.

#### Figure 9
jsut run the same ring buffer 