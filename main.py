import sys
from server import start_server, stop_server

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down server.")
        stop_server()
    except Exception as e:
        print(f"Unexpected error: {e}")
        stop_server()
        sys.exit(1)
