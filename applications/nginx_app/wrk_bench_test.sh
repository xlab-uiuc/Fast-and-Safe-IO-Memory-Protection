sudo taskset -c 0 ./wrk -t20 -c100 -d30s http://192.168.11.117:6000/file_4KB.html
