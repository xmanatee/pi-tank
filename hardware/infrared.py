from RPi import GPIO

# TODO: Rewrite using pigpio
class Infrared:
    def __init__(self):
        self.ir01 = 16
        self.ir02 = 20
        self.ir03 = 21
        self.lrm = 0x00
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ir01, GPIO.IN)
        GPIO.setup(self.ir02, GPIO.IN)
        GPIO.setup(self.ir03, GPIO.IN)
    
    def get(self, id):
        return self.get_all()[id]

    def get_all(self):
        return [
            GPIO.input(self.ir01),
            GPIO.input(self.ir02),
            GPIO.input(self.ir03),
        ]

    def run(self, motor):
        while True:
            ir_states = self.get_all()
            if ir_states == [False, True, False]:
                motor.set_motor_model(1200, 1200)
            elif ir_states == [True, False, False]:
                motor.set_motor_model(-1500, 2500)
            elif ir_states == [True, True, False]:
                motor.set_motor_model(-2000, 4000)
            elif ir_states == [False, False, True]:
                motor.set_motor_model(2500, -1500)
            elif ir_states == [False, True, True]:
                motor.set_motor_model(4000, -2000)
