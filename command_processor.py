import logging
import threading
import pigpio

from hardware.motor import Motor
from hardware.servo import Servos
from hardware.ultrasonic import Ultrasonic
from hardware.led import Led
from hardware.infrared import Infrared

class CommandProcessor:
    """Processes incoming commands and controls hardware accordingly."""

    def __init__(self):
        pwm_servo = pigpio.pi()
        self.motor = Motor(pwm_servo)
        self.servos = Servos(pwm_servo)
        self.ultrasonic = Ultrasonic()
        self.led = Led()
        self.current_direction = None
        self.lock = threading.Lock()
        self.infrared = Infrared()

    def handle_key_press(self, key):
        """Handles key press events from the client."""
        with self.lock:
            if key == 'w':
                self.motor.set_motor_model(1, 1)
                self.current_direction = 'forward'
            elif key == 's':
                self.motor.set_motor_model(-1, -1)
                self.current_direction = 'backward'
            elif key == 'a':
                self.motor.set_motor_model(-1, 1)
                self.current_direction = 'left'
            elif key == 'd':
                self.motor.set_motor_model(1, -1)
                self.current_direction = 'right'
            elif key == 'i':
                self.servos.get(1).start(1)
            elif key == 'k':
                self.servos.get(1).start(-1)
            elif key == 'j':
                self.servos.get(0).start(-1)
            elif key == 'l':
                self.servos.get(0).start(1)

    def handle_key_release(self, key):
        """Handles key release events from the client."""
        with self.lock:
            logging.info(f"Key released: {key}")
            if ((key == 'w' and self.current_direction == 'forward') or
                (key == 's' and self.current_direction == 'backward') or
                (key == 'a' and self.current_direction == 'left') or
                (key == 'd' and self.current_direction == 'right')):
                self.motor.set_motor_model(0, 0)
                self.current_direction = None
            elif key in ['i', 'k']:
                self.servos.get(1).stop()
            elif key in ['j', 'l']:
                self.servos.get(0).stop()

    def handle_action(self, action):
        """Handles action commands from web buttons."""
        with self.lock:
            logging.info(f"Action received: {action}")
            if action == 'stop':
                self.motor.set_motor_model(0, 0)
                self.current_direction = None
            elif action == 'forward':
                self.motor.set_motor_model(1, 1)
                self.current_direction = 'forward'
            elif action == 'backward':
                self.motor.set_motor_model(-1, -1)
                self.current_direction = 'backward'
            elif action == 'left':
                self.motor.set_motor_model(-1, 1)
                self.current_direction = 'left'
            elif action == 'right':
                self.motor.set_motor_model(1, -1)
                self.current_direction = 'right'
            elif action == 'stop_arm':
                self.servos.get(0).stop()
                self.servos.get(1).stop()
            elif action == 'arm_up':
                self.servos.get(1).start(1)
            elif action == 'arm_down':
                self.servos.get(1).start(-1)
            elif action == 'arm_left':
                self.servos.get(0).start(-1)
            elif action == 'arm_right':
                self.servos.get(0).start(1)
            elif action == 'light_up_leds':
                self.led.show_off()
            elif action == 'reset_servos':
                for servo in self.servos.servos.values():
                    servo.stop()
                self.servos.reset_all()
            else:
                logging.warning(f"Unknown action: {action}")

    def get_sensor_data(self):
        """Retrieves sensor data."""
        distance = self.ultrasonic.get_distance()
        infrared_data = self.infrared.get_all()
        return {
            'distance': distance,
            'infrared_data': infrared_data,
        }

    def stop_all(self):
        """Stop motors and continuous servo motion without moving to a new position."""
        with self.lock:
            self.motor.set_motor_model(0, 0)
            self.current_direction = None
            for servo in self.servos.servos.values():
                servo.stop()

    def reset_all(self):
        """Stops all movements and resets motors and servos."""
        with self.lock:
            logging.info("Resetting all motors and servos to default positions.")
            self.motor.set_motor_model(0, 0)
            self.current_direction = None
            for servo in self.servos.servos.values():
                servo.stop()
            self.servos.reset_all()
