dur=5
(redis-cli -h 192.168.11.116 -p 6386 INFO | grep total_commands_processed
sleep $dur
redis-cli -h 192.168.11.116 -p 6386 INFO | grep total_commands_processed) > tput.out

echo "RPS on server on port 6386"

cat tput.out | awk -F: 'NR==1 {first=$2} NR==2 {second=$2} END {print (second - first)/5}'
