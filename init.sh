#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ "$EUID" -ne 0 ]; then
  echo "Run this installer as root." >&2
  exit 1
fi
apt-get update
apt-get install -y git rsync python3-pip python3-dev python3-rpi.gpio \
  python3-picamera2 python3-opencv python3-flask python3-flask-socketio \
  python3-eventlet pigpio
clone_dir="$(mktemp -d)"
trap 'rm -rf "$clone_dir"' EXIT
git clone --recurse-submodules https://github.com/rpi-ws281x/rpi-ws281x-python.git "$clone_dir/library"
(cd "$clone_dir/library/library" && python3 setup.py install)
bash ./install-service.sh
