#!/bin/bash

# Treat unset variables as an error when substituting.
set -u

#-------------------------------------------------------------------------------
# CONFIGURATION AND PATHS
#-------------------------------------------------------------------------------
SCRIPT_NAME="tx-run-rdma-tput-experiment"
INIT_PORT=3000
MLC_DURATION_S=100
HOST_MLC_DIR_REL="mlc/Linux"

FTRACE_BUFFER_SIZE_KB=20000
FTRACE_OVERWRITE_ON_FULL=0 # 0=no overwrite (tracing stops when full), 1=overwrite
PERF_TRACING_HOST_ENABLED=0

# --- Base Directory Paths (Relative to respective home directories) ---
SCRIPT_DIR=$(dirname "$0")
CLIENT_FandS_REL="Fast-and-Safe-IO-Memory-Protection"
HOST_FandS_REL="viommu/Fast-and-Safe-IO-Memory-Protection"
HOST_VIOMMU_REL="viommu/Fast-and-Safe-IO-Memory-Protection"
HOST_RESULTS_REL="viommu"
HOST_PERF_REL="viommu/linux-6.12.9/tools/perf/perf" # TODO: Siyuan change for your directory

# --- F and S Directory Paths (Relative to respective F and S directories) ---
HOST_SETUP_DIR_REL="utils"
HOST_EXP_DIR_REL="utils/tcp"
CLIENT_SETUP_DIR_REL="utils"
CLIENT_EXP_DIR_REL="utils/tcp"

EBPF_HOST_LOADER_REL="$HOST_VIOMMU_REL/tracing/server_loader" # does not exist make it if needed for bare-metal cases
HOST_EBPF_TRACING_CORE=33


#-------------------------------------------------------------------------------
# DEFAULT CONFIGURATION AND PATHS EDITABLE BY COMMAND LINE
#-------------------------------------------------------------------------------
# --- Experiment Setup ---
EXP_NAME="tput-test"
NUM_RUNS=1
CORE_DURATION_S=20 # Duration for the main workload
MLC_CORES="none"
EBPF_TRACING_HOST_ENABLED=0

# --- Server Machine Configuration ---
HOST_HOME="/users/Leshna"
HOST_IP="10.10.1.3"
HOST_INTF="enp23s0f0np0"
HOST_NUM_SERVERS=5
HOST_CPU_MASK="0,1,2,3,4"
HOST_NIC_BUS="0x08"

# --- Client Machine Configuration ---
CLIENT_HOME="/users/Leshna/"
CLIENT_IP="10.10.1.2"
CLIENT_INTF="eno12409np1"
CLIENT_NUM_CLIENTS=5
CLIENT_CPU_MASK="0,4,8,12,16"
CLIENT_BANDWIDTH="100g"

# --- Network & System Parameters ---
MTU=4000
DDIO_ENABLED=1
RING_BUFFER_SIZE=256
TCP_SOCKET_BUF_MB=1

# --- Remote Access (SSH) Configuration ---
CLIENT_SSH_UNAME="saksham"
CLIENT_SSH_HOST="genie12.cs.cornell.edu" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=1 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/home/schai/.ssh/id_ed25519"

CLIENT_EXPECTED_KERNEL="6.12.9"
CLIENT_EXPECTED_IOMMU="intel_iommu=off"

#-------------------------------------------------------------------------------
# Help/usage
#-------------------------------------------------------------------------------
help() {
    echo "Usage: $SCRIPT_NAME"
    echo "Server/Host Configuration:"
    echo "    [ --host-home <path> (Host home directory) ]"
    echo "    [ --host-ip <ip> (IP address of the host) ]"
    echo "    [ --host-intf <name> (Network interface for the server/host) ]"
    echo "    [ --host-bus <bus> (NIC’s PCI bus number) ]"
    echo "    [ -n | --host-num <count> (Number of server instances; default: 5) ]"
    echo "    [ -c | --host-cpu-mask <csv> (HOST CPU mask, comma-separated; default: 0,1,2,3,4) ]"
    echo
    echo "Client Configuration:"
    echo "    [ --client-home <path> (Client home directory) ]"
    echo "    [ --client-ip <ip> (IP address of the client) ]"
    echo "    [ --client-intf <name> (Interface name for the client) ]"
    echo "    [ -N | --client-num <count> (Number of client instances; default: 5) ]"
    echo "    [ -C | --client-cpu-mask <csv> (Client CPU mask, comma-separated; default: 0,4,8,12,16) ]"
    echo
    echo "Experiment Parameters:"
    echo "    [ -e | --exp-name <name> (Experiment name for output directories; default: tput-test) ]"
    echo "    [ -m | --mtu <size> (MTU size: 256/512/1024/2048/4096; default: 4000) ]"
    echo "    [ -d | --ddio <0|1> (DDIO enabled; default: 1) ]"
    echo "    [ -b | --bandwidth <rate> (Client bandwidth in bits/sec, e.g., 100g; default: 100g) ]"
    echo "    [ -r | --ring-buffer <size> (NIC Rx ring buffer size; default: 256) ]"
    echo "    [ --mlc-cores <csv|'none'> (MLC cores; default: none) ]"
    echo "    [ --socket-buf <MB> (TCP socket buffer size in MB; default: 1) ]"
    echo "    [ --dur <seconds> (Core experiment duration in seconds; default: 20) ]"
    echo "    [ --runs <count> (Number of experiment repetitions; default: 1) ]"
    echo "    [ --ebpf-tracing <0|1> (Enable eBPF tracing; default: 0) ]"
    echo
     echo "Client SSH Configuration"
    echo "    [ --client-ssh-name <uname> (SSH username for client) ]"
    echo "    [ --client-ssh-host <ip> (Public IP or hostname for client) ]"
    echo "    [ --client-ssh-use-pass <0|1> (Use password for SSH instead of identity file) ]"
    echo "    [ --client-ssh-pass <pass> (SSH Password for client; needed if client-ssh-use-pass 1) ]"
    echo "    [ --client-ssh-ifile <path> (Path of identity file; needed if client-ssh-use-pass 0) ]"
    echo "Help:"
    echo "    [ -h | --help ]"
    exit 2
}


#-------------------------------------------------------------------------------
# COMMAND-LINE ARGUMENT PARSING
#-------------------------------------------------------------------------------
SHORT_OPTS="n:c:N:C:e:m:d:b:r:h"
LONG_OPTS="host-home:,host-ip:,host-intf:,host-bus:,host-num:,host-cpu-mask:,\
client-home:,client-ip:,client-intf:,client-num:,client-cpu-mask:,\
exp-name:,mtu:,ddio:,bandwidth:,ring-buffer:,mlc-cores:,socket-buf:,dur:,runs:,ebpf-tracing:,\
client-ssh-name:,client-ssh-host:,client-ssh-use-pass:,client-ssh-pass:,client-ssh-ifile:,help"

PARSED_OPTS=$(getopt -a -n "$SCRIPT_NAME" --options "$SHORT_OPTS" --longoptions "$LONG_OPTS" -- "$@")
VALID_ARGUMENTS=$#
if [ "$VALID_ARGUMENTS" -eq 0 ]; then
    help
fi
eval set -- "$PARSED_OPTS"

while :; do
    case "$1" in
        --host-home) HOST_HOME="$2"; shift 2 ;;
        --host-ip) HOST_IP="$2"; shift 2 ;;
        --host-intf) HOST_INTF="$2"; shift 2 ;;
	      --host-bus) HOST_NIC_BUS="$2"; shift 2 ;;
        -n | --host-num) HOST_NUM_SERVERS="$2"; shift 2 ;;
        -c | --host-cpu-mask) HOST_CPU_MASK="$2"; shift 2 ;;
        --client-home) CLIENT_HOME="$2"; shift 2 ;;
        --client-ip) CLIENT_IP="$2"; shift 2 ;;
        --client-intf) CLIENT_INTF="$2"; shift 2 ;;
        -N | --client-num) CLIENT_NUM_CLIENTS="$2"; shift 2 ;;
        -C | --client-cpu-mask) CLIENT_CPU_MASK="$2"; shift 2 ;;
        -e | --exp-name) EXP_NAME="$2"; shift 2 ;;
        -m | --mtu) MTU="$2"; shift 2 ;;
        -d | --ddio) DDIO_ENABLED="$2"; shift 2 ;;
        -b | --bandwidth) CLIENT_BANDWIDTH="$2"; shift 2 ;;
        -r | --ring-buffer) RING_BUFFER_SIZE="$2"; shift 2 ;;
        --mlc-cores) MLC_CORES="$2"; shift 2 ;;
        --socket-buf) TCP_SOCKET_BUF_MB="$2"; shift 2 ;;
        --dur) CORE_DURATION_S="$2"; shift 2 ;;
        --runs) NUM_RUNS="$2"; shift 2 ;;
        --ebpf-tracing) EBPF_TRACING_HOST_ENABLED="$2"; shift 2 ;;
	      --client-ssh-name) CLIENT_SSH_UNAME="$2"; shift 2 ;;
        --client-ssh-host) CLIENT_SSH_HOST="$2"; shift 2 ;;
        --client-ssh-use-pass) CLIENT_USE_PASS_AUTH="$2"; shift 2 ;;
        --client-ssh-pass) CLIENT_SSH_PASSWORD="$2"; shift 2 ;;
        --client-ssh-ifile) CLIENT_SSH_IDENTITY_FILE="$2"; shift 2 ;;
        -h | --help) help ;;
        --) shift; break ;;
        *) echo "Unexpected option: $1"; help ;;
    esac
done

HOST_SETUP_DIR="${HOST_HOME}/${HOST_FandS_REL}/${HOST_SETUP_DIR_REL}"
HOST_EXP_DIR="${HOST_HOME}/${HOST_FandS_REL}/${HOST_EXP_DIR_REL}"
HOST_MLC_DIR="${HOST_HOME}/${HOST_MLC_DIR_REL}"
HOST_PERF="${HOST_HOME}/${HOST_PERF_REL}"
CLIENT_SETUP_DIR="${CLIENT_HOME}/${CLIENT_FandS_REL}/${CLIENT_SETUP_DIR_REL}"
CLIENT_EXP_DIR="${CLIENT_HOME}/${CLIENT_FandS_REL}/${CLIENT_EXP_DIR_REL}"
HOST_RESULTS_DIR="${HOST_HOME}/${HOST_RESULTS_REL}" # TODO: Siyuan (Better name suggestion)
EBPF_HOST_LOADER="${HOST_HOME}/${EBPF_HOST_LOADER_REL}"
PROFILING_LOGGING_DUR_S=$((CORE_DURATION_S))

if [ "$CLIENT_USE_PASS_AUTH" -eq 1 ]; then
	SSH_CLIENT_CMD="sshpass -p $CLIENT_SSH_PASSWORD ssh ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
else
	SSH_CLIENT_CMD="ssh -i $CLIENT_SSH_IDENTITY_FILE ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}"
fi

log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
}

progress_bar() {
    local duration_secs=$1
    local interval_secs=$2
    local elapsed_time_secs=0

    if [ "$duration_secs" -eq 0 ]; then
        printf "[==================================================] 100%% (0/0s)\n"
        return
    fi

    local progress_bar_width=50
    while [ "$elapsed_time_secs" -lt "$duration_secs" ]; do
        elapsed_time_secs=$((elapsed_time_secs + interval_secs))
        if [ "$elapsed_time_secs" -gt "$duration_secs" ]; then
            elapsed_time_secs=$duration_secs
        fi
        
        local progress_percent=$((elapsed_time_secs * 100 / duration_secs))
        local bar_filled_length=$((progress_percent * progress_bar_width / 100))
        
        local bar_visual=""
        for ((k=0; k<bar_filled_length; k++)); do bar_visual+="="; done
        
        printf "[%-*s] %3d%% (%*ds/%ds)\r" "$progress_bar_width" "$bar_visual" "$progress_percent" \
               "${#duration_secs}" "$elapsed_time_secs" "$duration_secs"
        sleep "$interval_secs"
    done
    
    local full_bar_visual=""
    for ((k=0; k<progress_bar_width; k++)); do full_bar_visual+="="; done
    printf "[%-*s] 100%% (%ds/%ds)\n" "$progress_bar_width" "$full_bar_visual" "$duration_secs" "$duration_secs"
}

check_client_kernel() {
    local client_kernel=$($SSH_CLIENT_CMD 'uname -r')
    local client_cmdline=$($SSH_CLIENT_CMD 'cat /proc/cmdline')
    if [[ "$client_kernel" != *"$CLIENT_EXPECTED_KERNEL"* ]]; then
        log_error "Client kernel is not expected. Expected: $CLIENT_EXPECTED_KERNEL, Actual: $client_kernel"
        log_error "To fix, run this"
        log_error "$SSH_CLIENT_CMD 'sudo /home/siyuanc3/iommu-vm/reboot-scripts/reboot-6.12.9-iommu-off.sh'"
        exit 1
    fi

    if [[ "$client_cmdline" != *"$CLIENT_EXPECTED_IOMMU"* ]]; then
        log_error "Client IOMMU is not expected. Expected: $CLIENT_EXPECTED_IOMMU, Actual: $client_cmdline"
        log_error "To fix, run this"
        log_error "$SSH_CLIENT_CMD 'sudo /home/siyuanc3/iommu-vm/reboot-scripts/reboot-6.12.9-iommu-off.sh'"
        exit 1
    fi

    log_info "Client kernel check PASSED!"
}

pre_exp_setup() {
    log_info "--- Starting Pre-experiment Cleanup Phase ---"

    check_client_kernel
    
    log_info "Disabling TX/RX on HOST and CLIENT"
    sudo ethtool --pause $HOST_INTF tx off rx off
    $SSH_CLIENT_CMD "sudo ethtool --pause $CLIENT_INTF tx off rx off"
    
    log_info "Disabling SMT on Client"
    $SSH_CLIENT_CMD "echo off | sudo tee /sys/devices/system/cpu/smt/control"

    # Host's smt, cpu power, numa balance will be setup in setup-host.sh
    log_info "--- Pre-experiment Cleanup Phase Finished ---"
}

post_exp_cleanup() {
    log_info "--- Starting Post-experiment Cleanup Phase ---"
    
    log_info "Resetting HOST ftrace..."
    sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
    sudo echo 0 > /sys/kernel/debug/tracing/options/overwrite
    sudo echo 20000 > /sys/kernel/debug/tracing/buffer_size_kb

    log_info "Resetting HOST..."
    cd '$HOST_SETUP_DIR'; sudo bash reset-host.sh
    
    log_info "--- Post-experiment Cleanup Phase Finished ---"
}


# --- Cleanup Function ---
cleanup() {
    log_info "--- Starting Cleanup Phase ---"

    log_info "Killing local 'loaded_latency', 'iperf', and 'perf record' processes..."
    sudo pkill -9 -f loaded_latency
    sudo pkill -9 -f iperf 

    if [ "$PERF_TRACING_HOST_ENABLED" -eq 1 ]; then
        sudo pkill -SIGINT -f "$HOST_PERF record"
        sleep 1
        sudo pkill -9 -f "$HOST_PERF record"
    fi

    if [ "$EBPF_TRACING_HOST_ENABLED" -eq 1 ]; then
        log_info "Stopping eBPF tracers..."
        host_loader_basename=$(basename "$EBPF_HOST_LOADER")
        cd $(dirname "$EBPF_HOST_LOADER") || { log_error "Failed to cd to $(dirname "$EBPF_HOST_LOADER")"; exit 1; }
        make clean
        make
        cd -
	      sudo pkill -SIGINT -f "$host_loader_basename" 2>/dev/null || true
        sudo pkill -9 -f "$host_loader_basename" 2>/dev/null || true
    fi

    log_info "Terminating screen sessions..."
    $SSH_CLIENT_CMD \
        'screen -ls | grep -E "\.client_session|\.logging_session_client" | cut -d. -f1 | xargs -r -I % screen -S % -X quit'
    $SSH_CLIENT_CMD \
        'sudo pkill -9 -f iperf; screen -wipe || true'


    log_info "Resetting HOST network interface $HOST_INTF..."
    sudo ip link set "$HOST_INTF" down
    sleep 2
    sudo ip link set "$HOST_INTF" up
    sleep 2
    log_info "--- Cleanup Phase Finished ---"
}

save_config_to_report_json() {
    local report_dir="${1:-$current_host_reports_dir}"
    local config_file="$report_dir/config.json"

    local host_cmdline=$($SSH_HOST_CMD 'cat /proc/cmdline')
    local host_kernel=$($SSH_HOST_CMD 'uname -r')
    local client_cmdline=$($SSH_CLIENT_CMD 'cat /proc/cmdline')
    local client_kernel=$($SSH_CLIENT_CMD 'uname -r')

    cat > "$config_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "test_params": {
    "core_duration_s": "$CORE_DURATION_S",
    "mtu": "$MTU",
    "ddio_enabled": "$DDIO_ENABLED",
    "ring_buffer_size": "$RING_BUFFER_SIZE",
    "tcp_socket_buf_mb": "$TCP_SOCKET_BUF_MB",
    "mlc_cores": "$MLC_CORES"
  },
  "host": {
    "ip": "$HOST_IP",
    "interface": "$HOST_INTF",
    "num_servers": "$HOST_NUM_SERVERS",
    "cpu_mask": "$HOST_CPU_MASK",
    "nic_bus": "$HOST_NIC_BUS",
    "kernel": "$host_kernel",
    "cmdline": "$host_cmdline"
  },
  "client": {
    "ip": "$CLIENT_IP",
    "interface": "$CLIENT_INTF",
    "num_clients": "$CLIENT_NUM_CLIENTS",
    "cpu_mask": "$CLIENT_CPU_MASK",
    "bandwidth": "$CLIENT_BANDWIDTH",
    "kernel": "$client_kernel",
    "cmdline": "$client_cmdline"
  },
}
EOF
}

log_info "Starting experiment: $EXP_NAME"
log_info "Number of runs: $NUM_RUNS"

# save_pcpu_queue_stats() {
#     local pcpu_queue_stats_file="$1"
#     local header="$2"
#     echo "$header" >> "$pcpu_queue_stats_file"
#     sudo cat /sys/kernel/debug/pcpu_batch_index >> "$pcpu_queue_stats_file"
# }

pre_exp_setup

for ((j = 0; j < NUM_RUNS; j += 1)); do
    echo
    log_info "############################################################"
    log_info "### Starting Experiment Run: $j / $(($NUM_RUNS - 1)) for EXP: $EXP_NAME"
    log_info "############################################################"

    # --- Per-Run Directory and File Definitions ---
    # HOST (Server) side paths for reports and data
    current_host_reports_dir="${HOST_SETUP_DIR}/reports/${EXP_NAME}-RUN-${j}"
    client_reports_dir_remote="${CLIENT_SETUP_DIR}/reports/${EXP_NAME}-RUN-${j}"

    perf_host_data_file="${current_host_reports_dir}/perf_host_cpu.data"
    iova_ftrace_host_output_file="${current_host_reports_dir}/iova_ftrace_host.txt"
    ebpf_host_stats="${current_host_reports_dir}/ebpf_host_stats.csv"
    host_server_app_log_file="${current_host_reports_dir}/server_app.log"
    client_server_app_log_file="${client_reports_dir_remote}/client_server_app.log"
    host_mlc_log_file="${current_host_reports_dir}/mlc.log"
    perf_kvm_data_file="${current_host_reports_dir}/perf_host_kvm.data"
    perf_sched_data_file="${current_host_reports_dir}/perf_host_sched.data"

    sudo mkdir -p "$current_host_reports_dir"
    $SSH_CLIENT_CMD "sudo mkdir -p '$client_reports_dir_remote'"

    # --- Pre-run cleanup ---
    cleanup

    # --- Add config to reports ---
    save_config_to_report_json "$current_host_reports_dir"

    # save_pcpu_queue_stats "$current_host_reports_dir/pcpu_queue_stats.txt" "after_cleanup"

    # --- Start MLC (Memory Latency Checker) if configured ---
    if [ "$MLC_CORES" != "none" ]; then
        log_info "Starting MLC on cores: $MLC_CORES; logs at $host_mlc_log_file..."
        "$HOST_MLC_DIR/mlc" --loaded_latency -T -d0 -e -k"$MLC_CORES" -j0 -b1g -t10000 -W2 &> "$host_mlc_log_file" &
        log_info "Waiting for MLC to ramp up (30 seconds)..."
        progress_bar 30 1
    else
        log_info "MLC not configured for this run."
    fi
   
    # --- Setup and Start Clients ---
    log_info "Setting up and starting CLIENTS on $CLIENT_SSH_HOST..."
    client_cmd="cd '$CLIENT_SETUP_DIR'; sudo bash setup-envir.sh --dep '$CLIENT_HOME' --intf '$CLIENT_INTF' --ip '$CLIENT_IP' -m '$MTU' -d '$DDIO_ENABLED' -r '$RING_BUFFER_SIZE' --socket-buf '$TCP_SOCKET_BUF_MB' --hwpref 1 --rdma 0 --pfc 0 --ecn 1 --opt 1; "
    client_cmd+="cd '$CLIENT_EXP_DIR'; sudo bash run-tx-netapp-tput.sh --mode server -n '$HOST_NUM_SERVERS' -N '$CLIENT_NUM_CLIENTS'  -o '${EXP_NAME}-RUN-${j}' -p '$INIT_PORT' -c '$CLIENT_CPU_MASK' &> '$client_server_app_log_file'; exec bash"
    $SSH_CLIENT_CMD "screen -dmS client_session sudo bash -c \"$client_cmd\""
    sleep 2

    # --- Setup HOST (Server) Environment ---
    log_info "Setting up HOST server environment..."
    cd "$HOST_SETUP_DIR" || { log_error "Failed to cd to $HOST_SETUP_DIR"; exit 1; }
    sudo bash setup-envir.sh --dep "$HOST_HOME" --intf "$HOST_INTF" --ip "$HOST_IP" -m "$MTU" -d "$DDIO_ENABLED" -r "$RING_BUFFER_SIZE" \
        --socket-buf "$TCP_SOCKET_BUF_MB" --hwpref 1 --rdma 0 --pfc 0 --ecn 1 --opt 1 --nic-bus "$HOST_NIC_BUS"
    cd - > /dev/null # Go back to previous directory silently

    # --- Start HOST (Server) Application ---
    log_info "Waiting for remote servers to start listening on port $INIT_PORT..."
    for i in {1..30}; do
        if $SSH_CLIENT_CMD "ss -tln | grep -q :$INIT_PORT || netstat -tln | grep -q :$INIT_PORT" 2>/dev/null; then
            log_info "Remote servers are up and listening!"
            sleep 2 # Small buffer to ensure all subsequent ports (if NUM_SERVERS > 1) are also bound
            break
        fi
        sleep 1
        if [ "$i" -eq 30 ]; then
            log_error "Timeout waiting for remote servers to start!"
        fi
    done

    log_info "Starting HOST server application; logs at $host_server_app_log_file"
    cd "$HOST_EXP_DIR" || { log_error "Failed to cd to $HOST_EXP_DIR"; exit 1; }
    sudo bash run-tx-netapp-tput.sh --mode client --server-ip "$CLIENT_IP" -n "$HOST_NUM_SERVERS" -N "$CLIENT_NUM_CLIENTS" -o "${EXP_NAME}-RUN-${j}" \
        -p "$INIT_PORT" -c "$HOST_CPU_MASK" --b "$CLIENT_BANDWIDTH" &> "$host_server_app_log_file" & 
    sleep 2 # Allow server app to initialize
    cd - > /dev/null   

    # --- Warmup Phase ---
    # log_info "Warming up experiment (10 seconds)..."
    # progress_bar 10 1
    log_info "Warming up experiment (60 seconds)..."
    progress_bar 60 1

    # save_pcpu_queue_stats "$current_guest_reports_dir/pcpu_queue_stats.txt" "after_warmup"

    # --- Start eBPF Tracers (if enabled) ---
    if [ "$EBPF_TRACING_HOST_ENABLED" -eq 1 ]; then
        log_info "Starting HOST eBPF tracer..."
        echo "current_time: $(date) $(date +%s)"
        sudo taskset -c $HOST_EBPF_TRACING_CORE "$EBPF_HOST_LOADER" -d $CORE_DURATION_S -o "$ebpf_host_stats" &
        sleep 2 # Allow eBPF loaders to initialize
    fi

    # --- Ftrace Setup (Host) ---
    log_info "Configuring HOST ftrace for IOVA logging (Buffer: ${FTRACE_BUFFER_SIZE_KB}KB, Overwrite: ${FTRACE_OVERWRITE_ON_FULL})..."
    sudo echo "$FTRACE_BUFFER_SIZE_KB" > /sys/kernel/debug/tracing/buffer_size_kb
    sudo echo "$FTRACE_OVERWRITE_ON_FULL" > /sys/kernel/debug/tracing/options/overwrite
    sudo echo > /sys/kernel/debug/tracing/trace # Clear buffer
    sudo echo 1 > /sys/kernel/debug/tracing/tracing_on
    log_info "HOSF IOVA ftrace is ON."
    
    # --- Start Main Profiling & Logging Phase ---
    if [ "$PERF_TRACING_HOST_ENABLED" -eq 1 ]; then
        log_info "Starting HOST perf record (CPU profiling)..."
        sudo "$HOST_PERF" record -F 99 -a -g --call-graph dwarf -o "$perf_host_data_file" -- sleep "$PROFILING_LOGGING_DUR_S" &
    fi


    log_info "Starting CLIENT-side logging on $CLIENT_SSH_HOST..."
    client_logging_cmd="cd '$CLIENT_SETUP_DIR'; sudo bash record-host-metrics.sh \
        --dep '$CLIENT_HOME' -o '${EXP_NAME}-RUN-${j}' --dur '$CORE_DURATION_S' \
        --cpu-util 1 -c '$CLIENT_CPU_MASK' --retx 1 --tcplog 0 --bw 1 --flame 0 \
        --pcie 0 --membw 0 --iio 0 --pfc 0 --intf '$CLIENT_INTF' --type 0; exec bash"
    $SSH_CLIENT_CMD "screen -dmS logging_session_client sudo bash -c \"$client_logging_cmd\""

    log_info "Starting HOST-side logging on $HOST_IP..."
    cd "$HOST_SETUP_DIR" || { log_error "Failed to cd to $HOST_SETUP_DIR"; exit 1; }
    sudo bash record-host-metrics.sh --dep "$HOST_RESULTS_DIR" -o "${EXP_NAME}-RUN-${j}" --dur "$CORE_DURATION_S" \
        --cpu-util 1  -c "$HOST_CPU_MASK" --retx 1 --tcplog 0 --bw 1 --flame 0 \
        --pcie 1 --membw 0 --iio 0 --pfc 0 --intf "$HOST_INTF" --type 0

    cd - > /dev/null

    log_info "Logging done."
    log_info "Primary data collection phase on HOST complete."

    # --- Save Ftrace Data (Host) ---
    log_info "Stopping and saving HOST IOVA ftrace data..."
    sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
    sudo cat /sys/kernel/debug/tracing/trace > "$iova_ftrace_host_output_file"
    sudo echo > /sys/kernel/debug/tracing/trace # Clear buffer after saving
    
    head -n 10000 $iova_ftrace_host_output_file > $iova_ftrace_host_output_file.head10000
    tail -n 10000 $iova_ftrace_host_output_file > $iova_ftrace_host_output_file.tail10000
    log_info "HOST IOVA ftrace data saved to $iova_ftrace_host_output_file"

    sudo bash -c "dmesg > ${current_host_reports_dir}/dmesg.txt"
    

    # --- Stop eBPF Tracers (if enabled) ---
    if [ "$EBPF_TRACING_HOST_ENABLED" -eq 1 ]; then
        log_info "Stopping eBPF tracers..."
        echo "current_time: $(date) $(date +%s)"
        host_loader_basename=$(basename "$EBPF_HOST_LOADER")
        sudo pkill -SIGINT -f "$host_loader_basename" 2>/dev/null && log_info "SIGINT sent to HOST eBPF loader." || log_info "WARN: HOST eBPF loader process not found or SIGINT failed."
    fi
 
    # --- Transfer Report Files from Remote Machines ---
    log_info "Transferring report files from CLIENT..."
    # Client files
    if [ "$CLIENT_USE_PASS_AUTH" -eq 1 ]; then
	sshpass -p $CLIENT_SSH_PASSWORD \
	scp ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}:${client_reports_dir_remote}/retx.rpt ${current_host_reports_dir}/client-retx.rpt
	sshpass -p $CLIENT_SSH_PASSWORD \
	scp ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}:${client_server_app_log_file} ${current_host_reports_dir}/client_server_app.log
    else
	scp -i "$CLIENT_SSH_IDENTITY_FILE" \
	"${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}:${client_reports_dir_remote}/retx.rpt" \
        "${current_host_reports_dir}/client-retx.rpt" || log_error "Failed to SCP client retx.rpt"
	scp -i "$CLIENT_SSH_IDENTITY_FILE" \
	"${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}:${client_server_app_log_file}" \
        "${current_host_reports_dir}/client_server_app.log"
    fi

    log_info "Waiting for remote operations and data transfers to settle (original sleep: $(($CORE_DURATION_S * 2))s)..."
    progress_bar $((CORE_DURATION_S * 2)) 2

    sudo bash collect-period-tput.sh "$EXP_NAME-RUN-${j}"

    # --- Post-run cleanup ---
    # cleanup
    log_info "############################################################"
    log_info "### Finished Experiment Run: $j / $(($NUM_RUNS - 1))"
    log_info "############################################################"
    echo # Blank line
done

cleanup
post_exp_cleanup

if [ "$MLC_CORES" != "none" ]; then
    log_info "MLC cores were used. The original script had a second phase for MLC throughput which is currently skipped."
else
    log_info "No MLC instance used, or MLC throughput collection phase skipped."
fi

log_info "Collecting and processing statistics from all runs..."
# The '0' or '1' at the end of collect-tput-stats.py might indicate whether MLC was run. Adjust as needed.
if [ "$MLC_CORES" = "none" ]; then
    sudo python3 tx-collect-tput-stats.py "$EXP_NAME" "$NUM_RUNS" 0
else
    sudo python3 tx-collect-tput-stats.py "$EXP_NAME" "$NUM_RUNS" 0 # TODO: Change back to 1
fi

sync
sleep 1
log_info "Experiment $EXP_NAME finished."
