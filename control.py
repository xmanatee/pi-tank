"""One authenticated controller with a server-enforced dead-man timeout."""
import threading
import time

KEYS = frozenset('wasdijkl')
ACTIONS = frozenset({'stop', 'forward', 'backward', 'left', 'right', 'stop_arm',
                     'arm_up', 'arm_down', 'arm_left', 'arm_right', 'light_up_leds', 'reset_servos'})


class Controller:
    def __init__(self, processor, clock=time.monotonic, timeout=0.75):
        self.processor = processor
        self.clock = clock
        self.timeout = timeout
        self.owner = None
        self.deadline = 0
        self.lock = threading.Lock()

    def _expire(self):
        if self.owner is not None and self.clock() >= self.deadline:
            self.processor.stop_all()
            self.owner = None

    def tick(self):
        with self.lock:
            self._expire()

    def heartbeat(self, client):
        with self.lock:
            self._expire()
            if client == self.owner:
                self.deadline = self.clock() + self.timeout

    def disconnect(self, client):
        with self.lock:
            if client == self.owner:
                self.processor.stop_all()
                self.owner = None

    def command(self, client, event, data):
        field = 'action' if event == 'action' else 'key'
        allowed = ACTIONS if event == 'action' else KEYS
        if event not in {'action', 'key_press', 'key_release'} or not isinstance(data, dict):
            return False
        value = data.get(field)
        if not isinstance(value, str) or value not in allowed:
            return False
        with self.lock:
            self._expire()
            if self.owner not in (None, client):
                return False
            self.owner = client
            self.deadline = self.clock() + self.timeout
            getattr(self.processor, 'handle_' + event)(value)
            return True
