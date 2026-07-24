#!/bin/bash
set -e
SHARE_PATH="$1"; SMB_USER="$2"
SNIPPET="/tmp/jy_smb_snippet.conf"
BEGIN_MARK="# BEGIN jinyu-quanxing deploy-tool"
END_MARK="# END jinyu-quanxing deploy-tool"

echo "===== [remote] NAS samba 設定: $(hostname) ====="
sudo apt-get update
sudo apt-get install -y samba

sudo mkdir -p "$SHARE_PATH"
sudo chown "$SMB_USER":"$SMB_USER" "$SHARE_PATH"

# 備份 + 以 managed block 寫入 share 定義（重跑會先移除舊 block）
sudo cp /etc/samba/smb.conf "/etc/samba/smb.conf.bak.$(date +%Y%m%d%H%M%S)"
sudo awk -v b="$BEGIN_MARK" -v e="$END_MARK" '
    $0 == b {skip=1; next}
    $0 == e {skip=0; next}
    !skip {print}
' /etc/samba/smb.conf | sudo tee /etc/samba/smb.conf.new >/dev/null
{
    echo "$BEGIN_MARK"
    cat "$SNIPPET"
    echo "$END_MARK"
} | sudo tee -a /etc/samba/smb.conf.new >/dev/null
sudo mv /etc/samba/smb.conf.new /etc/samba/smb.conf
rm -f "$SNIPPET"

testparm -s >/dev/null || { echo "✗ smb.conf 語法檢查失敗"; exit 1; }
# share 為 guest + force user 模式，不需 smbpasswd

sudo systemctl enable --now smbd
sudo systemctl restart smbd

# samba 開機自動啟動保險服務（照 Linux Command/samba.txt 的做法）
sudo tee /etc/systemd/system/samba-autostart.service >/dev/null << 'UNIT_EOF'
[Unit]
Description=Start Samba service at boot time
After=network-online.target

[Service]
Type=oneshot
ExecStart=/bin/systemctl start smbd.service
ExecStartPost=/bin/systemctl status smbd.service

[Install]
WantedBy=multi-user.target
UNIT_EOF
sudo systemctl daemon-reload
sudo systemctl enable samba-autostart.service
systemctl is-active smbd
echo "===== [remote] NAS 設定完成 ✓ ====="
