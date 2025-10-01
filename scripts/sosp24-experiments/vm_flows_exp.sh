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

GUEST_INTF="enp0s1np0"
GUEST_IP="192.168.100.11"
GUEST_NIC_BUS="0x0"
GUEST_HOME="/home/schai"
# for some reason, public domain name doesn't work
HOST_IP="192.17.101.97"
HOST_HOME="/home/lbalara"
CLIENT_HOME="/home/siyuanc3"
CLIENT_INTF="ens5008np0"
CLIENT_IP="192.168.100.3"
CLIENT_SSH_UNAME="siyuanc3"
CLIENT_SSH_HOST="nexus03.csl.illinois.edu" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=0 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/home/schai/.ssh/id_rsa"

# off, shadow or nested
VIRT_TECH="nested"

function verify_virt_tech() {
    local tech="$1"
    # Check if we can connect to virsh

    # bash -l -c is required here to load the right env
    virsh_out=$(ssh -i "$CLIENT_SSH_IDENTITY_FILE" "${HOST_UNAME}@${HOST_IP}" 'bash -l -c "virsh list --all"')
    running_vms=$(echo "$virsh_out" | grep running | awk '{print $2}')
    # running_vms=$(ssh -i "$CLIENT_SSH_IDENTITY_FILE" "${HOST_UNAME}@${HOST_IP}" "bash -c 'virsh list --all | grep running'")
    
    if [ -z "$running_vms" ]; then
        echo "No VMs are currently running"
        exit 1
    else
        echo "Found running VMs: $running_vms"
    fi

    if [[ "$running_vms" == *"$tech"* ]]; then
        echo "Matched: VMname=$running_vms and virt_tech=$tech"
    else
        echo "ERROR Inconsistent virtualization tech: $running_vms and $tech"
        exit 1
    fi
}

verify_virt_tech $VIRT_TECH

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
    iommu_config="host-strict-guest-on-$VIRT_TECH"
fi

# pause the frame
sudo ethtool --pause $GUEST_INTF tx off rx off
$SSH_CLIENT_CMD "sudo ethtool --pause $CLIENT_INTF tx off rx off"
$SSH_CLIENT_CMD "echo off | sudo tee /sys/devices/system/cpu/smt/control"

sleep 1

client_cores="32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63"
server_cores="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31"

num_cores=20
client_cores_mask=($(echo $client_cores | tr ',' '\n' | shuf -n $num_cores | tr '\n' ','))
server_cores_mask=($(echo $server_cores | tr ',' '\n' | shuf -n $num_cores | tr '\n' ','))

timestamp=$(date '+%Y-%m-%d-%H-%M-%S')
# 5 10 20 40
for socket_buf in 1; do
    for ring_buffer in 512; do
    # 5 10 20 40
        for i in 20; do
            format_i=$(printf "%02d\n" $i)
            exp_name="${timestamp}-$(uname -r)-flow${format_i}-${iommu_config}-ringbuf-${ring_buffer}_sokcetbuf${socket_buf}_${num_cores}cores"
            echo $exp_name

            if [ "$DRY_RUN" -eq 1 ]; then
                continue
            fi

            sudo bash vm-run-dctcp-tput-experiment.sh \
            --guest-home "$GUEST_HOME" --guest-ip "$GUEST_IP" --guest-intf "$GUEST_INTF" --guest-bus "$GUEST_NIC_BUS" -n "$i" -c $server_cores_mask \
            --client-home "$CLIENT_HOME" --client-ip "$CLIENT_IP" --client-intf "$CLIENT_INTF" -N "$i" -C $client_cores_mask \
            --host-home "$HOST_HOME" --host-ip "$HOST_IP" \
            --client-ssh-name "$CLIENT_SSH_UNAME" --client-ssh-pass "$CLIENT_SSH_PASSWORD" --client-ssh-host "$CLIENT_SSH_HOST" --client-ssh-use-pass "$CLIENT_USE_PASS_AUTH" --client-ssh-ifile "$CLIENT_SSH_IDENTITY_FILE" \
            -e "$exp_name" -m 4000 -r $ring_buffer -b "100g" -d 1\
            --socket-buf $socket_buf --mlc-cores 'none' --runs 1

            # > /dev/null 2>&1
            #sudo bash run-dctcp-tput-experiment.sh -E $exp_name -M 4000 --num_servers $i --num_clients $i -c "4" -m "20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf $server_intf --client_intf $client_intf    
            python3 report-tput-metrics.py $exp_name tput,drops,acks,iommu,cpu | sudo tee ../utils/reports/$exp_name/summary.txt
            echo $PWD
            cd ../utils/reports/$exp_name

            sudo bash -c "cat /sys/kernel/debug/tracing/trace > iova.log"

            cd -
            sudo chmod +666 -R ../utils/reports/$exp_name

            # python sosp24-experiments/plot_iova_logging.py \
            #     --exp_folder "../utils/reports/$exp_name" \
            #     --log_file "iova.log"
        done
    done
done 
