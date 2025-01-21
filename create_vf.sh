#!/bin/bash

sudo bash -c "echo 4 > /sys/class/net/enp202s0f0np0/device/sriov_numvfs"

lspci -D | grep Mellanox

sudo virsh nodedev-detach pci_0000_ca_00_2

lspci -D | grep Mellanox