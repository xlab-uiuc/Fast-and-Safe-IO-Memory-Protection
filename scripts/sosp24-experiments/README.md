## Reproducing SIGCOMM'23 Results
*Put an instruction for each figure. Go one by one through the submission and then figure out which script*. I also need a python utility that will print each of the parts I use for the figure. So throughput, IOTLB and page table cache misses per page, etc. 

things to figure out:
* partial solution figures
* hostCC figures
* latency figure

## Figure 2
### IOMMU Off instructions
Instructions to use the right linux kernel and turn off IOMMU

script that will run all the run-dctcp for flows (in same sosp-experiments directory)
run utility that will read out all the values for each of (a), (b), (c), (d), (e). Except for the IOVA locality, since that's not part of the script and was a separate logging I did that shouldn't be used in production in testing

### IOMMU On instructions

## Figure 3
*for each of the 3 configurations below*
same script that runs run-dctcp for ring buffer
then run same utility that gets it from reports

### IOMMU Off
### IOMMU On

## Figure 5
Reuse IOMMU On and IOMMU Off results
### IOMMU On + F&S
instructions to boot into the F&S Kernel
and then run the same flows script and printing utility

## Figure 6
Reuse IOMMU On and IOMMU Off results
### IOMMU On + F&S
instructions to boot into the F&S Kernel
and then run the same ring buffer script and printing utility



