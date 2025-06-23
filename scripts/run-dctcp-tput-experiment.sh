#!/bin/bash

SCRIPT_NAME="run-rdma-tput-experiment"

help() {
    echo "Usage: $SCRIPT_NAME"
    echo "    [ -H | --home (Guest home directory; default: /home/schai) ]"
    echo "    [ -D | --home_client (Client home directory; default: /home/saksham) ]"
    echo "    [ --home_host (Host home directory; default: /home/saksham) ]"
    echo "    [ -S | --server (IP address of the server/guest; default: 192.168.11.127) ]"
    echo "    [ --server_intf (Interface name for the server/guest; default: enp8s0) ]"
    echo "    [ --num_servers (Number of server instances; default: 5) ]"
    echo "    [ -C | --client (IP address of the client; default: 192.168.11.125) ]"
    echo "    [ --client_intf (Interface name for the client; default: ens2f1np1) ]"
    echo "    [ --num_clients (Number of client instances; default: 5) ]"
    echo "    [ --host (IP address of the host; default: 192.168.123.1) ]"
    echo "    [ --host_intf (Interface name for the host; default: enp101s0f1np1) ]"
    echo "    [ -E | --exp (Experiment name for output directories; default: tput-test) ]"
    echo "    [ -M | --MTU (MTU size: 256/512/1024/2048/4096; default: 4000) ]"
    echo "    [ -d | --ddio (DDIO enabled: 0/1; default: 1) ]"
    echo "    [ -c | --cpu_mask (Guest CPU mask, comma-separated; default: 0,1,2,3,4) ]"
    echo "    [ -m | --cpu_mask_client (Client CPU mask, comma-separated; default: 0,4,8,12,16) ]"
    echo "    [ -b | --bandwidth (Client bandwidth in bits/sec, e.g., 100g; default: 100g) ]"
    echo "    [ --mlc_cores (MLC cores, comma-separated, 'none' to skip; default: none) ]"
    echo "    [ --ring_buffer (NIC Rx ring buffer size; default: 256) ]"
    echo "    [ --buf (TCP socket buffer size in MB; default: 1) ]"
    echo "    [ --dur (Core experiment duration in seconds; default: 20) ]"
    echo "    [ --num_runs (Number of experiment repetitions; default: 1) ]"
    echo "    [ --ebpf_tracing (Enable eBPF tracing: 0/1; default: 0) ]"
    echo "    [ -h | --help ]"
    exit 2
}

#-------------------------------------------------------------------------------
# DEFAULT CONFIGURATION AND PATHS
#-------------------------------------------------------------------------------
# --- Experiment Setup ---
DEFAULT_EXP_NAME="tput-test"
DEFAULT_NUM_RUNS=1
DEFAULT_CORE_DURATION_S=20 # Duration for the main workload
DEFAULT_INIT_PORT=3000

# --- Guest (Server) Machine Configuration ---
DEFAULT_GUEST_HOME="/home/schai"
DEFAULT_GUEST_IP="10.10.1.50"
DEFAULT_GUEST_INTF="enp8s0np1"
DEFAULT_GUEST_NUM_SERVERS=5
DEFAULT_GUEST_CPU_MASK="0,1,2,3,4"

# --- Client Machine Configuration ---
DEFAULT_CLIENT_HOME="/users/Leshna/"
DEFAULT_CLIENT_IP="10.10.1.2"
DEFAULT_CLIENT_INTF="eno12409np1"
DEFAULT_CLIENT_NUM_CLIENTS=5
DEFAULT_CLIENT_CPU_MASK="0,4,8,12,16"
DEFAULT_CLIENT_BANDWIDTH="100g"
CLIENT_SSH_UNAME="Leshna"
CLIENT_SSH_IP="128.110.220.127"

# --- Host Machine Configuration ---
DEFAULT_HOST_HOME="/users/Leshna"
DEFAULT_HOST_IP="192.168.122.1"
DEFAULT_HOST_INTF="enp101s0f1np1"
HOST_SSH_UNAME="Leshna"

# --- Network & System Parameters ---
DEFAULT_MTU=4000
DEFAULT_DDIO_ENABLED=1
DEFAULT_RING_BUFFER_SIZE=256
DEFAULT_TCP_SOCKET_BUF_MB=1

# --- MLC (Memory Latency Checker) Configuration ---
DEFAULT_MLC_CORES="none"
DEFAULT_MLC_DURATION_S=100
GUEST_MLC_DIR_REL="mlc/Linux"

# Ftrace settings
FTRACE_BUFFER_SIZE_KB=20000
FTRACE_OVERWRITE_ON_FULL=0 # 0=no overwrite (tracing stops when full), 1=overwrite

# --- Base Directory Paths (Relative to respective home directories) ---
GUEST_SETUP_DIR_REL="viommu/utils"
GUEST_EXP_DIR_REL="$GUEST_SETUP_DIR_REL/tcp"
CLIENT_SETUP_DIR_REL="Fast-and-Safe-IO-Memory-Protection/utils"
CLIENT_EXP_DIR_REL="$CLIENT_SETUP_DIR_REL/tcp"
HOST_EXP_DIR_REL="viommu"
HOST_SETUP_UTILS_DIR_REL="Fast-and-Safe-IO-Memory-Protection/utils" # For setup-envir.sh on host

# --- Profiling & Tracing Tools ---
GUEST_PERF_EXECUTABLE_DEFAULT="$DEFAULT_GUEST_HOME/linux-6.12.9/tools/perf/perf"
HOST_PERF_EXECUTABLE_REL_TO_EXP_DIR="linux-6.12.9/tools/perf/perf"
DEFAULT_EBPF_TRACING_ENABLED=0 #test
EBPF_GUEST_LOADER_DEFAULT="$DEFAULT_GUEST_HOME/viommu/tracing/guest_loader"
EBPF_HOST_LOADER_DEFAULT="$DEFAULT_HOST_HOME/viommu/iommu-vm/tracing/host_loader"
EBPF_GUEST_BASE_TRACE_DIR_REL="viommu/ebpf_traces"
EBPF_HOST_BASE_TRACE_DIR_REL="ebpf_traces" # Relative to HOST_EXP_DIR


identity_file="/home/schai/.ssh/id_ed25519"

#-------------------------------------------------------------------------------
# SECTION 3: COMMAND-LINE ARGUMENT PARSING
#-------------------------------------------------------------------------------
SHORT_OPTS="H:D:S:C:E:M:d:c:m:b:h"
LONG_OPTS="home:,home_client:,home_host:,server:,client:,host:,\
server_intf:,client_intf:,host_intf:,\
num_servers:,num_clients:,\
exp:,MTU:,ddio:,cpu_mask:,cpu_mask_client:,mlc_cores:,\
ring_buffer:,bandwidth:,buf:,dur:,num_runs:,ebpf_tracing:,help"

PARSED_OPTS=$(getopt -a -n "$SCRIPT_NAME" --options "$SHORT_OPTS" --longoptions "$LONG_OPTS" -- "$@")
VALID_ARGUMENTS=$#
if [ "$VALID_ARGUMENTS" -eq 0 ]; then
    help
fi
eval set -- "$PARSED_OPTS"

# Initialize variables with defaults
guest_home="$DEFAULT_GUEST_HOME"
client_home="$DEFAULT_CLIENT_HOME"
host_home="$DEFAULT_HOST_HOME"

server_ip="$DEFAULT_GUEST_IP"
guest_intf="$DEFAULT_GUEST_INTF"
num_servers="$DEFAULT_GUEST_NUM_SERVERS"

client_ip="$DEFAULT_CLIENT_IP"
client_intf="$DEFAULT_CLIENT_INTF"
num_clients="$DEFAULT_CLIENT_NUM_CLIENTS"

host_ip="$DEFAULT_HOST_IP"
host_intf="$DEFAULT_HOST_INTF"

exp_name="$DEFAULT_EXP_NAME"
mtu="$DEFAULT_MTU"
ddio_enabled="$DEFAULT_DDIO_ENABLED"
guest_cpu_mask="$DEFAULT_GUEST_CPU_MASK"
client_cpu_mask="$DEFAULT_CLIENT_CPU_MASK"
client_bandwidth="$DEFAULT_CLIENT_BANDWIDTH"
mlc_cores="$DEFAULT_MLC_CORES"
ring_buffer_size="$DEFAULT_RING_BUFFER_SIZE"
tcp_socket_buf_mb="$DEFAULT_TCP_SOCKET_BUF_MB"
core_duration_s="$DEFAULT_CORE_DURATION_S"
num_runs="$DEFAULT_NUM_RUNS"
ebpf_tracing_enabled="$DEFAULT_EBPF_TRACING_ENABLED"

# Tool paths using defaults that might be updated if $guest_home changes
guest_perf_executable="$GUEST_PERF_EXECUTABLE_DEFAULT" # Will be updated

while :; do
    case "$1" in
        -H | --home) guest_home="$2"; shift 2 ;;
        -D | --home_client) client_home="$2"; shift 2 ;;
        --home_host) host_home="$2"; shift 2 ;;
        -S | --server) server_ip="$2"; shift 2 ;;
        -C | --client) client_ip="$2"; shift 2 ;;
        --host) host_ip="$2"; shift 2 ;;
        --server_intf) guest_intf="$2"; shift 2 ;;
        --client_intf) client_intf="$2"; shift 2 ;;
        --host_intf) host_intf="$2"; shift 2 ;;
        --num_servers) num_servers="$2"; shift 2 ;;
        --num_clients) num_clients="$2"; shift 2 ;;
        -E | --exp) exp_name="$2"; shift 2 ;;
        -M | --MTU) mtu="$2"; shift 2 ;;
        -d | --ddio) ddio_enabled="$2"; shift 2 ;;
        -c | --cpu_mask) guest_cpu_mask="$2"; shift 2 ;;
        -m | --cpu_mask_client) client_cpu_mask="$2"; shift 2 ;;
        -b | --bandwidth) client_bandwidth="$2"; shift 2 ;;
        --mlc_cores) mlc_cores="$2"; shift 2 ;;
        --ring_buffer) ring_buffer_size="$2"; shift 2 ;;
        --buf) tcp_socket_buf_mb="$2"; shift 2 ;;
        --dur) core_duration_s="$2"; shift 2 ;;
        --num_runs) num_runs="$2"; shift 2 ;;
        --ebpf_tracing) ebpf_tracing_enabled="$2"; shift 2 ;;
        -h | --help) help ;;
        --) shift; break ;;
        *) echo "Unexpected option: $1"; help ;;
    esac
done

guest_setup_dir="${guest_home}/${GUEST_SETUP_DIR_REL}"
guest_exp_dir="${guest_home}/${GUEST_EXP_DIR_REL}"
guest_mlc_dir="${guest_home}/${GUEST_MLC_DIR_REL}"
guest_perf_executable="${guest_home}/linux-6.12.9/tools/perf/perf"

client_setup_dir="${client_home}/${CLIENT_SETUP_DIR_REL}"
client_exp_dir="${client_home}/${CLIENT_EXP_DIR_REL}"

host_exp_dir="${host_home}/${HOST_EXP_DIR_REL}"
host_setup_utils_dir="${host_exp_dir}/${HOST_SETUP_UTILS_DIR_REL}"
host_perf_executable="${host_exp_dir}/${HOST_PERF_EXECUTABLE_REL_TO_EXP_DIR}" # Path on host for perf

ebpf_guest_loader="${guest_home}/viommu/tracing/guest_loader"
ebpf_host_loader="${host_home}/viommu/iommu-vm/tracing/host_loader"
profiling_logging_duration_s=$((core_duration_s))

log_info() {
    echo "[INFO] - $1"
}

log_error() {
    echo "[ERROR] - $1" >&2
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

# --- Cleanup Function ---
cleanup() {
    log_info "--- Starting Cleanup Phase ---"

    log_info "Killing local 'loaded_latency', 'iperf', and 'perf record' processes..."
    sudo pkill -9 -f loaded_latency
    sudo pkill -9 -f iperf 
    # sudo pkill -SIGINT -f "$guest_perf_executable record"
    # sleep 1
    # sudo pkill -9 -f "$guest_perf_executable record"

    # log_info "Killing remote 'perf record' on HOST ($host_ip)..."
    # sshpass -p "$HOST_SSH_PASSWORD" ssh "$HOST_SSH_UNAME@$host_ip" \
      #  "sudo pkill -SIGINT -f '$host_perf_executable record'; sleep 1; sudo pkill -9 -f '$host_perf_executable record'"

    if [ "$ebpf_tracing_enabled" -eq 1 ]; then
        log_info "Stopping eBPF tracers..."
        local guest_loader_basename
        guest_loader_basename=$(basename "$ebpf_guest_loader")
	local host_loader_basename
        host_loader_basename=$(basename "$ebpf_host_loader")
	
	sudo pkill -SIGINT -f "$guest_loader_basename" 2>/dev/null || true
        sshpass -p "$HOST_SSH_PASSWORD" ssh "$HOST_SSH_UNAME@$host_ip" \
        "sudo pkill -SIGINT -f '$host_loader_basename'; sleep 5; sudo pkill -9 -f '$host_loader_basename'; screen -S ebpf_host_tracer -X quit || true"
	
	sleep 5
        sudo pkill -9 -f "$guest_loader_basename" 2>/dev/null || true
    fi

    log_info "Terminating screen sessions..."
    ssh -i "$identity_file" "$CLIENT_SSH_UNAME@$CLIENT_SSH_IP" \
        'screen -ls | grep -E "\.client_session|\.logging_session_client" | cut -d. -f1 | xargs -r -I % screen -S % -X quit'
    ssh -i "$identity_file" "$CLIENT_SSH_UNAME@$CLIENT_SSH_IP" \
        'sudo pkill -9 -f iperf; screen -wipe || true'
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" \
	'screen -ls | grep -E "\.host_session|\.perf_screen|\.logging_session_host" | cut -d. -f1 | xargs -r -I % screen -S % -X quit'
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" \
        'screen -wipe || true'

    log_info "Resetting GUEST ftrace..."
    sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
    sudo echo 0 > /sys/kernel/debug/tracing/options/overwrite
    sudo echo 20000 > /sys/kernel/debug/tracing/buffer_size_kb

    log_info "Resetting HOST ftrace..."
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" \
    "sudo bash -c 'echo 0 > /sys/kernel/debug/tracing/tracing_on; \
                    echo 0 > /sys/kernel/debug/tracing/options/overwrite; \
                    echo 20000 > /sys/kernel/debug/tracing/buffer_size_kb'"

    log_info "Resetting GUEST network interface $guest_intf..."
    sudo ip link set "$guest_intf" down
    sleep 2
    sudo ip link set "$guest_intf" up
    sleep 2
    log_info "--- Cleanup Phase Finished ---"
}


log_info "Starting experiment: $exp_name"
log_info "Number of runs: $num_runs"

for ((j = 0; j < num_runs; j += 1)); do
    echo
    log_info "############################################################"
    log_info "### Starting Experiment Run: $j / $(($num_runs - 1)) for EXP: $exp_name"
    log_info "############################################################"

    # --- Per-Run Directory and File Definitions ---
    # Guest (Server) side paths for reports and data
    current_guest_reports_dir="${guest_setup_dir}/reports/${exp_name}-RUN-${j}"
    host_reports_dir_remote="${host_exp_dir}/reports/${exp_name}-RUN-${j}"
    client_reports_dir_remote="${client_setup_dir}/reports/${exp_name}-RUN-${j}"

    perf_guest_data_file="${current_guest_reports_dir}/perf_guest_cpu.data"
    iova_ftrace_guest_output_file="${current_guest_reports_dir}/iova_ftrace_guest.txt"
    ebpf_guest_stats="${current_guest_reports_dir}/ebpf_guest_stats.csv"
    guest_ebpf_events_file="${current_guest_reports_dir}/ebpf_events.bin"
    guest_ebpf_stack_trace="${current_guest_reports_dir}/ebpf_stack_trace.bin"
    guest_server_app_log_file="${current_guest_reports_dir}/server_app.log"
    guest_mlc_log_file="${current_guest_reports_dir}/mlc.log"
    perf_host_data_file_remote="${host_reports_dir_remote}/perf_host_cpu.data"
    iova_ftrace_host_output_file_remote="${host_reports_dir_remote}/iova_ftrace_host.txt"
    ebpf_host_stats="${host_reports_dir_remote}/ebpf_host_stats.csv"
    host_ebpf_events_file="${host_reports_dir_remote}/ebpf_host_events.bin"
    host_ebpf_stack_trace="${host_reports_dir_remote}/ebpf_host_stack_trace.bin"


    sudo mkdir -p "$current_guest_reports_dir"
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" "sudo mkdir -p '$host_reports_dir_remote'"


    # --- Pre-run cleanup ---
    cleanup

    # --- Start MLC (Memory Latency Checker) if configured ---
    if [ "$mlc_cores" != "none" ]; then
        log_info "Starting MLC on cores: $mlc_cores..."
        "$guest_mlc_dir/mlc" --loaded_latency -T -d0 -e -k"$mlc_cores" -j0 -b1g -t10000 -W2 &> "$guest_mlc_log_file" &
        log_info "Waiting for MLC to ramp up (30 seconds)..."
        progress_bar 30 1
    else
        log_info "MLC not configured for this run."
    fi

    # --- Setup Guest (Server) Environment ---
    log_info "Setting up GUEST server environment..."
    cd "$guest_setup_dir" || { log_error "Failed to cd to $guest_setup_dir"; exit 1; }
    sudo bash setup-envir-unmodified.sh -i "$guest_intf" -a "$server_ip" -m "$mtu" -d "$ddio_enabled" \
        --ring_buffer "$ring_buffer_size" --buf "$tcp_socket_buf_mb" -f 1 -r 0 -p 0 -e 1 -o 1
    cd - > /dev/null # Go back to previous directory silently

     # --- Setup Host Environment ---
    log_info "Setting up HOST environment on $host_ip..."
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" \
        "screen -dmS host_session sudo bash -c \"cd '$host_setup_utils_dir'; sudo bash setup-envir.sh -m '$mtu' -d '$ddio_enabled' --ring_buffer '$ring_buffer_size' --buf '$tcp_socket_buf_mb' -f 1 -r 0 -p 0 -e 1 -o 1; exec bash\""

    # --- Start Guest (Server) Application ---
    log_info "Starting GUEST server application..."
    cd "$guest_exp_dir" || { log_error "Failed to cd to $guest_exp_dir"; exit 1; }
    sudo bash run-netapp-tput.sh -m server -S "$num_servers" -o "${exp_name}-RUN-${j}" \
        -p "$init_port" -c "$guest_cpu_mask" &> "$guest_server_app_log_file" &
    sleep 2 # Allow server app to initialize
    cd - > /dev/null

   
    # --- Ftrace Setup (Guest & Host) ---
    log_info "Configuring GUEST ftrace for IOVA logging (Buffer: ${FTRACE_BUFFER_SIZE_KB}KB, Overwrite: ${FTRACE_OVERWRITE_ON_FULL})..."
    sudo echo "$FTRACE_BUFFER_SIZE_KB" > /sys/kernel/debug/tracing/buffer_size_kb
    sudo echo "$FTRACE_OVERWRITE_ON_FULL" > /sys/kernel/debug/tracing/options/overwrite
    sudo echo > /sys/kernel/debug/tracing/trace # Clear buffer
    sudo echo 1 > /sys/kernel/debug/tracing/tracing_on
    log_info "GUEST IOVA ftrace is ON."

    log_info "Configuring HOST ftrace for IOVA logging on $host_ip..."
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" \
    "sudo bash -c 'sudo echo '$FTRACE_BUFFER_SIZE_KB' > /sys/kernel/debug/tracing/buffer_size_kb; \
         sudo echo '$FTRACE_OVERWRITE_ON_FULL' > /sys/kernel/debug/tracing/options/overwrite; \
         sudo echo > /sys/kernel/debug/tracing/trace; \
         sudo echo 1 > /sys/kernel/debug/tracing/tracing_on'"
    log_info "HOST IOVA ftrace is ON."



    # --- Setup and Start Clients ---
    log_info "Setting up and starting CLIENTS on $CLIENT_SSH_HOSTNAME..."
    client_cmd="cd '$client_setup_dir'; sudo bash setup-envir.sh -i '$client_intf' -a '$client_ip' -m '$mtu' -d '$ddio_enabled' --ring_buffer '$ring_buffer_size' --buf '$tcp_socket_buf_mb' -f 1 -r 0 -p 0 -e 1 -o 1; "
    client_cmd+="cd '$client_exp_dir'; sudo bash run-netapp-tput.sh -m client -a '$server_ip' -C '$num_clients' -S '$num_servers' -o '${exp_name}-RUN-${j}' -p '$init_port' -c '$client_cpu_mask' -b '$client_bandwidth'; exec bash"
    ssh -i "$identity_file" "$CLIENT_SSH_UNAME@$CLIENT_SSH_IP" "screen -dmS client_session sudo bash -c \"$client_cmd\""

    # --- Warmup Phase ---
    log_info "Warming up experiment (10 seconds)..."
    progress_bar 10 1

    # --- Start eBPF Tracers (if enabled) ---
    if [ "$ebpf_tracing_enabled" -eq 1 ]; then
        log_info "Starting GUEST eBPF tracer..."
        sudo taskset -c 13 "$ebpf_guest_loader" -o "$ebpf_guest_stats" &
        log_info "Starting HOST eBPF tracer on $host_ip..."
        host_loader_cmd="sudo taskset -c 33 $ebpf_host_loader -o $ebpf_host_stats"
        sshpass -p "$HOST_SSH_PASSWORD" ssh "$HOST_SSH_UNAME@$host_ip" "screen -dmS ebpf_host_tracer sudo bash -c \"$host_loader_cmd\""
        sleep 2 # Allow eBPF loaders to initialize
    fi

    # --- Start Main Profiling & Logging Phase ---
    # log_info "Starting GUEST perf record (CPU profiling)..."
    # sudo "$guest_perf_executable" record -F 99 -a -g --call-graph dwarf -o "$perf_guest_data_file" -- sleep "$profiling_logging_duration_s" &
    # log_info "Starting HOST perf record (CPU profiling) on $host_ip..."
    # host_perf_cmd="cd '$host_exp_dir'; sudo '$host_perf_executable' record -F 99 -a -g --call-graph dwarf -o '$perf_host_data_file_remote' -- sleep '$profiling_logging_duration_s'; exec bash"
    # sshpass -p "$HOST_SSH_PASSWORD" ssh "$HOST_SSH_UNAME@$host_ip" "screen -dmS perf_screen sudo bash -c \"$host_perf_cmd\""

    log_info "Starting CLIENT-side logging on $CLIENT_SSH_HOSTNAME..."
    client_logging_cmd="cd '$client_setup_dir'; sudo bash record-host-metrics.sh -f 0 -t 1 -i '$client_intf' -o '${exp_name}-RUN-${j}' --type 0 --cpu_util 1 --retx 1 --pcie 0 --membw 0 --dur '$core_duration_s' --cores '$client_cpu_mask'; exec bash"
    ssh -i "$identity_file" "$CLIENT_SSH_UNAME@$CLIENT_SSH_IP" "screen -dmS logging_session_client sudo bash -c \"$client_logging_cmd\""

    log_info "Starting HOST-side logging on $host_ip..."
    host_logging_cmd="cd '$host_exp_dir'; sudo bash record-metrics.sh -f 0 -I 1 -t 1 -o '${exp_name}-RUN-${j}' --type 0 --cpu_util 1 --pcie 1 --membw 1 --dur '$core_duration_s'; exec bash"
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" "screen -dmS logging_session_host sudo bash -c \"$host_logging_cmd\""

    log_info "Starting GUEST-side (server) logging..."
    cd "$guest_setup_dir" || { log_error "Failed to cd to $guest_setup_dir"; exit 1; }
    sudo bash record-host-metrics.sh -f 0 -I 1 -t 1 -i "$guest_intf" -o "${exp_name}-RUN-${j}" \
        --type 0 --cpu_util 1 --pcie 1 --membw 1 --dur "$core_duration_s" --cores "$guest_cpu_mask" 
    cd - > /dev/null

    log_info "Logging done."
    log_info "Primary data collection phase on GUEST complete."

    # --- Save Ftrace Data (Guest & Host) ---
    log_info "Stopping and saving GUEST IOVA ftrace data..."
    sudo echo 0 > /sys/kernel/debug/tracing/tracing_on
    sudo cat /sys/kernel/debug/tracing/trace > "$iova_ftrace_guest_output_file"
    sudo echo > /sys/kernel/debug/tracing/trace # Clear buffer after saving
    log_info "GUEST IOVA ftrace data saved to $iova_ftrace_guest_output_file"

    log_info "Stopping and saving HOST IOVA ftrace data on $host_ip..."
    ssh -i "$identity_file" "$HOST_SSH_UNAME@$host_ip" \
        "sudo bash -c 'sudo echo 0 > /sys/kernel/debug/tracing/tracing_on; \
         sudo cat /sys/kernel/debug/tracing/trace > '$iova_ftrace_host_output_file_remote'; \
         sudo echo > /sys/kernel/debug/tracing/trace'"

    # --- Stop eBPF Tracers (if enabled) ---
    if [ "$ebpf_tracing_enabled" -eq 1 ]; then
        log_info "Stopping eBPF tracers..."
        local guest_loader_basename # Ensure local scope if not already
        guest_loader_basename=$(basename "$ebpf_guest_loader")
        sudo pkill -SIGINT -f "$guest_loader_basename" 2>/dev/null && log_info "SIGINT sent to GUEST eBPF loader." || log_info "WARN: GUEST eBPF loader process not found or SIGINT failed."
        local host_loader_basename
        host_loader_basename=$(basename "$ebpf_host_loader")
        sshpass -p "$HOST_SSH_PASSWORD" ssh "$HOST_SSH_UNAME@$host_ip" "sudo pkill -SIGINT -f '$host_loader_basename'"
    fi

 
    # --- Transfer Report Files from Remote Machines ---
    log_info "Transferring report files from CLIENT and HOST..."
    # Client files
    scp -i "$identity_file" \
	"${CLIENT_SSH_UNAME}@${CLIENT_SSH_IP}:${client_reports_dir_remote}/retx.rpt" \
        "${current_guest_reports_dir}/client-retx.rpt" || log_error "Failed to SCP client retx.rpt"

    # Host files
    scp -i "$identity_file" \
        "${HOST_SSH_UNAME}@${host_ip}:${host_reports_dir_remote}/retx.rpt" \
        "${current_guest_reports_dir}/host-retx.rpt" || log_error "Failed to SCP host retx.rpt"
    scp -i "$identity_file" \
        "${HOST_SSH_UNAME}@${host_ip}:${host_reports_dir_remote}/pcie.rpt" \
        "${current_guest_reports_dir}/host-pcie.rpt" || log_error "Failed to SCP host pcie.rpt"
    scp -i "$identity_file" \
        "${HOST_SSH_UNAME}@${host_ip}:${host_reports_dir_remote}/membw.rpt" \
        "${current_guest_reports_dir}/host-membw.rpt" || log_error "Failed to SCP host membw.rpt"
    
    # SCP profiling data to host (as guest has limited space)
    # sudo sshpass -p "$HOST_SSH_PASSWORD" scp "$perf_guest_data_file" "${HOST_SSH_UNAME}@${host_ip}:${host_reports_dir_remote}/perf_guest_cpu.data"
    # sudo sshpass -p "$HOST_SSH_PASSWORD" scp "$iova_ftrace_guest_output_file" "${HOST_SSH_UNAME}@${host_ip}:${host_reports_dir_remote}/iova_ftrace_guest.data"

    log_info "Waiting for remote operations and data transfers to settle (original sleep: $(($core_duration_s * 2))s)..."
    sleep $((core_duration_s * 2))

    # --- Post-run cleanup ---
    cleanup
    log_info "############################################################"
    log_info "### Finished Experiment Run: $j / $(($num_runs - 1))"
    log_info "############################################################"
    echo # Blank line
done


if [ "$mlc_cores" != "none" ]; then
    log_info "MLC cores were used. The original script had a second phase for MLC throughput which is currently skipped."
else
    log_info "No MLC instance used, or MLC throughput collection phase skipped."
fi

log_info "Collecting and processing statistics from all runs..."
# The '0' or '1' at the end of collect-tput-stats.py might indicate whether MLC was run. Adjust as needed.
if [ "$mlc_cores" = "none" ]; then
    sudo python3 collect-tput-stats.py "$exp_name" "$num_runs" 0
else
    sudo python3 collect-tput-stats.py "$exp_name" "$num_runs" 0 # TODO: Change back to 1
fi

log_info "Experiment $exp_name finished."
