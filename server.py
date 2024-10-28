import logging
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit

from constants import *
from command_processor import CommandProcessor
from video_streaming import VideoCamera

app = Flask(__name__, static_folder='templates')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode=ASYNC_MODE)

# Global variables
background_thread_running = True
command_processor = None
video_camera = None

# Routes
@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

def gen(camera):
    """Video streaming generator function."""
    try:
        while True:
            frame = camera.get_frame()
            if frame:
                logging.debug("Sending a video frame")
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            else:
                logging.warning("No frame received from camera")
            # Control the frame rate (e.g., 0.05 for ~20 FPS)
            socketio.sleep(0.05)
    except Exception as e:
        logging.error(f"Error in video streaming generator: {e}")
        raise e

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# WebSocket events
@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    emit('connection_status', {'status': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')
    # Stop the robot when client disconnects
    command_processor.reset_all()

@socketio.on('key_press')
def handle_key_press(data):
    key = data.get('key')
    logging.info(f"Received key_press event: {key}")
    command_processor.handle_key_press(key)

@socketio.on('key_release')
def handle_key_release(data):
    key = data.get('key')
    logging.info(f"Received key_release event: {key}")
    command_processor.handle_key_release(key)

@socketio.on('action')
def handle_action(data):
    action = data.get('action')
    logging.info(f"Received action event: {action}")
    command_processor.handle_action(action)

def sensor_data_emit():
    """Background thread to emit sensor data."""
    try:
        while background_thread_running:
            sensor_data = command_processor.get_sensor_data()
            socketio.emit('sensor_data', sensor_data)
            socketio.sleep(0.5)  # Adjust as needed
    except Exception as e:
        logging.error(f"Error in sensor_data_emit: {e}")

def start_server():
    """Starts the Flask-SocketIO server."""
    global background_thread_running, command_processor, video_camera
    command_processor = CommandProcessor()
    video_camera = VideoCamera()

    background_thread_running = True
    socketio.start_background_task(sensor_data_emit)
    socketio.run(app, host='0.0.0.0', port=5013, debug=True, use_reloader=False)

def stop_server():
    """Stops the camera and other hardware components."""
    global background_thread_running, command_processor, video_camera
    if command_processor:
        command_processor.reset_all()
    background_thread_running = False
    if video_camera:
        video_camera.stop()
    logging.info("Server stopped")
