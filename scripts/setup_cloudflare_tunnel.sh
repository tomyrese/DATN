#!/bin/bash
# ==============================================================================
# Cloudflare Tunnel Auto Setup for Pi Robot Remote Internet Control
# Allows anyone over the Internet (e.g. Vercel web app) to connect via HTTPS/WSS
# without port forwarding or static IP!
# ==============================================================================

set -e

ROBOT_PORT=8765

echo "========================================================"
echo "    PI ROBOT - CLOUDFLARE TUNNEL REMOTE ACCESS SETUP    "
echo "========================================================"

# Check architecture
ARCH=$(uname -m)
echo "[1/4] Detecting hardware architecture: $ARCH"

if ! command -v cloudflared &> /dev/null; then
    echo "[2/4] Downloading cloudflared binary..."
    if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
        wget -q -O /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
    elif [[ "$ARCH" == "armv7l" || "$ARCH" == "armhf" ]]; then
        wget -q -O /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-armhf.deb
    else
        wget -q -O /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    fi
    sudo dpkg -i /tmp/cloudflared.deb
    rm -f /tmp/cloudflared.deb
    echo "[+] cloudflared installed successfully!"
else
    echo "[+] cloudflared is already installed."
fi

echo ""
echo "[3/4] Choose Cloudflare Tunnel Mode:"
echo "  1) Quick Free Tunnel (Instant public https://xyz.trycloudflare.com, no domain needed)"
echo "  2) Custom Cloudflare Domain Tunnel (Persistent custom subdomain)"
read -p "Select option (1 or 2, default 1): " TUNNEL_CHOICE
TUNNEL_CHOICE=${TUNNEL_CHOICE:-1}

if [ "$TUNNEL_CHOICE" == "1" ]; then
    echo ""
    echo "[4/4] Starting Quick Tunnel to port $ROBOT_PORT..."
    echo "========================================================"
    echo "Your robot public URL will be printed below."
    echo "Copy the https://xxx.trycloudflare.com URL and paste it"
    echo "into the Robot Settings or Vercel Web App!"
    echo "========================================================"
    cloudflared tunnel --url http://127.0.0.1:$ROBOT_PORT
else
    echo ""
    echo "For Custom Domain:"
    echo "1. Run: cloudflared tunnel login"
    echo "2. Run: cloudflared tunnel create pi-robot"
    echo "3. Run: cloudflared tunnel route dns pi-robot robot.yourdomain.com"
    echo "4. Run: cloudflared tunnel run --url http://127.0.0.1:$ROBOT_PORT pi-robot"
fi
