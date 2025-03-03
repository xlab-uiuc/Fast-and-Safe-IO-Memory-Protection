#!/bin/bash


#default values
exp="benny-test"
server="192.168.11.127"
client="192.168.11.125"
server_intf="enp8s0"
client_intf="ens2f1np1"
num_servers=5
num_clients=5
init_port=3000
ddio=0
mtu=4000
dur=20
cpu_mask_server="0,1,2,3,4"
cpu_mask_client="0,4,8,12,16"
mlc_cores="none"
mlc_dur=100
ring_buffer=256
buf=1
bandwidth="100g"
num_runs=1
home="/home/schai"
setup_dir=$home/viommu/utils
exp_dir=$home/viommu/utils/tcp
mlc_dir=$home/mlc/Linux

home_client="/home/saksham"
setup_dir_client=$home_client/Fast-and-Safe-IO-Memory-Protection/utils
exp_dir_client=$home_client/Fast-and-Safe-IO-Memory-Protection/utils/tcp
mlc_dir_client=$home_client/mlc/Linux

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
    rm -f $home/hostCC/utils/out.perf-folded
    rm -f $home/hostCC/utils/perf.data
    sshpass -p $password ssh $uname@$ssh_hostname 'screen -S $(screen -list | awk "/\\.client_session\t/ {print \$1}") -X quit'
    sshpass -p $password ssh $uname@$ssh_hostname 'screen -S $(screen -list | awk "/\\.logging_session\t/ {print \$1}") -X quit'
    sshpass -p $password ssh $uname@$ssh_hostname 'screen -wipe'
    sshpass -p $password ssh $uname@$ssh_hostname 'sudo pkill -9 -f iperf'
    ## IOVA logging
    sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
    sudo echo 0 > /sys/kernel/debug/tracing/options/overwrite
    sudo echo 5000 > /sys/kernel/debug/tracing/buffer_size_kb
      # reset interface
    sudo ip link set $server_intf down
    sleep 2
    sudo ip link set $server_intf up
    sleep 2
    sudo bash /home/benny/restart.sh
}


#first run very long running MLC app, to find out network tput
for ((j = 0; j < $num_runs; j += 1)); do
echo "running instance $j"

#### pre-run cleanup -- kill any existing clients/screen sessions
cleanup
sudo bash /home/benny/restart.sh

#### start MLC
sudo bash ../utils/set_mba_levels.sh
cd /home/benny/hostCC/src
sudo rm hostcc-module.ko
sudo make
if [ "$mlc_cores" = "none" ]; then
    echo "No MLC instance used..."
    echo "sudo insmod hostcc-module.ko mode=0 target_iio_wr_thresh=70 target_pcie_thresh=84"
    sudo rmmod hostcc-module.ko
    sleep 5
    sudo insmod hostcc-module.ko mode=0 target_iio_wr_thresh=70 target_pcie_thresh=84 
    # Perform actions for "none" input
else
    echo "starting MLC..."
    $mlc_dir/mlc --loaded_latency -T -d0 -e -k$mlc_cores -j0 -b1g -t10000 -W2 &> mlc.log &
    ## wait until MLC starts sending memory traffic at full rate
    echo "waiting for MLC for start..."
    echo "sudo insmod hostcc-module.ko target_pcie_thresh=84 target_iio_wr_thresh=85 target_pid=$(pidof mlc)"
    sudo rmmod hostcc-module.ko
    sleep 5
    sudo insmod hostcc-module.ko mode=0 target_iio_wr_thresh=70 target_pcie_thresh=84 target_pid=$(pidof mlc)
    progress_bar 15 1
fi
sudo dmesg --clear

sleep 10 #give time for hostcc module to load
cd -

#### setup and start servers
echo "setting up server config..."
cd $setup_dir
sudo bash setup-envir.sh -i $server_intf -a $server -m $mtu -d $ddio --ring_buffer $ring_buffer --buf $buf -f 1 -r 0 -p 0 -e 0 -o 1
cd -

echo "starting server instances..."
cd $exp_dir
sudo bash run-netapp-tput.sh -m server -S $num_servers -o $exp-RUN-$j -p $init_port -c $cpu_mask &
sleep 2
cd -

echo "turning on IOVA logging via ftrace"
sudo echo > /sys/kernel/debug/tracing/trace
sudo echo 1 > /sys/kernel/debug/tracing/tracing_on

#### setup and start clients
echo "setting up and starting clients..."
sshpass -p $password ssh $uname@$ssh_hostname 'screen -dmS client_session sudo bash -c "cd '$setup_dir'; sudo bash setup-envir.sh -i '$client_intf' -a '$client' -m '$mtu' -d '$ddio' --ring_buffer '$ring_buffer' --buf '$buf' -f 1 -r 0 -p 0 -e 0 -o 1; cd '$exp_dir'; sudo bash run-netapp-tput.sh -m client -a '$server' -C '$num_clients' -S '$num_servers' -o '$exp'-RUN-'$j' -p '$init_port' -c '$cpu_mask' -b '$bandwidth'; exec bash"'

#### warmup
echo "warming up..."
progress_bar 10 1

#record stats
##start sender side logging
echo "starting logging at client..."
sshpass -p $password ssh $uname@$ssh_hostname 'screen -dmS logging_session sudo bash -c "cd '$setup_dir'; sudo bash record-host-metrics.sh -f 0 -t 1 -i '$client_intf' -o '$exp-RUN-$j' --type 0 --cpu_util 1 --retx 1 --pcie 0 --membw 0 --dur '$dur' --cores '$cpu_mask' ; exec bash"'

##start receiver side logging
echo "starting logging at server..."
cd $setup_dir
sudo bash record-host-metrics.sh -f 0 -I 1 -t 1 -i $server_intf -o $exp-RUN-$j --type 0 --cpu_util 1 --pcie 1 --membw 1 --dur $dur --cores $cpu_mask
echo "done logging..."
cd -

#transfer sender-side info back to receiver
sshpass -p $password scp $uname@$ssh_hostname:$setup_dir/reports/$exp-RUN-$j/retx.rpt $setup_dir/reports/$exp-RUN-$j/retx.rpt

sleep $(($dur * 2))

#post-run cleanup
cleanup
done

if [ "$mlc_cores" = "none" ]; then
    echo "No MLC instance used... Skipping MLC throughput collection"
    sudo rmmod hostcc-module.ko
    dmesg > /home/benny/pcie.log
else
    sudo rmmod hostcc-module.ko
    dmesg > /home/benny/pcie.log
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

sudo python3 collect-tput-stats.py $exp $num_runs 0
#collect info from all runs
#if [ "$mlc_cores" = "none" ]; then
#    sudo python3 collect-tput-stats.py $exp $num_runs 0
#else
#    sudo python3 collect-tput-stats.py $exp $num_runs 1
#fi


