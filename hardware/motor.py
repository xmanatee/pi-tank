import pigpio

class Motor:
    MAX_DUTY = 4095

    def __init__(self, pwm_servo):
        self.pwm_servo = pwm_servo
        self.pwm1 = 24
        self.pwm2 = 23
        self.pwm3 = 5
        self.pwm4 = 6
        for pwm in [self.pwm1, self.pwm2, self.pwm3, self.pwm4]:
            self.pwm_servo.set_mode(pwm, pigpio.OUTPUT)
            self.pwm_servo.set_PWM_frequency(pwm, 50)
            self.pwm_servo.set_PWM_range(pwm, Motor.MAX_DUTY)


    def _set_wheel(self, pwm1, pwm2, duty):
        duty = duty * Motor.MAX_DUTY
        self.pwm_servo.set_PWM_dutycycle(pwm1, 0 if duty > 0 else -duty)
        self.pwm_servo.set_PWM_dutycycle(pwm2, duty if duty > 0 else 0)

    def set_motor_model(self, duty1, duty2):
        self._set_wheel(self.pwm1, self.pwm2, max(min(duty1, 1), -1))
        self._set_wheel(self.pwm3, self.pwm4, max(min(duty2, 1), -1))
