#!/bin/bash


# enp202s0f0np0 on numa node 1
# associated CPUs are 1,3,5,7,9,11,13,15 ...
sudo scripts/run-dctcp-tput-experiment.sh --home $(realpath ~) \
    --server 10.10.1.2 \
    --server_intf enp202s0f0np0 \
    --num_servers 1 \
    --client 10.10.1.1 \
    --client_intf enp202s0f0np0 \
    --num_clients 1 \
    --exp siyuan-iommu-off \
    --cpu_mask 1,3,5,7,9,11,13,15 \