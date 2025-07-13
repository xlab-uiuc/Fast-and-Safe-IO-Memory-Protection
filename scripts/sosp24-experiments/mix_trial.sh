cd ..

echo "Running ring buffer 2048 experiment... this may take a few minutes"
iommu_on=$(grep -o intel_iommu=on /proc/cmdline)
iommu_config=""
if [ -z $iommu_on ]; then
    iommu_config="iommu-off"
else
    iommu_config="iommu-on"
fi

sudo ethtool --pause enp101s0f1np1 tx off rx off
sshpass -p saksham ssh saksham@genie12.cs.cornell.edu "sudo -S <<< "saksham" ethtool --pause ens2f1np1 tx off rx off"

# 256 512 1024 2048
for i in 2048; do
    for f in 20 40 80 100; do
        format_i=$(printf "%04d\n" $i)
        format_f=$(printf "%02d\n" $f)
        exp_name="$(uname -r)-${iommu_config}-ring_buffer-${format_i}-flows-${format_f}"
        # exp_name="$(uname -r)-${iommu_config}-ring_buffer-${format_i}"
        echo $exp_name
        sudo bash run-dctcp-tput-experiment.sh -E $exp_name -M 4000 --num_servers $f --num_clients $f -c "4,8,12,16,20" --ring_buffer $i --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf enp101s0f1np1 --client_intf ens2f1np1
        python3 report-tput-metrics.py $exp_name tput,drops,acks,iommu,cpu
    done
done
# --server_intf ens2f1np1 > /dev/null 2>&1
# python3 report-tput-metrics.py ring_buffer-2048 tput,drops,acks,iommu,cpu

# echo "Running ring buffer 1024 experiment... this may take a few minutes"
# sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-1024" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 1024 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
# python3 report-tput-metrics.py ring_buffer-1024 tput,drops,acks,iommu,cpu

# echo "Running ring buffer 512 experiment... this may take a few minutes"
# sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-512" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 512 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
# python3 report-tput-metrics.py ring_buffer-512 tput,drops,acks,iommu,cpu

# echo "Running ring buffer 256 experiment... this may take a few minutes"
# sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-256" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
# python3 report-tput-metrics.py ring_buffer-256 tput,drops,acks,iommu,cpu
``
