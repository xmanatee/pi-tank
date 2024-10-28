# Use a Raspberry Pi 4 64-bit base image with Bullseye
FROM balenalib/raspberrypi4-64-debian-python:3.9-bullseye

# Set environment variables to avoid interactive prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive

# Copy the application code and init.sh into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Make init.sh executable
RUN chmod +x init.sh

# Run init.sh to install dependencies
RUN /bin/bash ./init.sh

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 5013

# Start the pigpio daemon and your server
CMD ["bash", "-c", "pigpiod && python3 main.py"]
