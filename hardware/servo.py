import pigpio
import threading
import time
import logging

class Servo:
    def __init__(self, pwm_servo, channel, min_angle=0, max_angle=180):
        self.pwm_servo = pwm_servo
        self.channel = channel
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.pwm_servo.set_mode(self.channel, pigpio.OUTPUT)
        self.pwm_servo.set_PWM_frequency(self.channel, 50)
        self.pwm_servo.set_PWM_range(self.channel, 4000)

        # Track servo angle
        # Start at the midpoint
        self.angle = (min_angle + max_angle) // 2
        self.servo_moving = threading.Event()
        self.servo_thread = None

    def angle_range(self, init_angle):
        return max(self.min_angle, min(self.max_angle, init_angle))

    def set(self, angle):
        angle = int(self.angle_range(angle))
        self.angle = angle
        self.pwm_servo.set_PWM_dutycycle(self.channel, 80 + (400 / 180) * angle)

    def reset(self):
        """Resets servo to default position."""
        self.set((self.min_angle + self.max_angle) // 2)

    def start(self, direction):
        """Starts moving the servo continuously in a direction."""
        if not self.servo_moving.is_set():
            self.servo_moving.set()
            self.servo_thread = threading.Thread(target=self._move_servo_continuous, args=(direction,))
            self.servo_thread.daemon = True
            self.servo_thread.start()

    def stop(self):
        """Stops moving the servo."""
        if self.servo_moving.is_set():
            self.servo_moving.clear()

    def _move_servo_continuous(self, direction):
        """Continuously moves the servo until stopped."""
        while self.servo_moving.is_set():
            self._move_to(2 * direction)  # Adjust the increment as needed
            time.sleep(0.05)  # Adjust speed as needed

    def _move_to(self, delta):
        """Moves the servo by a delta angle."""
        new_angle = self.angle + delta
        self.set(new_angle)
        logging.info(f"Moved servo on channel {self.channel} to angle {new_angle}")

class Servos:
    def __init__(self, pwn_servo):
        self.servos = {
            0: Servo(pwn_servo, 7, min_angle=90, max_angle=150),
            1: Servo(pwn_servo, 8, min_angle=90, max_angle=150),
        }
    
    def get(self, id):
        return self.servos[id]

    def reset_all(self):
        for servo in self.servos.values():
            servo.reset()
