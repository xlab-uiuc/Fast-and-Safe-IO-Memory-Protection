./clean_logs.sh
cd ..

working_dir=$(pwd)
echo "Running flow5 experiment... this may take a few minutes"


iommu_on=$(grep -o intel_iommu=on /proc/cmdline)
iommu_config=""
if [ -z $iommu_on ]; then
    iommu_config="iommu-off"
else
    iommu_config="iommu-on"
fi

# pause the frame
sudo ethtool --pause enp101s0f1np1 tx off rx off
sshpass -p saksham ssh saksham@genie12.cs.cornell.edu "sudo -S <<< "saksham" ethtool --pause ens2f1np1 tx off rx off"

sleep 10

warmup_time=100
buffer=4
folder_name=""

echo "Starting experiment"

for i in 4 8 16 32 64 128; do
# for buffer in 16 32 64 128 256 512; do
# for buffer in 512; do
    # for j in $(seq 1 1 1) # start from 1, increment by 2 until 10
    # do
        cd $working_dir
        # i=64
        # cur_time=$(date +"%Y-%m-%d-%H-%M-%S")
        format_i=$(printf "%02d\n" $i)
        # exp_name="jun17-testing-$(uname -r)-${iommu_config}-flow-${format_i}-warmup-${warmup_time}-buffer-${buffer}"
        folder_name="jun27-zero_newIPERF-4cores-1x_ring-${iommu_config}-buffer-${buffer}"
        exp_name="${folder_name}-$(uname -r)-warmup-${warmup_time}-flow-${format_i}"
        echo $exp_name

        sudo bash run-dctcp-tput-experiment-new.sh -E $folder_name/$exp_name -M 4000 --num_servers $i --num_clients $i -c "4,8,12,16" --ring_buffer 256 --buf $buffer --mlc_cores 'none' --bandwidth "100g" \
            --server_intf enp101s0f1np1 --client_intf ens2f1np1 --warmup $warmup_time

        python3 report-tput-metrics.py $folder_name/$exp_name tput,drops,acks,iommu,cpu
        cd ../utils/reports/$folder_name/$exp_name

        sudo bash -c "cat /sys/kernel/debug/tracing/instances/flow2/trace > trace.log"
        sudo bash -c "cat /sys/kernel/debug/tracing/instances/flow1/trace > tcp_trace.log"
        sudo echo 0 > /sys/kernel/debug/tracing/instances/flow2/tracing_on
        sudo echo 0 > /sys/kernel/debug/tracing/instances/flow1/tracing_on
        # sudo bash -c "rg iperf3 iova.log > iperf_iova.log"
        # sudo bash -c "rg 'core: 16' iova.log > iperf_iova_core16.log"
        # sudo bash -c "rg core iova.log > core_iova.log"

        python /home/saksham/Fast-and-Safe-IO-Memory-Protection/scripts/parse_trace_logs.py && cat trace_stats.txt

        cd $working_dir
        # sudo chmod +666 -R ../utils/reports/$folder_name
        # python sosp24-experiments/plot_iova_logging.py \
        #     --exp_folder "../utils/reports/$exp_name" \
        #     --log_file "iova.log"

        # python3 sosp24-experiments/count_invalidation.py --dir "../utils/reports/$exp_name"
    # done
done

cd ../utils/reports/$folder_name/
python ../../../scripts/generate_summ.py . > summary.txt
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
