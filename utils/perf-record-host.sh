SCRIPT_NAME="perf-record-host"

# default values
DURATION=20
PERF=/home/lbalara/viommu/linux-6.12.9/tools/perf/perf
GUEST_SRC=/home/lbalara/viommu/modified-linux-6.12.9 #TODO
EXP_NAME=unknown
UUID=unset


# string literals
VM_COPY_DIR=temp
QEMU_PROCESS_NAME=qemu-system-x86_64
CPU_DATA=perf_host_cpu.data
KVM_DATA=perf_host_kvm.data
KVM_STAT_DATA=perf.data.guest
SCHED_DATA=perf_host_sched.data
LOGS=perf_host.log

help()
{
    echo "Usage: $SCRIPT_NAME 
              [ -d | --dur (duration in second) ] 
              [ -e | --exp (experiment name) ] 
              [ -h | --help  ]"
    exit 2
}

SHORT=d:,e:,h
LONG=dur:,exp:,help
PARSED_OPTS=$(getopt -a -n $SCRIPT_NAME --options $SHORT --longoptions $LONG -- "$@")

VALID_ARGUMENTS=$#
if [ "$VALID_ARGUMENTS" -eq 0 ]; then
  help
fi
eval set -- "$PARSED_OPTS"

while :;do
  case "$1" in
    -d | --dur) DURATION="$2"; shift 2 ;;
    -e | --exp) EXP_NAME="$2"; shift 2 ;;
    -h | --help) help ;;
    -u | --uuid) UUID="$2"; shift 2 ;;
    --) shift; break ;;
    *) echo "Unexpected option: $1"; help ;;
  esac
done

log_info() {
    echo "[INFO] - $1"
}

QPID=$(pidof $QEMU_PROCESS_NAME)

mkdir -p reports/${EXP_NAME}

# $PERF record -F 99 -a -g --call-graph dwarf -o reports/${EXP_NAME}/${CPU_DATA} -- sleep $DURATION &
# $PERF kvm --guest --host --guestkallsyms=${VM_COPY_DIR}/kallsyms --guestmodules=${VM_COPY_DIR}/modules --guestvmlinux=$GUEST_SRC/vmlinux record -p $QPID -F 99 -o reports/${EXP_NAME}/${KVM_DATA} -- sleep $DURATION > reports/${EXP_NAME}/${LOGS} 2>&1 &
(exec -a ${UUID} $PERF kvm stat record -p $QPID -o reports/${EXP_NAME}/${KVM_STAT_DATA} -- sleep $DURATION > reports/${EXP_NAME}/${LOGS} 2>&1) &
# $PERF sched record -p $QPID -o reports/${EXP_NAME}/${SCHED_DATA} -- sleep $DURATION > reports/${EXP_NAME}/${LOGS} 2>&1 &
