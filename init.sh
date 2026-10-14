#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ "$EUID" -ne 0 ]; then
  echo "Run this installer as root." >&2
  exit 1
fi
apt-get update
apt-get install -y rsync python3-venv python3-dev python3-rpi.gpio \
  python3-picamera2 python3-opencv python3-pigpio pigpio build-essential
bash ./install-service.sh
