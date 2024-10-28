import time
from RPi import GPIO


# TODO: Rewrite using pigpio
# TODO: Fix
class Ultrasonic:
    MAX_DISTANCE = 300

    def __init__(self):
        self.trigger_pin = 27
        self.echo_pin = 22
        # calculate timeout according to the maximum measuring distance
        self.time_out = self.MAX_DISTANCE * 60
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)

    def pulse_in(self, pin, level, time_out):  # obtain pulse time of a pin under time_out
        t0 = time.time()
        while GPIO.input(pin) != level:
            if (time.time() - t0) > time_out * 0.000001:
                return 0
        t0 = time.time()
        while GPIO.input(pin) == level:
            if (time.time() - t0) > time_out * 0.000001:
                return 0
        pulse_time = (time.time() - t0) * 1000000
        return pulse_time

    def get_distance(self):     # get the measurement results of ultrasonic module,with unit: cm
        distance_cm2 = [0.0, 0.0, 0.0, 0.0, 0.0]
        for i in range(5):
            # make trigger_pin output 10us HIGH level
            GPIO.output(self.trigger_pin, GPIO.HIGH)
            time.sleep(0.00001)     # 10us
            GPIO.output(self.trigger_pin, GPIO.LOW)  # make trigger_pin output LOW level
            ping_time = self.pulse_in(
                self.echo_pin,
                GPIO.HIGH,
                self.time_out)   # read plus time of echo_pin
            # calculate distance with sound speed 340m/s
            distance_cm2[i] = ping_time * 340.0 / 2.0 / 10000.0
        distance_cm2 = sorted(distance_cm2)
        return distance_cm2[2]
