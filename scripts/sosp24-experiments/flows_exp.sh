#!/bin/bash
cd ..
echo "Running flow experiment... this may take a few minutes"

SERVER_HOME="/home/saksham"
SERVER_IP="192.168.11.126"
SERVER_INTF="enp101s0f1np1"
SERVER_BUS="0x65"
CLIENT_HOME="/home/saksham"
CLIENT_INTF="ens2f1np1"
CLIENT_IP="192.168.11.125"
CLIENT_SSH_UNAME="saksham"
CLIENT_SSH_HOST="genie12.cs.cornell.edu" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=1 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/home/schai/.ssh/id_ed25519"


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
$SSH_CLIENT_CMD "sudo ethtool --pause $CLIENT_INTF tx off rx off"

sleep 10

timestamp=$(date '+%H-%M_%m-%d')
# 5 10 20 40
for i in 5 10 ; do
    format_i=$(printf "%02d\n" $i)
    exp_name="${timestamp}-$(uname -r)-flow${format_i}-${iommu_config}"
    echo $exp_name
    sudo bash run-dctcp-tput-experiment.sh \
    --server-home "$SERVER_HOME" --server-ip "$SERVER_IP" --server-intf "$SERVER_INTF" -n "$i" -c "0,2,4,6,8" --server-bus "$SERVER_BUS" \
    --client-home "$CLIENT_HOME" --client-ip "$CLIENT_IP" --client-intf "$CLIENT_INTF" -N "$i" -C "4,8,12,16,20" \
    --client-ssh-name "$CLIENT_SSH_UNAME" --client-ssh-pass "$CLIENT_SSH_PASSWORD" --client-ssh-host "$CLIENT_SSH_HOST" --client-ssh-use-pass "$CLIENT_USE_PASS_AUTH" --client-ssh-ifile "$CLIENT_SSH_IDENTITY_FILE" \
    -e "$exp_name" -m 4000 -r 256 -b "100g" -d 1 \
    --socket-buf 1 --mlc-cores 'none' --runs 1

    python3 report-tput-metrics.py $exp_name tput,drops,acks,iommu,cpu
    cd ../utils/reports/$exp_name

    sudo bash -c "cat /sys/kernel/debug/tracing/trace > iova.log"
    # sudo bash -c "rg iperf3 iova.log > iperf_iova.log"
    # sudo bash -c "rg 'core: 16' iova.log > iperf_iova_core16.log"
    # sudo bash -c "rg core iova.log > core_iova.log"

    cd -
    sudo chmod +666 -R ../utils/reports/$exp_name
done
