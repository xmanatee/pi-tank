"""Independent systemd stop action, including after a killed server process."""
import pigpio


def stop():
    connection = pigpio.pi('127.0.0.1')
    if not connection.connected:
        raise RuntimeError('Cannot confirm motor stop: local pigpiod is unavailable')
    try:
        for pin in (24, 23, 5, 6):
            result = connection.set_PWM_dutycycle(pin, 0)
            if result < 0:
                raise RuntimeError('Motor stop rejected by pigpiod')
    finally:
        connection.stop()


if __name__ == '__main__':
    stop()
