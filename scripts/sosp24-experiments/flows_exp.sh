./clean_logs.sh
cd ..

echo "Running flow experiment... this may take a few minutes"

client_intf="eno12409np1"
server_intf="enp8s0np1"


iommu_on=$(grep -o intel_iommu=on /proc/cmdline)
iommu_config=""
if [ -z $iommu_on ]; then
    iommu_config="host-strict-guest-off"
else
    iommu_config="host-strict-guest-on"
fi

# pause the frame
sudo ethtool --pause $server_intf tx off rx off
ssh Leshna@128.110.220.127 "sudo ethtool --pause ${client_intf} tx off rx off"

sleep 1

timestamp=$(date '+%H-%M_%m-%d')
# 5 10 20 40
for i in 5 ; do
    format_i=$(printf "%02d\n" $i)
    exp_name="${timestamp}-$(uname -r)-flow${format_i}-${iommu_config}"
    echo $exp_name
    sudo bash run-dctcp-tput-experiment.sh -E $exp_name -M 4000 --num_servers $i --num_clients $i -c "0,1,2,3,4" -m "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf $server_intf --client_intf $client_intf
# > /dev/null 2>&1
    #sudo bash run-dctcp-tput-experiment.sh -E $exp_name -M 4000 --num_servers $i --num_clients $i -c "4" -m "20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf $server_intf --client_intf $client_intf    
    python3 report-tput-metrics.py $exp_name tput,drops,acks,iommu,cpu
    echo $PWD
    cd ../utils/reports/$exp_name

    sudo bash -c "cat /sys/kernel/debug/tracing/trace > iova.log"
    # sudo bash -c "rg iperf3 iova.log > iperf_iova.log"
    # sudo bash -c "rg 'core: 16' iova.log > iperf_iova_core16.log"
    # sudo bash -c "rg core iova.log > core_iova.log"

    cd -
    sudo chmod +666 -R ../utils/reports/$exp_name

    # python sosp24-experiments/plot_iova_logging.py \
    #     --exp_folder "../utils/reports/$exp_name" \
    #     --log_file "iova.log"

done

