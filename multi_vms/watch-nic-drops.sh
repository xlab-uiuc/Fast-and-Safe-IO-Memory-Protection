#!/bin/bash
# Monitor per-VF and PF-level NIC drop counters on the host during SR-IOV experiments.
#
# Usage:
#   ./watch-nic-drops.sh [interval_sec]              # default 1s
#   PF_BDF=0000:98:00.0 ./watch-nic-drops.sh 2       # override PF
#
# Shows per-interval deltas. Ctrl-C to stop.

set -uo pipefail

PF_BDF="${PF_BDF:-0000:98:00.0}"
INTERVAL="${1:-1}"

PF_IFACE=$(ls "/sys/bus/pci/devices/$PF_BDF/net/" 2>/dev/null | head -1)
[[ -n "$PF_IFACE" ]] || { echo "ERROR: no netdev for PF $PF_BDF" >&2; exit 1; }

NUM_VFS=$(cat "/sys/bus/pci/devices/$PF_BDF/sriov_numvfs" 2>/dev/null || echo 0)

echo "PF: $PF_IFACE ($PF_BDF)   VFs: $NUM_VFS   interval: ${INTERVAL}s"
echo "Watching rx_discards_phy, rx_prioN_discards, tx_queue_dropped, and per-VF rx/tx drops."
echo ""

# Read PF-level counters of interest via ethtool -S into an array
# Prints lines: "<name> <value>"
pf_counters() {
	sudo ethtool -S "$PF_IFACE" 2>/dev/null | awk '
		/rx_discards_phy:|tx_discards_phy:|rx_prio[0-9]+_discards:|rx_prio[0-9]+_buf_discard:|rx_prio[0-9]+_cong_discard:|rx_out_of_buffer:|tx_queue_dropped:|rx_xdp_drop:|rx_oversize_pkts_sw_drop:|rx_steer_missed_packets:|tx_errors_phy:|rx_crc_errors_phy:|rx_pause_ctrl_phy:|tx_pause_ctrl_phy:|rx_global_pause:|tx_global_pause:|rx_global_pause_duration:|tx_global_pause_duration:|tx_pause_storm_warning_events:|tx_pause_storm_error_events:/ {
			gsub(":", "", $1); print $1, $2
		}'
}

# Read per-VF rx/tx drops via "ip -s -s link show".
# Prints lines: "vf<N> rx_pkts rx_drop tx_pkts tx_drop"
vf_counters() {
	[[ "$NUM_VFS" -gt 0 ]] || return 0
	sudo ip -s -s link show dev "$PF_IFACE" 2>/dev/null | awk '
		/^[ \t]+vf [0-9]+/ { vf=$2; stage=""; next }
		vf!="" && /^[ \t]+RX:/ { stage="rxhdr"; next }
		vf!="" && stage=="rxhdr" {
			# "rx bytes packets mcast bcast"
			rx_pkts=$2; stage="rxdone"; next
		}
		vf!="" && /^[ \t]+TX:/ { stage="txhdr"; next }
		vf!="" && stage=="txhdr" {
			# "tx bytes packets"
			tx_pkts=$2;
			# dropped columns arent always in VF output; use 0 and rely on ethtool per-VF if present
			printf "vf%s %s 0 %s 0\n", vf, rx_pkts, tx_pkts;
			vf=""; stage=""
		}'
}

# Collect into assoc arrays keyed by counter name
declare -A PREV
snapshot() {
	local name val
	while read -r name val; do
		[[ -z "${name:-}" ]] && continue
		CUR[$name]=$val
	done < <(pf_counters)
	while read -r vf rxp rxd txp txd; do
		[[ -z "${vf:-}" ]] && continue
		CUR["${vf}_rx_pkts"]=$rxp
		CUR["${vf}_rx_drop"]=$rxd
		CUR["${vf}_tx_pkts"]=$txp
		CUR["${vf}_tx_drop"]=$txd
	done < <(vf_counters)
}

# Initial snapshot
declare -A CUR
snapshot
for k in "${!CUR[@]}"; do PREV[$k]=${CUR[$k]}; done

# Header
printf "\n%-10s" "time"
printf " %14s" "rx_disc_phy/s" "rx_oob/s" "rx_buf_disc/s" "rx_cong_disc/s" "rx_pause/s" "tx_pause/s" "rx_steer_miss/s" "tx_q_drop/s"
if [[ "$NUM_VFS" -gt 0 ]]; then
	for ((i=0; i<NUM_VFS; i++)); do printf " %11s" "vf${i}_rx/s" "vf${i}_tx/s"; done
fi
echo
echo "-----------------------------------------------------------------------------------------------------------------------------"

delta() {
	local key=$1
	local cur=${CUR[$key]:-0}
	local prev=${PREV[$key]:-0}
	echo $(( (cur - prev) / INTERVAL ))
}

while true; do
	sleep "$INTERVAL"
	declare -A CUR=()
	snapshot

	ts=$(date +%H:%M:%S)
	printf "%-10s" "$ts"
	printf " %14d" \
		"$(delta rx_discards_phy)" \
		"$(delta rx_out_of_buffer)" \
		"$(delta rx_prio0_buf_discard)" \
		"$(delta rx_prio0_cong_discard)" \
		"$(delta rx_pause_ctrl_phy)" \
		"$(delta tx_pause_ctrl_phy)" \
		"$(delta rx_steer_missed_packets)" \
		"$(delta tx_queue_dropped)"

	if [[ "$NUM_VFS" -gt 0 ]]; then
		for ((i=0; i<NUM_VFS; i++)); do
			printf " %11d" \
				"$(delta vf${i}_rx_pkts)" \
				"$(delta vf${i}_tx_pkts)"
		done
	fi
	echo

	# Rotate
	for k in "${!CUR[@]}"; do PREV[$k]=${CUR[$k]}; done
done
