import logging
import hmac
import os
import threading
from flask import Flask, render_template, Response, request, session, redirect
from flask_socketio import SocketIO, emit

from constants import *
from command_processor import CommandProcessor
from video_streaming import VideoCamera
from control import Controller

app = Flask(__name__, static_folder='templates')
socketio = SocketIO(app, async_mode=ASYNC_MODE)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Strict')
controller = None
watchdog_stop = threading.Event()
watchdog_thread = None


@app.before_request
def require_login():
    if request.path != '/login' and not session.get('authenticated'):
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = os.environ.get('TANK_TOKEN', '')
        if token and hmac.compare_digest(request.form.get('token', ''), token):
            session.clear()
            session['authenticated'] = True
            return redirect('/')
        return render_template('login.html', failed=True), 401
    return render_template('login.html', failed=False)

background_thread_running = True
command_processor = None
video_camera = None

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        if frame:
            logging.debug("Sending a video frame")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            logging.warning("No frame received from camera")
        socketio.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def handle_connect(auth=None):
    if not session.get('authenticated'):
        return False
    emit('connection_status', {'status': 'Connected'})


@socketio.on('disconnect')
def handle_disconnect(reason=None):
    if controller:
        controller.disconnect(request.sid)


@socketio.on('heartbeat')
def handle_heartbeat():
    if controller:
        controller.heartbeat(request.sid)


@socketio.on('key_press')
def handle_key_press(data):
    return controller.command(request.sid, 'key_press', data)


@socketio.on('key_release')
def handle_key_release(data):
    return controller.command(request.sid, 'key_release', data)


@socketio.on('action')
def handle_action(data):
    return controller.command(request.sid, 'action', data)


def watchdog():
    while not watchdog_stop.wait(0.05):
        controller.tick()


def sensor_data_emit():
    """Background thread to emit sensor data."""
    while background_thread_running:
        sensor_data = command_processor.get_sensor_data()
        socketio.emit('sensor_data', sensor_data)
        socketio.sleep(0.5)

def initialize_hardware():
    """Initialize hardware in the single serving worker, after it forks."""
    global background_thread_running, command_processor, video_camera, controller, watchdog_thread
    token = os.environ.get('TANK_TOKEN', '')
    secret = os.environ.get('TANK_SESSION_SECRET', '')
    if len(token) < 32 or len(secret) < 32:
        raise RuntimeError('Set independent TANK_TOKEN and TANK_SESSION_SECRET values of at least 32 characters')
    app.secret_key = secret
    command_processor = CommandProcessor()
    controller = Controller(command_processor)
    watchdog_stop.clear()
    watchdog_thread = threading.Thread(target=watchdog, daemon=True)
    watchdog_thread.start()
    video_camera = VideoCamera()

    background_thread_running = True
    socketio.start_background_task(sensor_data_emit)

def stop_server():
    """Stops the camera and other hardware components."""
    global background_thread_running, command_processor, video_camera
    watchdog_stop.set()
    if watchdog_thread:
        watchdog_thread.join(timeout=2)
    if command_processor:
        command_processor.stop_all()
    background_thread_running = False
    if video_camera:
        video_camera.stop()
    logging.info("Server stopped")
