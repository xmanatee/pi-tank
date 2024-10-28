import time

from libcamera import Transform
from picamera2 import Picamera2, Preview
import pigpio

from servo import Servos
from infrared import Infrared
from led import Led, Color
from motor import Motor
from ultrasonic import Ultrasonic


# TODO: Rewrite using pigpio
def test_led():
    led = Led()
    try:
        led.led_index(0x01, 255, 0, 0)  # red
        led.led_index(0x02, 0, 255, 0)  # green
        led.led_index(0x04, 0, 0, 255)  # blue
        led.led_index(0x08, 255, 255, 255)  # white

        print("The LED has been lit, the color is red green blue white")
        time.sleep(3)  # wait 3s
        led.color_wipe(Color(0, 0, 0))  # turn off the light
        print("\nEnd of program")
    except KeyboardInterrupt:
        led.color_wipe(Color(0, 0, 0))  # turn off the light
        print("\nEnd of program")


def test_motor():
    pwm_servo = pigpio.pi()
    motor = Motor(pwm_servo)
    try:
        motor.set_motor_model(2000, 2000)
        print("The car is moving forward")
        time.sleep(1)
        motor.set_motor_model(-2000, -2000)
        print("The car is going backwards")
        time.sleep(1)
        motor.set_motor_model(-2000, 2000)
        print("The car is turning left")
        time.sleep(1)
        motor.set_motor_model(2000, -2000)
        print("The car is turning right")
        time.sleep(1)
        motor.set_motor_model(0, 0)
        print("\nEnd of program")
    except KeyboardInterrupt:
        motor.set_motor_model(0, 0)
        print("\nEnd of program")


def test_ultrasonic():
    ultrasonic = Ultrasonic()
    try:
        while True:
            data = ultrasonic.get_distance()  # Get the value
            distance = int(data)
            print("Obstacle distance is " + str(distance) + "CM")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEnd of program")


def test_infrared():
    infrared = Infrared()
    try:
        while True:
            print(infrared.get_all())
    except KeyboardInterrupt:
        print("\nEnd of program")

def test_infrared2():
    print('Program is starting ... ')
    pwm_servo = pigpio.pi()
    servos = Servos(pwm_servo)
    motor = Motor(pwm_servo)
    infrared = Infrared()

    servos.get(0).set(90)
    servos.get(1).set(140)
    try:
        infrared.run(motor)
    except KeyboardInterrupt:
        motor.set_motor_model(0, 0)
        servos.get(0).set(90)
        print("\nEnd of program")

def test_servo():
    pwm_servo = pigpio.pi()
    servos = Servos(pwm_servo)
    try:
        while True:
            for i in range(90, 150, 1):
                servos.get(0).set(i)
                time.sleep(0.01)
            for i in range(140, 90, -1):
                servos.get(1).set(i)
                time.sleep(0.01)
            for i in range(90, 140, 1):
                servos.get(1).set(i)
                time.sleep(0.01)
            for i in range(150, 90, -1):
                servos.get(0).set(i)
                time.sleep(0.01)
    except KeyboardInterrupt:
        servos.get(0).set(90)
        servos.get(1).set(140)
        print("\nEnd of program")


def test_camera():
    # Capture a JPEG while still running in the preview mode. When you
    # capture to a file, the return value is the metadata for that image.
    preview_enabled = False
    picam2 = Picamera2()

    if preview_enabled:
        preview_config = picam2.create_preview_configuration(
            main={"size": (640, 480)}, transform=Transform(hflip=1, vflip=1))
        picam2.configure(preview_config)
        picam2.start_preview(Preview.QTGL)
    picam2.start()
    time.sleep(2)
    metadata = picam2.capture_file("image.jpg")
    print(metadata)
    picam2.close()


if __name__ == '__main__':

    print('Program is starting ... ')
    import sys
    if len(sys.argv) < 2:
        print("Parameter error: Please assign the device")
        exit()
    if sys.argv[1] == 'Led':
        test_led()
    elif sys.argv[1] == 'Motor':
        test_motor()
    elif sys.argv[1] == 'Ultrasonic':
        test_ultrasonic()
    elif sys.argv[1] == 'Infrared':
        test_infrared()
    elif sys.argv[1] == 'Infrared2':
        test_infrared2()
    elif sys.argv[1] == 'Servo':
        test_servo()
    elif sys.argv[1] == 'Camera':
        test_camera()

