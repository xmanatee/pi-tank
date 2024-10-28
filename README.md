# Raspberry Pi Tank Server

A complete rewrite of the [Freenove Tank Robot Kit code](https://github.com/Freenove/Freenove_Tank_Robot_Kit_for_Raspberry_Pi) to control the Freenove Tank Robot (because I couldn't tolerate running [that](https://github.com/Freenove/Freenove_Tank_Robot_Kit_for_Raspberry_Pi/blob/main/Code/setup.py)). This implementation provides a simple HTTP server hosted on the Raspberry Pi, accessible via your browser. The UI displays the camera feed and controls for the robot - no client application required.

**IMPORTANT:** Only tested on Raspberry Pi 4 B (e.g., logic for disabling audio on the board is commented out in `init.sh`).

## Features

- **Web-Based Control Interface:** Control your robot directly from a web browser.
- **Live Video Streaming:** View the camera feed in real-time.
- **No Client Application Needed:** Access the controls via HTTP.

## Prerequisites

- Raspberry Pi 4 B with Raspberry Pi OS Bullseye installed.
- Freenove Tank Robot Kit assembled and connected.
- Internet connection for installing dependencies.

## Installation

### 1. Clone the Repository

1. Move the code to your board:
```bash
git clone https://github.com/xmanatee/pi-tank.git
```

### 2. Set Up the Board:
```bash
cd pi-tank
sudo bash init.sh
```

### 3. Run the Server:
```bash
sudo python3 main.py
```

## Usage

- Access the server via `http://raspberry-pi.local:5013` or `http://<raspberry-pi-ip>:5013` in your web browser.

- Use the on-screen controls or keyboard keys (`W`, `A`, `S`, `D`, `I`, `J`, `K`, `L`) to control the robot.


## Docker Setup (Experimental)

**NOTE:** Docker setup is experimental and not fully tested.

**Build the Docker Image:**

```bash
docker build -t pi-tank .
```

**Run the Docker Container:**

```bash
docker run \
    --privileged \
    --device /dev/vchiq \
    --device /dev/gpiomem \
    --device /dev/video0 \
    -p 5013:5013 \
    pi-tank
```

Note: Docker may have limitations with hardware access. Ensure the devices are correctly mapped and permissions are set.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
