#!/bin/bash

# Treat unset variables as an error when substituting.
set -uo pipefail

#-------------------------------------------------------------------------------
# CONFIGURATION AND PATHS
#-------------------------------------------------------------------------------
SCRIPT_NAME="run-rdma-tput-experiment"
INIT_PORT=3000
MLC_DURATION_S=100
SERVER_MLC_DIR_REL="mlc/Linux"

FTRACE_BUFFER_SIZE_KB=20000
FTRACE_OVERWRITE_ON_FULL=0 # 0=no overwrite (tracing stops when full), 1=overwrite
PERF_TRACING_ENABLED=0

# --- Base Directory Paths (Relative to respective home directories) ---
SERVER_FandS_REL="viommu/BareMetal-FandS"
SERVER_DEP_REL="viommu/"
CLIENT_FandS_REL="Fast-and-Safe-IO-Memory-Protection"
SERVER_PERF_REL="viommu/linux-6.12.9/tools/perf/perf" # TODO: Siyuan change for your directory

# --- F and S Directory Paths (Relative to respective F and S directories) ---
SERVER_SETUP_DIR_REL="utils"
SERVER_EXP_DIR_REL="utils/tcp"
CLIENT_SETUP_DIR_REL="utils"
CLIENT_EXP_DIR_REL="utils/tcp"

EBPF_SERVER_LOADER_REL="tracing/server_loader" # does not exist make it if needed for bare-metal cases

#-------------------------------------------------------------------------------
# DEFAULT CONFIGURATION AND PATHS EDITABLE BY COMMAND LINE
#-------------------------------------------------------------------------------
# --- Experiment Setup ---
EXP_NAME="tput-test"
NUM_RUNS=1
CORE_DURATION_S=20 # Duration for the main workload
MLC_CORES="none"
EBPF_TRACING_ENABLED=1 #test

# --- Guest (Server) Machine Configuration ---
# GUEST_NIC_BUS="0x08"

# --- Client Machine Configuration ---
CLIENT_HOME="/users/Leshna/"
CLIENT_IP="10.10.1.2"
CLIENT_INTF="eno12409np1"
CLIENT_NUM_CLIENTS=5
CLIENT_CPU_MASK="0,4,8,12,16"
CLIENT_BANDWIDTH="100g"

# --- Server Machine Configuration ---
SERVER_HOME="/users/Leshna"
SERVER_IP="10.10.1.3"
SERVER_INTF="enp23s0f0np0"
SERVER_NUM_SERVERS=5
SERVER_CPU_MASK="0,1,2,3,4"
SERVER_NIC_BUS="0x08"

# --- Network & System Parameters ---
MTU=4000
DDIO_ENABLED=1
RING_BUFFER_SIZE=256
TCP_SOCKET_BUF_MB=1

# --- Remote Access (SSH) Configuration ---
CLIENT_SSH_UNAME="saksham"
CLIENT_SSH_HOST="128.110.220.29" # Public IP or hostname for SSH "genie12.cs.cornell.edu"
CLIENT_SSH_PASSWORD="saksham"
CLIENT_USE_PASS_AUTH=0 # 1 to use password, 0 to use identity file
CLIENT_SSH_IDENTITY_FILE="/home/schai/.ssh/id_ed25519"

CLIENT_EXPECTED_KERNEL="6.12.9"
CLIENT_EXPECTED_IOMMU="intel_iommu=off"

#-------------------------------------------------------------------------------
# Help/usage
#-------------------------------------------------------------------------------
help() {
    echo "Usage: $SCRIPT_NAME"
    echo
    echo "Server Configuration:"
    echo "    [ --server-home <path> (Host home directory) ]"
    echo "    [ --server-ip <ip> (IP address of the host) ]"
    echo "    [ --server-intf <name> (Interface name for the host) ]"
    echo "    [ -n | --server-num <count> (Number of server instances; default: 5) ]"
    echo "    [ -c | --server-cpu-mask <csv> (Server CPU mask, comma-separated; default: 0,1,2,3,4) ]"
    echo "    [ --server-bus <bus> (NIC’s PCI bus number) ]"
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
LONG_OPTS="server-home:,server-ip:,server-intf:,server-num:,server-cpu-mask:,server-bus:,\
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
        --server-home) SERVER_HOME="$2"; shift 2 ;;
        --server-ip) SERVER_IP="$2"; shift 2 ;;
        --server-intf) SERVER_INTF="$2"; shift 2 ;;
        -n | --server-num) SERVER_NUM_SERVERS="$2"; shift 2 ;;
        -c | --server-cpu-mask) SERVER_CPU_MASK="$2"; shift 2 ;;
        --server-bus) SERVER_NIC_BUS="$2"; shift 2 ;;
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
        --ebpf-tracing) EBPF_TRACING_ENABLED="$2"; shift 2 ;;
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

SERVER_SETUP_DIR="${SERVER_HOME}/${SERVER_FandS_REL}/${SERVER_SETUP_DIR_REL}"
EBPF_SERVER_LOADER="${SERVER_HOME}/${SERVER_FandS_REL}/${EBPF_SERVER_LOADER_REL}"
SERVER_EXP_DIR="${SERVER_HOME}/${SERVER_FandS_REL}/${SERVER_EXP_DIR_REL}"
SERVER_MLC_DIR="${SERVER_HOME}/${SERVER_MLC_DIR_REL}"
SERVER_DEP_DIR="${SERVER_HOME}/${SERVER_DEP_REL}"
CLIENT_SETUP_DIR="${CLIENT_HOME}/${CLIENT_FandS_REL}/${CLIENT_SETUP_DIR_REL}"
CLIENT_EXP_DIR="${CLIENT_HOME}/${CLIENT_FandS_REL}/${CLIENT_EXP_DIR_REL}"
SERVER_PERF="${SERVER_HOME}/${SERVER_PERF_REL}"
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
    sudo ethtool --pause $SERVER_INTF tx off rx off
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
    cd "$SERVER_SETUP_DIR"; sudo bash reset-host.sh
    cd -
    
    log_info "--- Post-experiment Cleanup Phase Finished ---"
}


# --- Cleanup Function ---
cleanup() {
    log_info "--- Starting Cleanup Phase ---"

    log_info "Killing local 'loaded_latency', 'iperf', and 'perf record' processes..."
    sudo pkill -9 -f loaded_latency
    sudo pkill -9 -f iperf 

    if [ "$PERF_TRACING_ENABLED" -eq 1 ]; then
        sudo pkill -SIGINT -f "$SERVER_PERF record"
        sleep 1
        sudo pkill -9 -f "$SERVER_PERF record"
    fi

    if [ "$EBPF_TRACING_ENABLED" -eq 1 ]; then
        log_info "Stopping eBPF tracers..."
	    local server_loader_basename
        server_loader_basename=$(basename "$EBPF_SERVER_LOADER")
        cd $(dirname "$EBPF_SERVER_LOADER") || { log_error "Failed to cd to $(dirname "$EBPF_SERVER_LOADER")"; exit 1; }
        make clean
        make
        cd -
	    sudo pkill -SIGINT -f "$server_loader_basename" 2>/dev/null || true
        sudo pkill -9 -f "$server_loader_basename" 2>/dev/null || true
        sleep 1
    fi

    log_info "Terminating screen sessions..."
    $SSH_CLIENT_CMD \
        'screen -ls | grep -E "\.client_session|\.logging_session_client" | cut -d. -f1 | xargs -r -I % screen -S % -X quit'
    $SSH_CLIENT_CMD \
        'sudo pkill -9 -f iperf; screen -wipe || true'

    log_info "Resetting SERVER network interface $SERVER_INTF..."
    sudo ip link set "$SERVER_INTF" down
    sleep 2
    sudo ip link set "$SERVER_INTF" up
    sleep 2
    log_info "--- Cleanup Phase Finished ---"
}

save_config_to_report_json() {
    local report_dir="${1:-$current_server_reports_dir}"
    local config_file="$report_dir/config.json"

    local host_cmdline=$(cat /proc/cmdline)
    local host_kernel=$(uname -r)
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
    "ip": "$SERVER_IP",
    "interface": "$SERVER_INTF",
    "num_servers": "$SERVER_NUM_SERVERS",
    "cpu_mask": "$SERVER_CPU_MASK",
    "nic_bus": "$SERVER_NIC_BUS",
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
  }
}
EOF
}

log_info "Starting experiment: $EXP_NAME"
log_info "Number of runs: $NUM_RUNS"

pre_exp_setup

for ((j = 0; j < NUM_RUNS; j += 1)); do
    echo
    log_info "############################################################"
    log_info "### Starting Experiment Run: $j / $(($NUM_RUNS - 1)) for EXP: $EXP_NAME"
    log_info "############################################################"

    # --- Per-Run Directory and File Definitions ---
    # Server side paths for reports and data
    current_server_reports_dir="${SERVER_SETUP_DIR}/reports/${EXP_NAME}-RUN-${j}"
    client_reports_dir_remote="${CLIENT_SETUP_DIR}/reports/${EXP_NAME}-RUN-${j}"
    
    iova_ftrace_server_output_file="${current_server_reports_dir}/iova_ftrace_server.txt"
    ebpf_server_stats="${current_server_reports_dir}/ebpf_server_stats.csv"
    server_app_log_file="${current_server_reports_dir}/server_app.log"
    server_mlc_log_file="${current_server_reports_dir}/mlc.log"
    server_perf_data_file="${current_server_reports_dir}/perf_cpu.data"
    
    sudo mkdir -p "$current_server_reports_dir"
    $SSH_CLIENT_CMD "sudo mkdir -p '$client_reports_dir_remote'"


    # --- Pre-run cleanup ---
    cleanup

    # --- Add config to reports ---
    save_config_to_report_json "$current_server_reports_dir"

    # --- Start MLC (Memory Latency Checker) if configured ---
    if [ "$MLC_CORES" != "none" ]; then
        log_info "Starting MLC on cores: $MLC_CORES; logs at $server_mlc_log_file..."
        "$SERVER_MLC_DIR/mlc" --loaded_latency -T -d0 -e -k"$MLC_CORES" -j0 -b1g -t10000 -W2 &> "$server_mlc_log_file" &
        log_info "Waiting for MLC to ramp up (30 seconds)..."
        progress_bar 30 1
    else
        log_info "MLC not configured for this run."
    fi

    # --- Setup Server Environment ---
    log_info "Setting up server environment..."
    cd "$SERVER_SETUP_DIR" || { log_error "Failed to cd to $SERVER_SETUP_DIR"; exit 1; }
    sudo bash setup-envir.sh --dep "$SERVER_DEP_DIR" --intf "$SERVER_INTF" --ip "$SERVER_IP" -m "$MTU" -d "$DDIO_ENABLED" -r "$RING_BUFFER_SIZE" \
      --socket-buf "$TCP_SOCKET_BUF_MB" --hwpref 1 --rdma 0 --pfc 0 --ecn 1 --opt 1 --nic-bus "$SERVER_NIC_BUS"
    sudo bash setup-host.sh -m "$MTU" --socket-buf "$TCP_SOCKET_BUF_MB" --hwpref 1 --rdma 0 --ecn 1
    cd - > /dev/null # Go back to previous directory silently

    # --- Start Server Application ---
    log_info "Starting server application; logs at $server_app_log_file"
    cd "$SERVER_EXP_DIR" || { log_error "Failed to cd to $SERVER_EXP_DIR"; exit 1; }
    sudo bash run-netapp-tput.sh --mode server -n "$SERVER_NUM_SERVERS" -N "$CLIENT_NUM_CLIENTS" -o "${EXP_NAME}-RUN-${j}" \
        -p "$INIT_PORT" -c "$SERVER_CPU_MASK" &> "$server_app_log_file" &
    SERVER_PID=$!
    echo "SERVER_PID=$SERVER_PID" >> "$server_app_log_file"
    ps -o pid,cmd,psr,pcpu --pid $SERVER_PID >> "$server_app_log_file"
    sleep 2 # Allow server app to initialize
    cd - > /dev/null

    # --- Setup and Start Clients ---
    log_info "Setting up and starting CLIENTS on $CLIENT_SSH_HOST..."
    client_cmd="cd '$CLIENT_SETUP_DIR'; sudo bash setup-envir.sh --dep '$CLIENT_HOME' --intf '$CLIENT_INTF' --ip '$CLIENT_IP' -m '$MTU' -d '$DDIO_ENABLED' -r '$RING_BUFFER_SIZE' --socket-buf '$TCP_SOCKET_BUF_MB' --hwpref 1 --rdma 0 --pfc 0 --ecn 1 --opt 1; "
    client_cmd+="cd '$CLIENT_EXP_DIR'; sudo bash run-netapp-tput.sh --mode client --server-ip '$SERVER_IP' -n '$SERVER_NUM_SERVERS' -N '$CLIENT_NUM_CLIENTS'  -o '${EXP_NAME}-RUN-${j}' -p '$INIT_PORT' -c '$CLIENT_CPU_MASK' -b '$CLIENT_BANDWIDTH'; exec bash"
    $SSH_CLIENT_CMD "screen -dmS client_session sudo bash -c \"$client_cmd\""

    # --- Warmup Phase ---
    log_info "Warming up experiment (60 seconds)..."
    progress_bar 60 1

    
    # --- Start eBPF Tracers (if enabled) ---
    if [ "$EBPF_TRACING_ENABLED" -eq 1 ]; then
        log_info "Starting server eBPF tracer..."
        sudo taskset -c 13 "$EBPF_SERVER_LOADER" -o "$ebpf_server_stats" &
        sleep 2 # Allow eBPF loaders to initialize
    fi
   
    # --- Ftrace Setup (Guest & Host) ---
    log_info "Configuring server ftrace for IOVA logging (Buffer: ${FTRACE_BUFFER_SIZE_KB}KB, Overwrite: ${FTRACE_OVERWRITE_ON_FULL})..."
    sudo echo "$FTRACE_BUFFER_SIZE_KB" > /sys/kernel/debug/tracing/buffer_size_kb
    sudo echo "$FTRACE_OVERWRITE_ON_FULL" > /sys/kernel/debug/tracing/options/overwrite
    sudo echo > /sys/kernel/debug/tracing/trace # Clear buffer
    sudo echo 1 > /sys/kernel/debug/tracing/tracing_on
    log_info "server IOVA ftrace is ON."

    # --- Start Main Profiling & Logging Phase ---
     if [ "$PERF_TRACING_ENABLED" -eq 1 ]; then
        log_info "Starting perf record (CPU profiling)..."
        sudo "$SERVER_PERF" record -F 99 -a -g --call-graph dwarf -o "$server_perf_data_file" -- sleep "$PROFILING_LOGGING_DUR_S" &
    fi

    log_info "Starting CLIENT-side logging on $CLIENT_SSH_HOST..."
    client_logging_cmd="cd '$CLIENT_SETUP_DIR'; sudo bash record-host-metrics.sh \
        --dep '$CLIENT_HOME' -o '${EXP_NAME}-RUN-${j}' --dur '$CORE_DURATION_S' \
        --cpu-util 1 -c '$CLIENT_CPU_MASK' --retx 1 --tcplog 0 --bw 1 --flame 0 \
        --pcie 0 --membw 0 --iio 0 --pfc 0 --intf '$CLIENT_INTF' --type 0; exec bash"
    $SSH_CLIENT_CMD "screen -dmS logging_session_client sudo bash -c \"$client_logging_cmd\""

    log_info "Starting server logging..."
    cd "$SERVER_SETUP_DIR" || { log_error "Failed to cd to $SERVER_SETUP_DIR"; exit 1; }
    sudo bash record-host-metrics.sh --dep "$SERVER_DEP_DIR" -o "${EXP_NAME}-RUN-${j}" \
    --dur "$CORE_DURATION_S" --cpu-util 1 -c "$SERVER_CPU_MASK" --retx 1 --tcplog 0 --bw 1 --flame 1 \
    --pcie 1 --membw 0 --iio 0 --pfc 0 --intf "$SERVER_INTF" --type 0
    cd - > /dev/null

    log_info "Logging done."
    log_info "Primary data collection phase on SERVER complete."

    # --- Save Ftrace Data (Guest & Host) ---
    log_info "Stopping and saving server IOVA ftrace data..."
    sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
    sudo cat /sys/kernel/debug/tracing/trace > "$iova_ftrace_server_output_file"
    sudo echo > /sys/kernel/debug/tracing/trace # Clear buffer after saving
    log_info "server IOVA ftrace data saved to $iova_ftrace_server_output_file"

    sudo bash -c "dmesg > ${current_server_reports_dir}/dmesg.txt"

    # --- Stop eBPF Tracers (if enabled) ---
    if [ "$EBPF_TRACING_ENABLED" -eq 1 ]; then
        log_info "Stopping eBPF tracers..."
        local server_loader_basename # Ensure local scope if not already
        server_loader_basename=$(basename "$EBPF_SERVER_LOADER")
        sudo pkill -SIGINT -f "$server_loader_basename" 2>/dev/null && log_info "SIGINT sent to SERVER eBPF loader." || log_info "WARN: SERVER eBPF loader process not found or SIGINT failed."
    fi

 
    # --- Transfer Report Files from Remote Machines --- TODO: FIX THESE
    log_info "Transferring report files from CLIENT"
    if [ "$CLIENT_USE_PASS_AUTH" -eq 1 ]; then
	    sshpass -p $CLIENT_SSH_PASSWORD \
        scp ${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}:$client_reports_dir_remote/retx.rpt $current_server_reports_dir/retx.rpt
    else
	    scp -i "$CLIENT_SSH_IDENTITY_FILE" \
        "${CLIENT_SSH_UNAME}@${CLIENT_SSH_HOST}:$client_reports_dir_remote/retx.rpt" "$current_server_reports_dir/retx.rpt"
    fi

    log_info "Waiting for remote operations and data transfers to settle (original sleep: $(($CORE_DURATION_S * 2))s)..."
    progress_bar $((CORE_DURATION_S * 2)) 2

    # --- Post-run cleanup ---
    cleanup
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
    sudo python3 collect-tput-stats.py "$EXP_NAME" "$NUM_RUNS" 0
else
    sudo python3 collect-tput-stats.py "$EXP_NAME" "$NUM_RUNS" 0 # TODO: Change back to 1
fi

log_info "Experiment $EXP_NAME finished."
