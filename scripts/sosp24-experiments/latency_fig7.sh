# latency experiment
cd ..

echo "Running latency experiment... this may take a few minutes"
sudo bash run-dctcp-latency-experiment.sh -E "latency" -M 4000 --num_servers 5 --num_clients 5 -c "0,4,8,12,16" -L 20 --server_intf ens2f1np1 > /dev/null 2>&1
python3 report-lat-metrics.py latency
