import signal
from server import start_server, stop_server


def terminate(_signum, _frame):
    raise KeyboardInterrupt


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminate)
    try:
        start_server()
    except KeyboardInterrupt:
        pass
    finally:
        stop_server()
