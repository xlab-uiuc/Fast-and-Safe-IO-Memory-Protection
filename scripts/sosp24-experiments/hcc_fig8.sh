# same 3 experiments of MLC increase bandwidth contention
# need to be careful how I present breakdown of the 3 configurations:
# IOMMU Off (top plot), Linux + IOMMU On (bottom), Linux + IOMMU On + F&S (bottom)

sudo bash run-dctcp-tput-experiment-hcc.sh -E "hcc-mlc0" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores 'none' --bandwidth "100g" --server_intf ens2f1np1
sudo bash run-dctcp-tput-experiment-hcc.sh -E "hcc-mlc1" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores '1' --bandwidth "100g" --server_intf ens2f1np1
sudo bash run-dctcp-tput-experiment-hcc.sh -E "hcc-mlc2" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores '1,2' --bandwidth "100g" --server_intf ens2f1np1
sudo bash run-dctcp-tput-experiment-hcc.sh -E "hcc-mlc3" -M 4000 --num_servers 5 --num_clients 5 -c "4,8,12,16,20" --ring_buffer 256 --buf 1 --mlc_cores '1,2,3' --bandwidth "100g" --server_intf ens2f1np1

