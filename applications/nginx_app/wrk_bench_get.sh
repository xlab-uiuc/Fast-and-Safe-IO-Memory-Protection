client_ip=192.168.11.116
server_ip=192.168.11.117
iface=ens2f1

#sudo ifconfig $iface mtu 9000
#sudo ethtool -K $iface tso on gso on gro on lro on

#command line args
exp_name=${1:-"http_get"}
client_threads=${2:-40}
val_size=${3:-4}
dur=${4:-10}
connections=${5:-500}
num_clients=${6:-5}

rm -rf "logs/${exp_name}"
mkdir -p "logs/${exp_name}"

mtu=$(ifconfig | grep "ens2f1np1" | awk '{for(i=1;i<=NF;i++) if($i=="mtu") print $(i+1)}')
# Run the client program
start_port=6000
#requests=100000
#requests=$((10000000000/val_size))
#requests=$((1000000/val_size))
echo "### Running wrk with $num_clients cores and $((client_threads)) client threads, ${connections} connections and ${val_size}KB value size for $dur seconds with mtu $mtu"

base_threads=$((client_threads / num_clients))         # Base number of threads per core
extra_threads=$((client_threads % num_clients))        # Extra threads to be distributed
threads=0

for ((i=0;i<${num_clients};i++)); do
	(
		if [ $i -lt $extra_threads ]; then
		    threads=$((base_threads + 1))
		else
		    threads=$base_threads
		fi
		#echo "threads: $threads"
		#cpu=$((4*i))
		port=$((start_port+i))
		core=$((i*4))
		#echo "### Run redis_bench on port: $port###"
		#connections=threads*64
		sudo taskset -c $core nice -20 ./wrk2 -t${threads} -c$((connections)) -d${dur}s -R 5000099 http://192.168.11.117:${port}/file_${val_size}KB.html > logs/${exp_name}/output${i}
	) &
done

#sleep 1s
#./dump_netstat.sh

wait
python3 report_data.py $exp_name
