import logging
import eventlet
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
        self.led = Led()  # Initialize the LED class here
        self.current_direction = None
        self.lock = eventlet.semaphore.Semaphore()
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
                # Stop moving servo 1
                self.servos.get(1).stop()
            elif key in ['j', 'l']:
                # Stop moving servo 0
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
            elif action == 'stop_arm':
                self.servos.get(0).stop()
                self.servos.get(1).stop()
            elif action == 'light_up_leds':
                self.led.show_off()
            elif action == 'take_photo':
                # TODO: implement
                pass
            elif action == 'reset_servos':
                self.servos.reset_all()
            elif action == 'make_sound':
                # TODO: check
                pass

    def get_sensor_data(self):
        """Retrieves sensor data."""
        distance = self.ultrasonic.get_distance()
        battery_percentage = self.get_battery_percentage()
        infrared_data = self.infrared.get_all()
        return {
            'distance': distance,
            'battery_percentage': battery_percentage,
            'infrared_data': infrared_data,
        }

    def get_battery_percentage(self):
        """Retrieves battery percentage."""
        # TODO: figure out battery
        return 75

    def reset_all(self):
        """Stops all movements and resets motors and servos."""
        with self.lock:
            logging.info("Resetting all motors and servos to default positions.")
            self.motor.set_motor_model(0, 0)
            self.current_direction = None
            self.servos.reset_all()
