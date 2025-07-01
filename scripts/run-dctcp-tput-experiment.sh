#!/bin/bash

help()
{
    echo "Usage: run-rdma-tput-experiment
               [ -H | --home (home directory)]
               [ -S | --server (ip address of the server)]
               [ --server_intf (interface name for the server, for eg., ens2f0)]
               [ --num_servers (number of servers)]
               [ -C | --client (ip address of the client)]
               [ --client_intf (interface name for the client, for eg., ens2f0)]
               [ --num_clients (number of clients)]
               [ -E | --exp (experiment name, this name will be used to create output directories; default='rdma-test')]
               [ -M | --MTU (=256/512/1024/2048/4096; MTU size used;default=4096) ]
               [ -d | --ddio (=0/1, whether DDIO is disabled or enabled) ]
               [ -c | --cpu_mask (comma separated CPU mask to run the app on, recommended to run on NUMA node local to the NIC for maximum performance; default=0) ]
               [ -b | --bandwidth (bandwidth to send at in bits/sec)]
               [ --mlc_cores (comma separated values for MLC cores, for eg., '1,2,3' for using cores 1,2 and 3. Use 'none' to skip running MLC.) ]
               [ --ring_buffer (size of NIC Rx buffer)]
               [ --buf (TCP socket buffer size (in MB))]
               [ -h | --help  ]"
    exit 2
}

SHORT=H:,S:,C:,E:,M:,d:,c:,b:,h
LONG=home:,server:,client:,num_servers:,num_clients:,server_intf:,client_intf:,exp:,txn:,MTU:,size:,ddio:,cpu_mask:,mlc_cores:,ring_buffer:,bandwidth:,buf:,help
OPTS=$(getopt -a -n run-rdma-tput-experiment --options $SHORT --longoptions $LONG -- "$@")

VALID_ARGUMENTS=$# # Returns the count of arguments that are in short or long options

if [ "$VALID_ARGUMENTS" -eq 0 ]; then
  help
fi

eval set -- "$OPTS"

#default values
exp="benny-test"
server="10.10.1.3"
client="10.10.1.2"
server_intf="enp23s0f0np0"
client_intf="enp23s0f0np0"
num_servers=5
num_clients=5
init_port=3000
ddio=0
mtu=4000
dur=20
cpu_mask="0,4,8,12,16"
mlc_cores="none"
mlc_dur=100
ring_buffer=256
buf=1
bandwidth="100g"
num_runs=1
home="/users/Leshna"
viommu="/users/Leshna/viommu"
setup_dir=$viommu/Fast-and-Safe-IO-Memory-Protection/utils
exp_dir=$viommu/Fast-and-Safe-IO-Memory-Protection/utils/tcp
mlc_dir=$viommu/mlc/Linux
setup_dir_client=$home/Fast-and-Safe-IO-Memory-Protection/utils
exp_dir_client=$home/Fast-and-Safe-IO-Memory-Protection/utils/tcp
mlc_dir_client=$home/mlc/Linux

#echo -n "Enter SSH Username for client:"
#read uname
#echo -n "Enter SSH Address for client:"
#read addr
#echo -n "Enter SSH Password for client:"
#read -s password
CLIENT_SSH_UNAME="Leshna"
CLIENT_SSH_HOST="128.110.220.29" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=0 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/users/Leshna/.ssh/id_ed25519_wisc"


while :
do
  case "$1" in
    -H | --home )
      home="$2"
      shift 2
      ;;
    -E | --exp )
      exp="$2"
      shift 2
      ;;
    -S | --server )
      server="$2"
      shift 2
      ;;
    --num_servers )
      num_servers="$2"
      shift 2
      ;;
     --server_intf )
      server_intf="$2"
      shift 2
      ;;
    -C | --client )
      client="$2"
      shift 2
      ;;
    --num_clients )
      num_clients="$2"
      shift 2
      ;;
     --client_intf )
      client_intf="$2"
      shift 2
      ;;
    -M | --MTU )
      mtu="$2"
      shift 2
      ;;
    -d | --ddio )
      ddio="$2"
      shift 2
      ;;
    -c | --cpu_mask )
      cpu_mask="$2"
      shift 2
      ;;
    --mlc_cores )
      mlc_cores="$2"
      shift 2
      ;;
    --ring_buffer )
      ring_buffer="$2"
      shift 2
      ;;
    --buf )
      buf="$2"
      shift 2
      ;;
    -b | --bandwidth )
      bandwidth="$2"
      shift 2
      ;;
    -h | --help)
      help
      ;;
    --)
      shift;
      break
      ;;
    *)
      echo "Unexpected option: $1"
      help
      ;;
  esac
done

if [ "$CLIENT_USE_PASS_AUTH" -eq 1 ]; then
	SSH_CLIENT_CMD="sshpass -p $CLIENT_SSH_PASSWORD ssh ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
else
	SSH_CLIENT_CMD="ssh -i $CLIENT_SSH_IDENTITY_FILE ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
fi

#TODO fix this
exp_name=$exp

# Function to display the progress bar
function progress_bar() {
    local duration=$1
    local interval=$2

    for ((i = 0; i <= duration; i += interval)); do
        local progress=$((i * 100 / duration))
        local bar_length=$((progress / 2))
        local bar=$(printf "%-${bar_length}s" "=")
        printf "[%-${bar_length}s] %d%%" "$bar" "$progress"
        sleep "$interval"
        printf "\r"
    done
    printf "[%-${duration}s] %d%%\n" "$(printf "%-${duration}s" "=")" "100"
}

function cleanup() {
    sudo pkill -9 -f loaded_latency
    sudo pkill -9 -f iperf
#    rm -f $home/hostCC/utils/out.perf-folded
#    rm -f $home/hostCC/utils/perf.data
    $SSH_CLIENT_CMD 'screen -S $(screen -list | awk "/\\.client_session\t/ {print \$1}") -X quit'
    $SSH_CLIENT_CMD 'screen -S $(screen -list | awk "/\\.logging_session\t/ {print \$1}") -X quit'
    $SSH_CLIENT_CMD 'screen -wipe'
    $SSH_CLIENT_CMD 'sudo pkill -9 -f iperf'
    ## IOVA logging
    sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
    sudo echo 0 > /sys/kernel/debug/tracing/options/overwrite
    sudo echo 5000 > /sys/kernel/debug/tracing/buffer_size_kb
    # reset interface
    sudo ip link set $server_intf down
    sleep 2
    sudo ip link set $server_intf up
    sleep 2
#     sudo bash /home/benny/restart.sh
}


#first run very long running MLC app, to find out network tput
for ((j = 0; j < $num_runs; j += 1)); do
echo "running instance $j"

#### pre-run cleanup -- kill any existing clients/screen sessions
cleanup

reports_dir="${setup_dir}/reports/${exp_name}-RUN-${j}"
server_app_log_file="${reports_dir}/server_app.log"
sudo mkdir -p "$reports_dir"

#### start MLC
if [ "$mlc_cores" = "none" ]; then
    echo "No MLC instance used..."
    # Perform actions for "none" input
else
    echo "starting MLC..."
    $mlc_dir/mlc --loaded_latency -T -d0 -e -k$mlc_cores -j0 -b1g -t10000 -W2 &> mlc.log &
    ## wait until MLC starts sending memory traffic at full rate
    echo "waiting for MLC for start..."
    progress_bar 30 1
fi

#### setup and start servers
echo "setting up server config..."
# sudo bash /home/benny/restart.sh
cd $setup_dir
sudo bash setup-envir.sh -i $server_intf -a $server -m $mtu -d $ddio --ring_buffer $ring_buffer --buf $buf -f 1 -r 0 -p 0 -e 1 -o 1
cd -

echo "starting server instances..."
cd $exp_dir
sudo bash run-netapp-tput.sh --mode server -n "$num_servers" -N "$num_clients" -o "${exp}-RUN-${j}" \
        -p "$init_port" -c "$cpu_mask" &> "$server_app_log_file" &
sleep 2
cd -

echo "turning on IOVA logging via ftrace"
sudo echo > /sys/kernel/debug/tracing/trace
sudo echo 1 > /sys/kernel/debug/tracing/tracing_on

#### setup and start clients
echo "setting up and starting clients..."
client_cmd="cd '$setup_dir_client'; sudo bash setup-bare-metal.sh --dep '$home' --intf '$client_intf' --ip '$client' -m '$mtu' -d '$ddio' -r '$ring_buffer' --socket-buf '$buf' --hwpref 1 --rdma 0 --pfc 0 --ecn 1 --opt 1; "
client_cmd+="cd '$exp_dir_client'; sudo bash run-netapp-tput.sh --mode client --server-ip '$server' -n '$num_servers' -N '$num_clients'  -o '${exp_name}-RUN-${j}' -p '$init_port' -c '$cpu_mask' -b '$bandwidth'; exec bash"
$SSH_CLIENT_CMD "screen -dmS client_session sudo bash -c \"$client_cmd\""

#### warmup
echo "warming up..."
progress_bar 10 1

#record stats
##start sender side logging
echo "starting logging at client..."
client_logging_cmd="cd '$setup_dir_client'; sudo bash record-host-metrics.sh \
        --dep '$home' -o '${exp_name}-RUN-${j}' --dur '$dur' \
        --cpu-util 1 -c '$cpu_mask' --retx 1 --tcplog 1 --bw 1 --flame 0 \
	--pcie 0 --membw 0 --iio 0 --pfc 0 --intf '$client_intf' --type 0; exec bash"
$SSH_CLIENT_CMD "screen -dmS logging_session_client sudo bash -c \"$client_logging_cmd\""

##start receiver side logging
echo "starting logging at server..."
cd $setup_dir
sudo bash record-host-metrics.sh --dep "$viommu" -o "${exp}-RUN-${j}" \
    --dur "$dur" --cpu-util 1 -c "$cpu_mask" --retx 1 --tcplog 1 --bw 1 --flame 0 \
    --pcie 1 --membw 1 --iio 1 --pfc 0 --intf "$server_intf" --type 0
echo "done logging..."
cd -

#transfer sender-side info back to receiver
# sshpass -p benny ssh benny@192.168.11.117 -- "sudo rm /dev/null; sudo mknod /dev/null c 1 3; sudo chmod 666 /dev/null"
# sshpass -p $password scp $uname@$ssh_hostname:$setup_dir/reports/$exp-RUN-$j/retx.rpt $setup_dir/reports/$exp-RUN-$j/retx.rpt
scp -i "$CLIENT_SSH_IDENTITY_FILE" \
	"${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}:$setup_dir_client/reports/$exp-RUN-$j/retx.rpt" "$setup_dir/reports/$exp-RUN-$j/retx.rpt"

sleep $(($dur * 2))

#post-run cleanup
cleanup
done

if [ "$mlc_cores" = "none" ]; then
    echo "No MLC instance used... Skipping MLC throughput collection"
else
    echo "MLC cores detected.. Still skipping MLC throughput collection"
   # #now run very long network app, to find out MLC tput
   # for ((j = 0; j < $num_runs; j += 1)); do
   # echo "running instance $j"

   # #### pre-run cleanup -- kill any existing clients/screen sessions
   # cleanup

   # #### setup and start servers
   # echo "setting up server config..."
   # cd $setup_dir
   # sudo bash setup-envir.sh -i $server_intf -a $server -m $mtu -d $ddio --ring_buffer $ring_buffer --buf $buf -f 1 -r 0 -p 0 -e 0 -o 1
   # cd -

   # echo "starting server instances..."
   # cd $exp_dir
   # sudo bash run-netapp-tput.sh -m server -S $num_servers -o $exp-MLCRUN-$j -p $init_port -c $cpu_mask &
   # sleep 2
   # cd -

   # #### setup and start clients
   # echo "setting up and starting clients..."
   # sshpass -p $password ssh $uname@$ssh_hostname 'screen -dmS client_session sudo bash -c "cd '$setup_dir'; sudo bash setup-envir.sh -i '$client_intf' -a '$client' -m '$mtu' -d '$ddio' --ring_buffer '$ring_buffer' --buf '$buf' -f 1 -r 0 -p 0 -e 0 -o 1; cd '$exp_dir'; sudo bash run-netapp-tput.sh -m client -a '$server' -C '$num_clients' -S '$num_servers' -o '$exp'-MLCRUN-'$j' -p '$init_port' -c '$cpu_mask' -b '$bandwidth'; exec bash"'

   # #### start MLC
   # echo "starting MLC..."
   # $mlc_dir/mlc --loaded_latency -T -d0 -e -k$mlc_cores -j0 -b1g -t$mlc_dur -W2 &> $setup_dir/reports/$exp-MLCRUN-$j/mlc.log &
   # ## wait until MLC starts sending memory traffic at full rate
   # sleep 30
   # echo "Running MLC..."
   # progress_bar $mlc_dur 1

   # #post-run cleanup
   # cleanup
   # done
fi

#collect info from all runs
if [ "$mlc_cores" = "none" ]; then
    sudo python3 collect-tput-stats.py $exp $num_runs 0
else
    sudo python3 collect-tput-stats.py $exp $num_runs 0 #TODO: Change back to 1
fi


