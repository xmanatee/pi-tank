#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
if [ "$EUID" -ne 0 ]; then
  echo "Run this installer as root." >&2
  exit 1
fi
# Stop using the installed helper before replacing code or restarting pigpiod.
if systemctl cat pi-tank.service >/dev/null 2>&1; then
  systemctl stop pi-tank.service
fi
install -d -m 0755 /opt/pi-tank
# Copy tracked application files without credentials, repository metadata or caches.
rsync -a --exclude=.git --exclude=.env --exclude=.venv --exclude=__pycache__ ./ /opt/pi-tank/
python3 -m venv --system-site-packages /opt/pi-tank/.venv
/opt/pi-tank/.venv/bin/python -m pip install --require-hashes -r /opt/pi-tank/requirements.txt
chown -R root:root /opt/pi-tank
chmod -R go-w /opt/pi-tank
if [ ! -e /etc/pi-tank.env ]; then
  umask 077
  python3 - <<'ENV'
import secrets
from pathlib import Path
Path('/etc/pi-tank.env').write_text('TANK_TOKEN='+secrets.token_urlsafe(48)+'\nTANK_SESSION_SECRET='+secrets.token_urlsafe(48)+'\nTANK_BIND=127.0.0.1\n')
ENV
fi
chmod 0600 /etc/pi-tank.env
install -d /etc/systemd/system/pigpiod.service.d
install -m 0644 pigpiod-local.conf /etc/systemd/system/pigpiod.service.d/local.conf
install -m 0644 pi-tank.service /etc/systemd/system/pi-tank.service
systemctl daemon-reload
systemctl enable pigpiod.service
systemctl restart pigpiod.service
systemctl enable --now pi-tank.service
