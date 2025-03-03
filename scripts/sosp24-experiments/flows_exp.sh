./clean_logs.sh
cd ..

echo "Running flow5 experiment... this may take a few minutes"

client_intf="ens2f1np1"
server_intf="enp8s0"


iommu_on=$(grep -o intel_iommu=on /proc/cmdline)
iommu_config=""
if [ -z $iommu_on ]; then
    iommu_config="iommu-off-lazy"
else
    iommu_config="iommu-on-lazy"
fi

# pause the frame
sudo ethtool --pause $server_intf tx off rx off
ssh saksham@genie12.cs.cornell.edu "sudo ethtool --pause ${client_intf} tx off rx off"

sleep 1

timestamp=$(date '+%H-%M_%m-%d')
# 5 10 20 40
# 10 20 40
for i in 5 10 20 40; do
    format_i=$(printf "%02d\n" $i)
    exp_name="${timestamp}-$(uname -r)-flow${format_i}-${iommu_config}-ofed24.10"
    echo $exp_name
    sudo bash run-dctcp-tput-experiment.sh -E $exp_name -M 4000 --num_servers $i --num_clients $i -c "0,1,2,3,4" -m "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf $server_intf --client_intf $client_intf
# > /dev/null 2>&1
    python3 report-tput-metrics.py $exp_name tput,cpu
done

# sudo bash run-dctcp-tput-experiment.sh -E "flow5-iommu-on" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" \
#     --server_intf ens2f0np0 --client_intf ens2f0
# # > /dev/null 2>&1
# python3 report-tput-metrics.py flow5 tput,drops,acks,iommu,cpu

# echo "Running flow10 experiment... this may take a few minutes"
# sudo bash run-dctcp-tput-experiment.sh -E "flow10" -M 4000 --num_servers 10 --num_clients 10 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
# python3 report-tput-metrics.py flow10 tput,drops,acks,iommu,cpu

# echo "Running flow20 experiment... this may take a few minutes"
# sudo bash run-dctcp-tput-experiment.sh -E "flow20" -M 4000 --num_servers 20 --num_clients 20 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
# python3 report-tput-metrics.py flow20 tput,drops,acks,iommu,cpu

# echo "Running flow40 experiment... this may take a few minutes"
# sudo bash run-dctcp-tput-experiment.sh -E "flow40" -M 4000 --num_servers 40 --num_clients 40 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
# python3 report-tput-metrics.py flow40 tput,drops,acks,iommu,cpu
