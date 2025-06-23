#!/bin/bash
cd ..
echo "Running flow experiment... this may take a few minutes"

GUEST_INTF="enp0s1np0"
GUEST_IP="10.10.1.1"
GUEST_NIC_BUS="0x00"
GUEST_HOME="/home/schai"
HOST_IP="192.168.122.1"
HOST_INTF="virbr0"
HOST_HOME="/users/Leshna"
CLIENT_HOME="/users/Leshna"
CLIENT_INTF="enp23s0f0np0"
CLIENT_IP="10.10.1.2"
CLIENT_SSH_UNAME="Leshna"
CLIENT_SSH_HOST="128.110.220.29" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=0 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/home/schai/.ssh/id_ed25519"

if [ "$CLIENT_USE_PASS_AUTH" -eq 1 ]; then
	SSH_CLIENT_CMD="sshpass -p $CLIENT_SSH_PASSWORD ssh ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
else
	SSH_CLIENT_CMD="ssh -i $CLIENT_SSH_IDENTITY_FILE ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
fi

iommu_on=$(grep -o intel_iommu=on /proc/cmdline)
iommu_config=""
if [ -z $iommu_on ]; then
    iommu_config="host-strict-guest-off"
else
    iommu_config="host-strict-guest-on"
fi

# pause the frame
sudo ethtool --pause $GUEST_INTF tx off rx off
$SSH_CLIENT_CMD "sudo ethtool --pause $CLIENT_INTF tx off rx off"

sleep 1

timestamp=$(date '+%H-%M_%m-%d')
# 5 10 20 40
for i in 5; do
    format_i=$(printf "%02d\n" $i)
    exp_name="${timestamp}-$(uname -r)-flow${format_i}-${iommu_config}"
    echo $exp_name

    sudo bash vm-run-dctcp-tput-experiment.sh \
    --guest-home "$GUEST_HOME" --guest-ip "$GUEST_IP" --guest-intf "$GUEST_INTF" --guest-bus "$GUEST_NIC_BUS" -n "$i" -c "0,1,2,3,4" \
    --client-home "$CLIENT_HOME" --client-ip "$CLIENT_IP" --client-intf "$CLIENT_INTF" -N "$i" -C "4,8,12,16,20" \
    --host-home "$HOST_HOME" --host-ip "$HOST_IP" --host-intf "$HOST_INTF" \
    -e "$exp_name" -m 4000 -r 256 -b "100g" -d 1\
    --socket-buf 1 --mlc-cores 'none' --runs 1

    # > /dev/null 2>&1
    #sudo bash run-dctcp-tput-experiment.sh -E $exp_name -M 4000 --num_servers $i --num_clients $i -c "4" -m "20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf $server_intf --client_intf $client_intf    
    python3 report-tput-metrics.py $exp_name tput,drops,acks,iommu,cpu
    echo $PWD
    cd ../utils/reports/$exp_name

    sudo bash -c "cat /sys/kernel/debug/tracing/trace > iova.log"

    cd -
    sudo chmod +666 -R ../utils/reports/$exp_name

    # python sosp24-experiments/plot_iova_logging.py \
    #     --exp_folder "../utils/reports/$exp_name" \
    #     --log_file "iova.log"

done

