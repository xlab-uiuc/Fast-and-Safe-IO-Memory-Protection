client_ip=192.168.11.117
server_ip=192.168.11.116
iface=ens2f1np1

# Configuration
#~/NetChannel/scripts/run_np.sh $iface

# Run the server program
sudo taskset -c 0 redis/src/redis-server redis/redis_nd.conf
