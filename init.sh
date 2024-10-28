#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Upgrading and installing dependencies (without sudo)
apt-get update -y && apt-get upgrade -y
apt-get install -y \
  git \
  python3-pip \
  python3-dev \
  python3-rpi.gpio \
  python3-picamera2 \
  python3-opencv \
  python3-flask \
  python3-flask-socketio \
  python3-eventlet \
  pigpio

# Installing PWM library
git clone --recurse-submodules \
  https://github.com/rpi-ws281x/rpi-ws281x-python.git \
  /tmp/rpi-ws281x-python
pushd /tmp/rpi-ws281x-python/library
python3 setup.py install
popd
rm -rf /tmp/rpi-ws281x-python

# Enable pigpio daemon (host-only, skip in Docker)
if [ "$(grep -i docker /proc/1/cgroup)" ]; then
  echo "Running inside Docker; skipping pigpiod setup."
else
  systemctl enable pigpiod
  systemctl start pigpiod
fi

# Disable audio (host-only, skip in Docker)
# echo 'blacklist snd_bcm2835' | tee /etc/modprobe.d/snd-blacklist.conf
# sed -i 's/dtparam=audio=on/#dtparam=audio=on/' /boot/firmware/config.txt

# Reboot the system to apply changes (host-only, skip in Docker)
if [ "$(grep -i docker /proc/1/cgroup)" ]; then
  echo "Running inside Docker; skipping reboot."
else
  reboot
fi
