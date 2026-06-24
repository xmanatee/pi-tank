from server import start_server, stop_server

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down server.")
    finally:
        stop_server()
