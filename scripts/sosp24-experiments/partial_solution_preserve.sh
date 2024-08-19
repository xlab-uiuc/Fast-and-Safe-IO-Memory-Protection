# NIC Rx Ring buffer size
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-2048-sol" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 2048 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-1024-sol" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 1024 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-512-sol" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 512 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1
sudo bash run-dctcp-tput-experiment.sh -E "ring_buffer-256-sol" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1

sudo bash run-dctcp-tput-experiment.sh -E "flow5-sol" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1
sudo bash run-dctcp-tput-experiment.sh -E "flow10-sol" -M 4000 --num_servers 10 --num_clients 10 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1
sudo bash run-dctcp-tput-experiment.sh -E "flow20-sol" -M 4000 --num_servers 20 --num_clients 20 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1
sudo bash run-dctcp-tput-experiment.sh -E "flow40-sol" -M 4000 --num_servers 40 --num_clients 40 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1 -d 1

