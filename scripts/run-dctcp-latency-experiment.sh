#!/bin/bash


#default values
exp="dctcp-lat-test"
server="192.168.11.127"
client="192.168.11.125"
server_intf="enp8s0"
client_intf="ens2f1np1"
num_servers=5
num_clients=5
init_port=3000
ddio=1
mtu=4000
dur=20
cpu_mask_server="0,1,2,3,4"
cpu_mask_client="0,4,8,12,16"
lat_app_core=20
lat_app_port=5050
mlc_cores="none"
mlc_dur=100
ring_buffer=256
num_runs=1
home="/home/schai"
setup_dir=$home/viommu/utils
exp_dir=$home/viommu/utils/tcp
mlc_dir=$home/mlc/Linux

home_client="/home/saksham"
setup_dir_client=$home_client/Fast-and-Safe-IO-Memory-Protection/utils
exp_dir_client=$home_client/Fast-and-Safe-IO-Memory-Protection/utils/tcp
mlc_dir=$home_client/mlc/Linux

uname=saksham
addr=192.168.11.125
ssh_hostname=genie12.cs.cornell.edu
password=saksham


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
    sudo pkill -9 -f netperf
    sshpass -p $password ssh $uname@$addr 'screen -S $(screen -list | awk "/\\.client_session\t/ {print \$1}") -X quit'
    sshpass -p $password ssh $uname@$addr 'screen -S $(screen -list | awk "/\\.logging_session\t/ {print \$1}") -X quit'
    sshpass -p $password ssh $uname@$addr 'screen -wipe'
    sshpass -p $password ssh $uname@$addr 'sudo pkill -9 -f iperf'
    sudo bash /home/benny/restart.sh
}


#first run very long running MLC app, to find out network tput
for ((j = 0; j < $num_runs; j += 1)); do
echo "running instance $j"

#### pre-run cleanup -- kill any existing clients/screen sessions
cleanup

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
cd $setup_dir
sudo bash setup-envir-unmodified.sh -i $server_intf -a $server -m $mtu -d $ddio --ring_buffer $ring_buffer -f 1 -r 0 -p 0 -e 1 -b 1 -o 1
cd -

echo "starting server instances..."
cd $exp_dir
sudo bash run-netapp-tput.sh -m server -S $num_servers -o $exp-LATRUN-$j -p $init_port -c $cpu_mask_server &
sleep 2
cd -

#### setup and start clients, and netserver on the client machine
echo "setting up and starting clients..."
sshpass -p $password ssh $uname@$addr 'screen -dmS client_session sudo bash -c "cd '$setup_dir_client'; sudo bash setup-envir.sh -i '$client_intf' -a '$client' -m '$mtu' -d '$ddio' -f 1 -r 0 -p 0 -e 1 -b 1 -o 1; cd '$exp_dir_client'; sudo bash run-netapp-tput.sh -m client -a '$server' -C '$num_clients' -S '$num_servers' -o '$exp'-RUN-'$j' -p '$init_port' -c '$cpu_mask_client'; sudo bash run-netapp-lat.sh -m netserver -p '$lat_app_port' -c '$lat_app_core' ;exec bash"'


#### warmup
echo "warming up..."
progress_bar 10 1

### start netperf clients and logging
for k in {128,512,2048,8192,32768}
do
     cd $exp_dir
     echo "Dumping Netperf Stats for RPC size $k bytes..."
     sudo bash run-netapp-lat.sh -m netperf -s $k -o $exp-LATRUN-$j -d 10 -a $client -p $lat_app_port -c $lat_app_core
     cd -
done

#post-run cleanup
cleanup
done

#collect info from all runs
sudo python3 collect-lat-stats.py $exp $num_runs


