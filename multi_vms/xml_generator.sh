#!/bin/bash
# Generate libvirt XML configs for nested vIOMMU VMs with VFIO passthrough.
#
# Each VM gets:
#   - VF at 0000:98:00.<i+1>
#   - Disk at /data/server_small_<i>.qcow2
#   - vCPUs pinned starting at cpuset 64 + i * vcpus
#   - Unique MAC address
#
# Usage:
#   ./xml-generator.sh --kernel /boot/vmlinuz-6.12.9-iommufd \
#                   --initrd /boot/initrd.img-6.12.9-iommufd \
#                   --vcpus 16 --num-vms 4 --viommu on \
#                   --cmdline "root=/dev/vda2 ro console=ttyS0,115200 intel_iommu=on,sm_on iommu.strict=1"

set -euo pipefail

# --- Defaults ---
NUM_VMS=2
VCPUS=16
VIOMMU="nested"
KERNEL="/boot/vmlinuz-6.12.9-iommufd"
INITRD="/boot/initrd.img-6.12.9-iommufd"
CMDLINE="root=/dev/vda2 ro console=ttyS0,115200 earlyprintk=serial,ttyS0,115200 intel_iommu=on,sm_on iommu.strict=1"
TAG="vanilla"
OUTPUT_DIR="./generated"

QEMU_BIN="/home/lbalara/viommu/qemu-nested/build/qemu-system-x86_64"
BIOS="/home/lbalara/viommu/qemu-nested/pc-bios/bios-256k.bin"

# --- Mostly static configs ---
CPU_START=64
NUMA_NODE=2
MEMORY_KIB=14680064  # 32 GiB

MAX_VMS=16

usage() {
	cat <<-USAGE
	Usage: $0 [OPTIONS]

	Required:
	  --kernel PATH       Full path to kernel image
	  --initrd PATH       Full path to initrd image
	  --cmdline STRING    Full kernel command line

	Optional:
	  --vcpus N           vCPUs per VM (default: 16)
	  --num-vms N         Number of VMs to generate, max $MAX_VMS (default: 2)
	  --viommu nested|off     Enable vIOMMU + iommufd passthrough (default: nested)
	  --qemu PATH         QEMU binary path (default: $QEMU_BIN)
	  --bios PATH         BIOS image path (default: $BIOS)
	  --output-dir DIR    Output directory for XML files (default: .)
	  --cpu-start N       First physical CPU for pinning (default: $CPU_START)
	  --numa-node N       NUMA node for memory binding (default: $NUMA_NODE)
	  -h, --help          Show this help
	USAGE
}

# --- Parse arguments ---
while [[ $# -gt 0 ]]; do
	case "$1" in
	--kernel)      KERNEL="$2";     shift 2 ;;
	--initrd)      INITRD="$2";     shift 2 ;;
	--cmdline)     CMDLINE="$2";    shift 2 ;;
	--vcpus)       VCPUS="$2";      shift 2 ;;
	--num-vms)     NUM_VMS="$2";    shift 2 ;;
	--viommu)      VIOMMU="$2";     shift 2 ;;
	--qemu)        QEMU_BIN="$2";   shift 2 ;;
	--bios)        BIOS="$2";       shift 2 ;;
	--output-dir)  OUTPUT_DIR="$2"; shift 2 ;;
	--cpu-start)   CPU_START="$2";  shift 2 ;;
	--numa-node)   NUMA_NODE="$2";  shift 2 ;;
  --tag)         TAG="$2";        shift 2 ;;
	-h|--help)     usage; exit 0    ;;
	*)             echo "Error: unknown option '$1'" >&2; usage >&2; exit 1 ;;
	esac
done

# --- Validate ---
err=0
for var in KERNEL INITRD CMDLINE; do
	if [[ -z "${!var}" ]]; then
		echo "Error: --$(echo "$var" | tr '[:upper:]' '[:lower:]') is required" >&2
		err=1
	fi
done
[[ $err -ne 0 ]] && exit 1

if [[ "$VIOMMU" != "nested" && "$VIOMMU" != "off" ]]; then
	echo "Error: --viommu must be 'nested' or 'off'" >&2
	exit 1
fi

if [[ "$NUM_VMS" -lt 1 || "$NUM_VMS" -gt "$MAX_VMS" ]]; then
	echo "Error: --num-vms must be between 1 and $MAX_VMS" >&2
	exit 1
fi

mkdir -p "$OUTPUT_DIR"

# --- Helper: generate vcpupin entries ---
gen_vcpupin() {
	local cpu_base=$1
	local nvcpus=$2
	local i

	for ((i = 0; i < nvcpus; i++)); do
		printf "    <vcpupin vcpu='%d' cpuset='%d'/>\n" "$i" "$((cpu_base + i))"
	done
}

# --- Helper: generate pcie-root-port controllers ---
gen_pcie_root_ports() {
	local idx
	local port
	local slot
	local func

	for ((idx = 1; idx <= 14; idx++)); do
		port=$((0x0f + idx))
		if [[ $idx -le 8 ]]; then
			slot=2
			func=$((idx - 1))
		else
			slot=3
			func=$((idx - 9))
		fi

		local mf=""
		if [[ $func -eq 0 ]]; then
			mf=" multifunction='on'"
		fi

		cat <<-PORT
		    <controller type='pci' index='$idx' model='pcie-root-port'>
		      <model name='pcie-root-port'/>
		      <target chassis='$idx' port='$(printf '0x%x' "$port")'/>
		      <address type='pci' domain='0x0000' bus='0x00' slot='$(printf '0x%02x' "$slot")' function='$(printf '0x%x' "$func")'${mf}/>
		    </controller>
		PORT
	done
}

# --- Generate VM XMLs ---
for ((vm = 0; vm < NUM_VMS; vm++)); do
	vm_name="${TAG}-generated-iommufd-${VIOMMU}-vcpu${VCPUS}-vm${vm}"
  vf_num=$((vm + 1))
  vf_dev=$(printf '%02x' $((vf_num / 8)))
  vf_func=$((vf_num % 8))
  vf_pci="0000:98:${vf_dev}.${vf_func}"
  if [[ $vm -eq 0 ]]; then
    disk="/data/server_small.qcow2"
  else
    disk="/data/server_small${vf_num}.qcow2"
  fi
	cpu_base=$((CPU_START + vm * VCPUS))
	mac_last=$(printf '%02x' $(( (0xe2 + vm) & 0xff )))
	mac="52:54:00:14:26:${mac_last}"
	outfile="${OUTPUT_DIR}/${TAG}-iommufd-${VIOMMU}-vcpu${VCPUS}-vm${vm}.xml"

	cat > "$outfile" <<EOF
<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
  <name>${vm_name}</name>
  <metadata>
    <libosinfo:libosinfo xmlns:libosinfo="http://libosinfo.org/xmlns/libvirt/domain/1.0">
      <libosinfo:os id="http://ubuntu.com/ubuntu/20.04"/>
    </libosinfo:libosinfo>
  </metadata>
  <memory unit='KiB'>${MEMORY_KIB}</memory>
  <currentMemory unit='KiB'>${MEMORY_KIB}</currentMemory>
  <vcpu placement='static'>${VCPUS}</vcpu>
  <numatune>
    <memory mode='strict' nodeset='${NUMA_NODE}'/>
  </numatune>
  <cputune>
$(gen_vcpupin "$cpu_base" "$VCPUS")
  </cputune>
  <resource>
    <partition>/machine</partition>
  </resource>
  <os>
    <type arch='x86_64' machine='q35'>hvm</type>
    <kernel>${KERNEL}</kernel>
    <initrd>${INITRD}</initrd>
    <cmdline>${CMDLINE}</cmdline>
    <loader>${BIOS}</loader>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <ioapic driver='qemu'/>
  </features>
  <cpu mode='host-passthrough' check='none'/>
  <clock offset='utc'>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='pit' tickpolicy='delay'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <pm>
    <suspend-to-mem enabled='no'/>
    <suspend-to-disk enabled='no'/>
  </pm>
  <devices>
    <emulator>${QEMU_BIN}</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' discard='unmap'/>
      <source file='${disk}' index='2'/>
      <backingStore/>
      <target dev='vda' bus='virtio'/>
      <alias name='virtio-disk0'/>
      <address type='pci' domain='0x0000' bus='0x04' slot='0x00' function='0x0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu'/>
      <target dev='sda' bus='sata'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
    <controller type='usb' index='0' model='qemu-xhci' ports='15'>
      <address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
    </controller>
    <controller type='pci' index='0' model='pcie-root'/>
$(gen_pcie_root_ports)
    <controller type='sata' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x1f' function='0x2'/>
    </controller>
    <controller type='virtio-serial' index='0'>
      <address type='pci' domain='0x0000' bus='0x03' slot='0x00' function='0x0'/>
    </controller>
    <interface type='network'>
      <mac address='${mac}'/>
      <source network='default'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x01' slot='0x00' function='0x0'/>
    </interface>
    <serial type='pty'>
      <target type='isa-serial' port='0'>
        <model name='isa-serial'/>
      </target>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
      <alias name='serial0'/>
    </console>
    <channel type='unix'>
      <target type='virtio' name='org.qemu.guest_agent.0' state='disconnected'/>
      <alias name='channel0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    <input type='tablet' bus='usb'>
      <alias name='input0'/>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'>
      <alias name='input1'/>
    </input>
    <input type='keyboard' bus='ps2'>
      <alias name='input2'/>
    </input>
    <video>
      <model type='virtio' heads='1' primary='yes'/>
      <alias name='video0'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <alias name='balloon0'/>
      <address type='pci' domain='0x0000' bus='0x05' slot='0x00' function='0x0'/>
    </memballoon>
    <rng model='virtio'>
      <backend model='random'>/dev/urandom</backend>
      <alias name='rng0'/>
      <address type='pci' domain='0x0000' bus='0x06' slot='0x00' function='0x0'/>
    </rng>
  </devices>
  <seclabel type='dynamic' model='dac' relabel='yes'>
    <label>+64055:+108</label>
    <imagelabel>+64055:+108</imagelabel>
  </seclabel>
  <qemu:commandline>
    <qemu:arg value='-M'/>
    <qemu:arg value='kernel_irqchip=split'/>
    <qemu:arg value='-object'/>
    <qemu:arg value='iommufd,id=iommufd0'/>
    <qemu:arg value='-device'/>
    <qemu:arg value='intel-iommu,intremap=on,caching-mode=on,x-scalable-mode=on,x-flts=on'/>
    <qemu:arg value='-device'/>
    <qemu:arg value='vfio-pci,host=${vf_pci},id=hostdev0,iommufd=iommufd0'/>
  </qemu:commandline>
</domain>
EOF

	echo "Generated: ${outfile}  (${vm_name}, VF=${vf_pci}, CPUs=${cpu_base}-$((cpu_base + VCPUS - 1)), disk=${disk})"
done

echo "Done: ${NUM_VMS} VM config(s) in ${OUTPUT_DIR}/"