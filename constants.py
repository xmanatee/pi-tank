# server/constants.py

import logging
from libcamera import Transform
from picamera2.encoders import Quality

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
FRAME_SIZE = (640, 480)
FRAME_TRANSFORM = Transform(hflip=1, vflip=1)
JPEG_QUALITY = 90
VIDEO_QUALITY = Quality.VERY_HIGH

# Flask-SocketIO Configuration
ASYNC_MODE = 'eventlet'
CORS_ALLOWED_ORIGINS = '*'
