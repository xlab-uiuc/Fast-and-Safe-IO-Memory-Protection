#!/bin/bash

client_ip=192.168.11.117
server_ip=192.168.11.116
iface=ens2f1np1
#sudo ethtool -K $iface tso on gso on gro on lro on
#sudo bash enable_arfs.sh $iface
sudo ifconfig ens2f1np1 mtu 9000

function cleanup(){
	echo "cleanup"
	kill $(jobs -p -r)
}

trap cleanup EXIT

# clean up old servers
#sudo pkill redis-ser
#sleep 1

# Configuration
#~/NetChannel/scripts/run_np.sh $iface

# Run the server program
start_port=6379
num_servers=8
for ((i=0;i<${num_servers};i++)); do
	cpu=$((4*i))
	port=$((start_port+i))
	echo "Starting redis server on CPU: $cpu, port: $port"
	sudo taskset -c $cpu redis/src/redis-server redis_nd.conf --port $port &
done

wait
