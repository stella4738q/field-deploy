#!/bin/bash
set -e
NAS_IP="$1"; SHARE="$2"; MOUNT_POINT="$3"; SMB_USER="$4"; SMB_PASSWORD="$5"
BEGIN_MARK="# BEGIN jinyu-quanxing deploy-tool - Samba Mount"
END_MARK="# END jinyu-quanxing deploy-tool - Samba Mount"

echo "===== [remote] NAS 掛載設定: $(hostname) ====="
command -v mount.cifs >/dev/null 2>&1 || sudo apt-get install -y cifs-utils
sudo mkdir -p "$MOUNT_POINT"

# 帳密存 credentials 檔（root 600），fstab 不放明文密碼
CRED_FILE="/etc/samba/jy-nas-credentials"
sudo mkdir -p /etc/samba
printf 'username=%s\npassword=%s\n' "$SMB_USER" "$SMB_PASSWORD" | sudo tee "$CRED_FILE" >/dev/null
sudo chmod 600 "$CRED_FILE"

FSTAB_LINE="//${NAS_IP}/${SHARE} ${MOUNT_POINT} cifs credentials=${CRED_FILE},uid=1000,iocharset=utf8,_netdev 0 0"

sudo cp /etc/fstab "/etc/fstab.bak.$(date +%Y%m%d%H%M%S)"
sudo awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
    $0 == b {skip=1; next}
    $0 == e {skip=0; next}
    !skip {print}
' /etc/fstab | sudo tee /etc/fstab.new >/dev/null
{
    echo "$BEGIN_MARK"
    echo "$FSTAB_LINE"
    echo "$END_MARK"
} | sudo tee -a /etc/fstab.new >/dev/null
sudo mv /etc/fstab.new /etc/fstab

sudo systemctl daemon-reload 2>/dev/null || true
sudo mount -a
if mountpoint -q "$MOUNT_POINT"; then
    echo "✓ 掛載成功: $(df -h "$MOUNT_POINT" | tail -1)"
else
    echo "✗ 掛載失敗，請檢查 NAS 端設定與網路"
    exit 1
fi
echo "===== [remote] $(hostname) 掛載完成 ✓ ====="
