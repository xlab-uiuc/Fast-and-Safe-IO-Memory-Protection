#!/usr/bin/env bash
set -euo pipefail

# =========================================================
# Sync kernel modules from host into guest
# Siyuan's auto-reset script (runs on boot with systemd)
# =========================================================

KERNEL_NAME=$(uname -r)
HOST_USER="siyuanc3"
HOST_IP="192.168.122.1"
SSH_PORT=22
IDENTITY_FILE="/home/schai/.ssh/id_rsa"

SSH_OPTS="-i ${IDENTITY_FILE} -o StrictHostKeyChecking=accept-new"

TMP_TARBALL="/tmp/modules-${KERNEL_NAME}.tar.gz"
REMOTE_TARBALL="/tmp/modules-${KERNEL_NAME}.tar.gz"
DST_DIR="/lib/modules/${KERNEL_NAME}"

echo "[1/5] Requesting host to package modules..."
ssh -p "$SSH_PORT" $SSH_OPTS "${HOST_USER}@${HOST_IP}" \
  "sudo rm -f ${REMOTE_TARBALL} && sudo tar czf ${REMOTE_TARBALL} -C /lib/modules/${KERNEL_NAME} ."

echo "[2/5] Copying archive from host:${HOST_IP} ..."
scp -P "$SSH_PORT" $SSH_OPTS "${HOST_USER}@${HOST_IP}:${REMOTE_TARBALL}" "$TMP_TARBALL"

echo "[3/5] Installing into ${DST_DIR} ..."
sudo mkdir -p "$DST_DIR"
sudo tar xzf "$TMP_TARBALL" -C "$DST_DIR" --numeric-owner

echo "[4/5] Backing up DKMS updates (if any) ..."
if [[ -d "${DST_DIR}/updates/dkms" ]]; then
  sudo mkdir -p "/tmp/dkms_backup/${KERNEL_NAME}"
  sudo sh -c "mv ${DST_DIR}/updates/dkms/* /tmp/dkms_backup/${KERNEL_NAME}/ || true"
fi

echo "[5/5] Running depmod ..."
sudo depmod -a "$KERNEL_NAME"

# Optional cleanup on host and guest
echo "[cleanup] Removing temporary archives..."
ssh -p "$SSH_PORT" $SSH_OPTS "${HOST_USER}@${HOST_IP}" "sudo rm -f ${REMOTE_TARBALL}" || true
sudo rm -f "$TMP_TARBALL" || true

echo "✅ Done. Try: sudo modprobe msr"
