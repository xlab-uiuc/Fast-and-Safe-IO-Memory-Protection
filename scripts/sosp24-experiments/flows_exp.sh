#!/bin/bash
cd ..
echo "Running flow experiment... this may take a few minutes"

# Add dry run flag
DRY_RUN=0

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --dry)
        DRY_RUN=1
        shift # past argument
        ;;
        *)
        shift # past unknown argument
        ;;
    esac
done

SERVER_HOME="/home/siyuanc3/"
SERVER_IP="192.168.100.1"
SERVER_INTF="ens1np0"
SERVER_BUS="0x98"
CLIENT_HOME="/home/siyuanc3"
CLIENT_INTF="ens5008np0"
CLIENT_IP="192.168.100.3"
CLIENT_SSH_UNAME="siyuanc3"
CLIENT_SSH_HOST="nexus03.csl.illinois.edu" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=0 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/home/siyuanc3/.ssh/id_rsa"


## THINGS TO MANUALLY CHANGE NIC_BUS IN SETUP-ENVIR IN CLIENT

if [ "$CLIENT_USE_PASS_AUTH" -eq 1 ]; then
	SSH_CLIENT_CMD="sshpass -p $CLIENT_SSH_PASSWORD ssh ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
else
	SSH_CLIENT_CMD="ssh -i $CLIENT_SSH_IDENTITY_FILE ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
fi

iommu_on=$(grep -o intel_iommu=on /proc/cmdline)
iommu_config=""
if [ -z $iommu_on ]; then
    iommu_config="iommu-off"
else
    iommu_config="iommu-on"
fi

# pause the frame
sudo ethtool --pause $SERVER_INTF tx off rx off
echo off | sudo tee /sys/devices/system/cpu/smt/control
$SSH_CLIENT_CMD "sudo ethtool --pause $CLIENT_INTF tx off rx off"
$SSH_CLIENT_CMD "echo off | sudo tee /sys/devices/system/cpu/smt/control"

sleep 3

client_cores="32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63"
server_cores="64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95"

num_cores=20
client_cores_mask=($(echo $client_cores | tr ',' '\n' | shuf -n $num_cores | tr '\n' ','))
server_cores_mask=($(echo $server_cores | tr ',' '\n' | shuf -n $num_cores | tr '\n' ','))


timestamp=$(date '+%Y-%m-%d-%H-%M-%S')
for socket_buf in 1; do
    for ring_buffer in 512; do
    # 5 10 20 40
        for i in 20 40 60 80 160; do
            format_i=$(printf "%02d\n" $i)
            exp_name="${timestamp}-$(uname -r)-flow${format_i}-${iommu_config}-ringbuf-${ring_buffer}_sokcetbuf${socket_buf}_${num_cores}cores"
            echo $exp_name

            if [ "$DRY_RUN" -eq 1 ]; then
                continue
            fi

            # Client setup: ens5008np0 interface is device bf:00.0 which is attached to NUMANode L#1
            # CPU core 32 33 34 35 36 37 38 39 40 are always on NUMANode L#1
            # Host setup: ens1np0 interface is device 98:00.0 which is attached to NUMANode L#2
            # 64 65 66 67 68 69 are on NUMANode L#2
            sudo bash run-dctcp-tput-experiment.sh \
            --server-home "$SERVER_HOME" --server-ip "$SERVER_IP" --server-intf "$SERVER_INTF" -n "$i" -c $server_cores_mask --server-bus "$SERVER_BUS" \
            --client-home "$CLIENT_HOME" --client-ip "$CLIENT_IP" --client-intf "$CLIENT_INTF" -N "$i" -C $client_cores_mask \
            --client-ssh-name "$CLIENT_SSH_UNAME" --client-ssh-pass "$CLIENT_SSH_PASSWORD" --client-ssh-host "$CLIENT_SSH_HOST" --client-ssh-use-pass "$CLIENT_USE_PASS_AUTH" --client-ssh-ifile "$CLIENT_SSH_IDENTITY_FILE" \
            -e "$exp_name" -m 4000 -r $ring_buffer -b "100g" -d 1 \
            --socket-buf $socket_buf --mlc-cores 'none' --runs 1

            python3 report-tput-metrics.py $exp_name tput,drops,acks,iommu,cpu | sudo tee ../utils/reports/$exp_name/summary.txt
            # cd ../utils/reports/$exp_name

            # sudo bash -c "cat /sys/kernel/debug/tracing/trace > iova.log"
            # sudo bash -c "rg iperf3 iova.log > iperf_iova.log"
            # sudo bash -c "rg 'core: 16' iova.log > iperf_iova_core16.log"
            # sudo bash -c "rg core iova.log > core_iova.log"

            # cd -
            # sudo chmod +666 -R ../utils/reports/$exp_name
            sleep 2
        done
    done
done 