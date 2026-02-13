# we want to vary the nubmer of connections for whatever minimum size is required to saturate
#value=4
for mtu in 4000 9000; do
	sudo ifconfig ens2f1np1 mtu $mtu
	ssh benny@genie04.cs.cornell.edu "sudo ifconfig ens2f1 mtu $mtu"
	for cores in 8; do
		(
		for value in 32; do
			echo "new value: ${value}"
			for clients in 16 32; do
				for conn in 16 32 64; do
					if [ $conn -ge $clients ]; then
					    ./wrk_bench_get.sh http_get $clients $value 12 $conn $cores
					    sleep 1
					    sudo pkill wrk 
					    ssh benny@genie04.cs.cornell.edu "sudo nginx -s reload"
					    sleep 45 
					fi
				done
			done
		done
	) > results/off_32kb_${cores}cores_${mtu}mtu.txt
	done
done
echo "all done"
