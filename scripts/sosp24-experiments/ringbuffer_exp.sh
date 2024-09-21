./clean_logs.sh
cd ..

echo "Running ring buffer 2048 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-2048" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 2048 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py ring_buffer-2048 tput,drops,acks,iommu,cpu

echo "Running ring buffer 1024 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-1024" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 1024 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py ring_buffer-1024 tput,drops,acks,iommu,cpu

echo "Running ring buffer 512 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-512" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 512 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py ring_buffer-512 tput,drops,acks,iommu,cpu

echo "Running ring buffer 256 experiment... this may take a few minutes"
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-256" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-tput-metrics.py ring_buffer-256 tput,drops,acks,iommu,cpu

