SCRIPT_NAME="reset-host"

CPUPOWER_PATH="/home/lbalara/viommu/linux-6.12.9/tools/power/cpupower" #TODO: HARDCODED

LD_LIBRARY_PATH=$CPUPOWER_PATH $CPUPOWER_PATH/cpupower --cpu all frequency-set --governor ondemand
echo on > /sys/devices/system/cpu/smt/control
echo 1 > /proc/sys/kernel/numa_balancing
echo 0 > /sys/kernel/debug/tracing/tracing_on
echo 0 > /sys/kernel/debug/tracing/options/overwrite
echo 20000 > /sys/kernel/debug/tracing/buffer_size_kb

rm -rf temp/