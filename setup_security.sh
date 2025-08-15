#!/usr/bin/env bash
# MAGI setup_security.sh
# Usage: sudo bash setup_security.sh --api-key <key> --node <NODE_NAME> [--tailscale]

set -euo pipefail
API_KEY=""
NODE_NAME="magi-node"
USE_TAILSCALE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-key)
      API_KEY="$2"; shift 2;;
    --node)
      NODE_NAME="$2"; shift 2;;
    --tailscale)
      USE_TAILSCALE=1; shift 1;;
    --help)
      echo "Usage: sudo bash setup_security.sh --api-key <key> --node <NODE_NAME> [--tailscale]"; exit 0;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
done

if [[ -z "$API_KEY" ]]; then
  echo "ERROR: --api-key is required"
  exit 1
fi

echo "[MAGI] Setting up basic security for node: ${NODE_NAME}"

# 1) UFW basic rules
if command -v ufw >/dev/null 2>&1; then
  echo "[MAGI] Configuring UFW: deny incoming, allow outgoing"
  ufw default deny incoming
  ufw default allow outgoing
  # Allow SSH only from VPN later -- here we allow local management as example
  ufw allow 22/tcp
  # MAGI port (restrict later to VPN subnet)
  ufw allow 8080/tcp
  ufw --force enable
else
  echo "[MAGI] ufw not installed. Skipping firewall setup."
fi

# 2) Optional: install tailscale
if [[ $USE_TAILSCALE -eq 1 ]]; then
  echo "[MAGI] Installing Tailscale"
  curl -fsSL https://tailscale.com/install.sh | sh
  echo "Run: sudo tailscale up --authkey <your-key>"
fi

# 3) Create systemd unit template for MAGI with API key env
SERVICE_NAME="magi-${NODE_NAME}.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"

echo "[MAGI] Creating systemd unit template at ${SERVICE_PATH}"
cat > "${SERVICE_NAME}.tmp" <<EOF
[Unit]
Description=MAGI Node ${NODE_NAME}
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/magi
Environment=MAGI_API_KEY=${API_KEY}
ExecStart=/usr/bin/python3 /opt/magi/magi-node-v2.py ${NODE_NAME}
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo "Copying unit file to ${SERVICE_PATH} (requires sudo)"
sudo mkdir -p /opt/magi || true
sudo cp -v ./${SERVICE_NAME}.tmp "${SERVICE_PATH}"
sudo systemctl daemon-reload
sudo systemctl enable --now "${SERVICE_NAME}"
rm -f ./${SERVICE_NAME}.tmp

echo "[MAGI] Systemd unit installed and started. Use: sudo journalctl -u ${SERVICE_NAME} -f"

echo "Done. Remember to restrict UFW rules to VPN subnet once VPN is up (e.g. ufw allow from 10.0.0.0/24 to any port 8080 proto tcp)"
