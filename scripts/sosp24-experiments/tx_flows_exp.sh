#!/bin/bash
# Ensure we are in the scripts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Assuming the script is in scripts/sosp24-experiments/
# We want to go to scripts/
cd "$SCRIPT_DIR/.." || exit 1
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


# for some reason, public domain name doesn't work
HOST_IP="192.168.101.111"
HOST_UNAME="lbalara"
HOST_HOME="/home/lbalara"
HOST_INTF="ens1np0"
HOST_NIC_BUS="0x98"
CLIENT_HOME="/home/siyuanc3"
CLIENT_INTF="ens1006np0"
CLIENT_IP="192.168.101.3"
CLIENT_SSH_UNAME="siyuanc3"
CLIENT_SSH_HOST="nexus03.csl.illinois.edu" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=0 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/home/lbalara/.ssh/id_rsa"

parse_iommu_mode() {
	local cmdline="${1:-$(</proc/cmdline)}"
	local cl
	cl="$(printf '%s' "$cmdline" | tr '[:upper:]' '[:lower:]')"

	# Passthrough (separate case)
	if [[ "$cl" =~ (^|[[:space:]])(iommu=pt|iommu\.passthrough=(1|on|y|yes|true))($|[[:space:]]) ]]; then
		echo passthrough
		return
	fi

	# Off
	if [[ "$cl" =~ (^|[[:space:]])(noiommu|iommu=off|intel_iommu=off|amd_iommu=off)($|[[:space:]]) ]]; then
		echo off
		return
	fi

	# Strict
	if [[ "$cl" =~ (^|[[:space:]])iommu\.strict=(1|on|y|yes|true)($|[[:space:]]) ]] || \
	   [[ "$cl" =~ (^|[[:space:]])intel_iommu=([^[:space:]]*,)?strict([^[:space:]]*)($|[[:space:]]) ]] || \
	   [[ "$cl" =~ (^|[[:space:]])amd_iommu=([^[:space:]]*,)?strict([^[:space:]]*)($|[[:space:]]) ]]; then
		echo strict
		return
	fi

	# Lazy (non-strict)
	if [[ "$cl" =~ (^|[[:space:]])iommu\.strict=(0|off|n|no|false)($|[[:space:]]) ]] || \
	   [[ "$cl" =~ (^|[[:space:]])intel_iommu=([^[:space:]]*,)?nonstrict([^[:space:]]*)($|[[:space:]]) ]] || \
	   [[ "$cl" =~ (^|[[:space:]])amd_iommu=([^[:space:]]*,)?nonstrict([^[:space:]]*)($|[[:space:]]) ]]; then
		echo lazy
		return
	fi

	# Explicitly enabled but no strictness specified → assume strict
	if [[ "$cl" =~ (^|[[:space:]])(iommu=on|intel_iommu=on|amd_iommu=on)($|[[:space:]]) ]]; then
		echo strict
		return
	fi

	# Default if unspecified
	echo strict
}

if [ "$CLIENT_USE_PASS_AUTH" -eq 1 ]; then
	SSH_CLIENT_CMD="sshpass -p $CLIENT_SSH_PASSWORD ssh ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
else
	SSH_CLIENT_CMD="ssh -i $CLIENT_SSH_IDENTITY_FILE ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
fi


host_cmdline=$(cat /proc/cmdline)
host_iommu_config=$(parse_iommu_mode "$host_cmdline")

iommu_config="baremetal-${host_iommu_config}"
echo "iommu_config: $iommu_config"

# pause the frame
sudo ethtool --pause $HOST_INTF tx off rx off
echo off | sudo tee /sys/devices/system/cpu/smt/control
$SSH_CLIENT_CMD "sudo ethtool --pause $CLIENT_INTF tx off rx off"
$SSH_CLIENT_CMD "echo off | sudo tee /sys/devices/system/cpu/smt/control"

sleep 3


client_cores="0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31"
server_cores="64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95"

timestamp=$(date '+%Y-%m-%d-%H-%M-%S')

N_RUNS=1

for socket_buf in 1; do
    for ring_buffer in 512; do
        for i in 1; do
            # for num_cores in 1 4 8 12 16 20 24; do
            for num_cores in 12; do
                client_cores_mask=($(echo $client_cores | tr ',' '\n' | head -n $num_cores | tr '\n' ','))
                server_cores_mask=($(echo $server_cores | tr ',' '\n' | head -n $num_cores | tr '\n' ','))

                n_val=$(( i * num_cores ))
                # echo $n_val
                format_i=$(printf "%02d\n" $n_val)

                exp_name="${timestamp}-$(uname -r)-BM-TX-flow${format_i}-${iommu_config}-${num_cores}cores-ringbuf${ring_buffer}-sockbuf${socket_buf}"
                echo $exp_name
                echo "Running $exp_name" "N_RUN=$N_RUNS"

                if [ "$DRY_RUN" -eq 1 ]; then
                  continue
                fi

                sudo mkdir -p ../utils/reports/$exp_name
                sudo bash tx-run-dctcp-tput-experiment.sh \
                    --host-home "$HOST_HOME" --host-ip "$HOST_IP" --host-intf "$HOST_INTF" --host-bus "$HOST_NIC_BUS" -n "$n_val" -c $server_cores_mask \
                    --client-home "$CLIENT_HOME" --client-ip "$CLIENT_IP" --client-intf "$CLIENT_INTF" -N "$n_val" -C $client_cores_mask \
                    --client-ssh-name "$CLIENT_SSH_UNAME" --client-ssh-pass "$CLIENT_SSH_PASSWORD" --client-ssh-host "$CLIENT_SSH_HOST" --client-ssh-use-pass "$CLIENT_USE_PASS_AUTH" --client-ssh-ifile "$CLIENT_SSH_IDENTITY_FILE" \
                    -e "$exp_name" -m 4000 -r $ring_buffer -b "400g" -d 1\
                    --socket-buf $socket_buf --mlc-cores 'none' --runs $N_RUNS 2>&1 | sudo tee ../utils/reports/$exp_name/experiment.log

                  python3 report-tput-metrics.py $exp_name tput,drops,acks,iommu,cpu | sudo tee ../utils/reports/$exp_name/summary.txt
                  echo $PWD
                  cd ../utils/reports/$exp_name

                  cd -
                  sudo chmod +666 -R ../utils/reports/$exp_name      
            done
        done
    done
done

sync
sleep 1
