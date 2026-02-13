dur=5
(netstat -s
sleep $dur
netstat -s) > netstat.out

cat netstat.out | grep "segments sent out" | awk -v dur="$dur" 'NR==1 {first=$1} NR==2 {second=$1} END {print (second - first)/dur}' 

