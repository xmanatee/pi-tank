# Raspberry Pi Tank Server

Browser control and camera streaming for the Freenove Tank Robot on a Raspberry Pi 4. The hardware needs Raspberry Pi OS and its native camera/GPIO libraries.

## Install

On the Pi, clone this repository and run `sudo bash init.sh`. It installs the native systemd service, keeps pigpiod on localhost, and creates independent login and session secrets in `/etc/pi-tank.env` (root only). It does not reboot or start a privileged Docker container.

After changing the code, run `sudo bash install-service.sh`. It stops the service before replacing code and starts it again afterward.

## Connect

From your private machine:

```sh
ssh -L 5013:127.0.0.1:5013 xmanatee@raspberry-pi.local
```

Open <http://127.0.0.1:5013> and log in with `TANK_TOKEN` from `/etc/pi-tank.env`. Keep that token private. The server binds to loopback by default; `TANK_BIND` is in the same environment file.

Use the browser controls or W/A/S/D and I/J/K/L. Only one connected browser owns the controller at a time. Movement stops when its heartbeat is lost, it disconnects, or its tab loses focus. The systemd service also runs an independent motor stop before startup and after the process exits, including a forced termination. Keep a physical power cutoff accessible when operating the robot.

`systemctl status pi-tank` and `journalctl -u pi-tank` show service health. Controller logic can be checked without hardware using `python3 -m unittest test_control.py`. Camera, GPIO, and motor behavior still require testing on the physical Pi.

## License

Apache License 2.0; see LICENSE.
