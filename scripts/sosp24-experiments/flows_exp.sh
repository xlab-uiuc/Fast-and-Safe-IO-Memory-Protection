./clean_logs.sh
cd ..

echo "Running flow5 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "flow5" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py flow5 tput,drops,acks,iommu,cpu

echo "Running flow10 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "flow10" -M 4000 --num_servers 10 --num_clients 10 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py flow10 tput,drops,acks,iommu,cpu

echo "Running flow20 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "flow20" -M 4000 --num_servers 20 --num_clients 20 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py flow20 tput,drops,acks,iommu,cpu

echo "Running flow40 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "flow40" -M 4000 --num_servers 40 --num_clients 40 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py flow40 tput,drops,acks,iommu,cpu
