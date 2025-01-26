#!/bin/bash


# enp202s0f0np0 on numa node 1
# associated CPUs are 1,3,5,7,9,11,13,15 ...

# Turn off Hyper threading
echo "Server: $client"

echo off | sudo tee /sys/devices/system/cpu/smt/control
cat /proc/cmdline


sleep 5

server=10.10.1.2
client=10.10.1.1
home=/users/schai

echo "Client: $client"
ssh -i $home/.ssh/id_rsa schai@$client "echo off | sudo tee /sys/devices/system/cpu/smt/control"
ssh -i $home/.ssh/id_rsa schai@$client "cat /proc/cmdline"

# 2 4 5 10 20 40
for number in 5; do
    format_number=$(printf "%02d" $number)
    echo $number
    sudo scripts/run-dctcp-tput-experiment.sh --home /users/schai \
    --server $server \
    --server_intf enp202s0f0np0 \
    --num_servers $number \
    --client $client \
    --client_intf enp202s0f0np0 \
    --num_clients $number \
    --exp siyuan-$(uname -r)-server-off-client-on-$format_number-flows \
    --cpu_mask 1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31 \
    --num_runs 5
    sleep 10
done
