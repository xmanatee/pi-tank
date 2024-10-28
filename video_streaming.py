# server/video_streaming.py

import io
import logging
import eventlet
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput
from constants import FRAME_SIZE, FRAME_TRANSFORM, JPEG_QUALITY, VIDEO_QUALITY

class StreamingOutput(io.BufferedIOBase):
    """Handles streaming output for video frames."""

    def __init__(self):
        super().__init__()
        self.frame_queue = eventlet.queue.Queue(maxsize=1)

    def write(self, buf):
        # Overwrite the old frame if the queue is full
        if self.frame_queue.full():
            try:
                self.frame_queue.get_nowait()
                logging.debug("Discarded old frame")
            except eventlet.queue.Empty:
                pass
        self.frame_queue.put(buf)
        logging.debug("New frame added to queue")

class VideoCamera:
    def __init__(self):
        self.camera = Picamera2()
        self.output = StreamingOutput()
        self.encoder = JpegEncoder(q=JPEG_QUALITY)
        self.camera.configure(
            self.camera.create_video_configuration(
                main={"size": FRAME_SIZE},
                transform=FRAME_TRANSFORM
            )
        )
        self.camera.start_recording(self.encoder, FileOutput(self.output), quality=VIDEO_QUALITY)
        logging.info("Camera started")

    def get_frame(self):
        try:
            frame = self.output.frame_queue.get_nowait()
            logging.debug("Frame retrieved from queue")
            return frame
        except eventlet.queue.Empty:
            # No frame is available
            logging.warning("No frame available in queue")
            return None

    def stop(self):
        logging.info("Stopping camera")
        try:
            self.camera.stop_recording()
            logging.info("Camera recording stopped")
        except Exception as e:
            logging.error(f"Error stopping camera recording: {e}")
        try:
            self.camera.stop()
            logging.info("Camera stopped")
        except Exception as e:
            logging.error(f"Error stopping camera: {e}")
        try:
            self.camera.close()
            logging.info("Camera closed")
        except Exception as e:
            logging.error(f"Error closing camera: {e}")
