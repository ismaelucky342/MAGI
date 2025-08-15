# MAGI Security Recommendations

This document describes a pragmatic, layered approach to secure MAGI nodes and the network between them.

## Goals
- Remove direct exposure of node web APIs and management ports to the public internet.
- Provide encrypted, authenticated transport between nodes.
- Limit attack surface via firewall rules and authentication.
- Add continuous protection and monitoring to detect and block attacks.

---

## 1) Close direct exposure (VPN first)

A. VPN mandatory (recommended)
- Use WireGuard or Tailscale to create a private network between MAGI nodes.
- WireGuard: faster, self-hosted, simple configs.
- Tailscale: easiest to maintain, auto NAT-traversal, ACLs available.

WireGuard quick setup (Ubuntu/Debian):

sudo apt update; sudo apt install -y wireguard
# generate keys on each node
wg genkey | tee privatekey | wg pubkey > publickey
# create /etc/wireguard/wg0.conf with peers and start
sudo systemctl enable --now wg-quick@wg0

Tailscale quick install (single line):

curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --authkey tskey-...  # use your auth key

B. ZeroTier is an alternative if you prefer easier LAN-style bridging.

## 2) Firewall - deny by default

Use `ufw` (simple) or `nftables` (advanced). Example `ufw` rules:

sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
# allow SSH only from VPN subnet (example 10.0.0.0/24)
sudo ufw allow from 10.0.0.0/24 to any port 22 proto tcp
# allow MAGI only from VPN
sudo ufw allow from 10.0.0.0/24 to any port 8080 proto tcp
sudo ufw enable

If you run Tailscale, restrict to Tailscale IPs instead of local VPN subnet.

## 3) Authentication hardening

- Use SSH key-based auth; disable password auth in `/etc/ssh/sshd_config`:

PasswordAuthentication no
ChallengeResponseAuthentication no
UsePAM no

- For web panels (Nextcloud, Jellyfin, etc) enable 2FA and IP restrictions when possible.

- For MAGI API: enable API key enforcement in `magi-node-v2.py` by setting `CONFIG['require_api_key']=True` and change `CONFIG['api_key']` to a strong secret.

## 4) Continuous audit and blocking

- Install `fail2ban` or `crowdsec` to ban IPs with suspicious behavior.

sudo apt install -y fail2ban
# enable basic SSH jail and HTTP protections

- Centralized log monitoring (Melchior): run Wazuh/ELK or even `logwatch` and alert on anomalies.

## 5) Internal DNS / service names

- Use Avahi/Bonjour or an internal DNS (dnsmasq, Pi-hole) so nodes communicate by `gaspar.local`, `melchior.local`, `baltasar.local`.
- Avahi example (Avahi publishes hostname on local link):

sudo apt install -y avahi-daemon
sudo systemctl enable --now avahi-daemon

## 6) Orchestration & distributed intelligence

- If you want dynamic placement and task scheduling, use a lightweight queue (Redis, NATS, RabbitMQ) where nodes publish their state and consume tasks.
- For container orchestration, consider Docker Swarm (simple), Nomad (lightweight), or Kubernetes (more complex).
- Use HAProxy/Traefik as ingress and replicate important data across nodes (Nextcloud replication, backups).

## 7) Quick checklist to apply now

- [ ] Install WireGuard or Tailscale on all nodes and ensure mgmt ports are reachable only via VPN.
- [ ] Configure UFW to deny incoming by default and allow only VPN traffic.
- [ ] Disable SSH password auth.
- [ ] Enable MAGI API key: edit `magi-node-v2.py` CONFIG and restart service.
- [ ] Install fail2ban or crowdsec.
- [ ] Configure Melchior as monitoring/alerting node.

---

If you want, I can:
- Add a small `setup_security.sh` script to help install WireGuard/Tailscale and basic ufw rules.
- Add code to `magi-node-v2.py` to populate its `CONFIG['api_key']` from an environment variable and refuse to start if `require_api_key` is true but key is default.

Dime qué siguiente paso quieres que haga y lo implemento.
