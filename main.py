import os
from gunicorn.app.base import BaseApplication


def initialize_worker(_worker):
    from server import initialize_hardware, stop_server
    try:
        initialize_hardware()
    except BaseException:
        stop_server()
        raise


def stop_worker(_server, _worker):
    from server import stop_server
    stop_server()


class TankServer(BaseApplication):
    def load_config(self):
        for key, value in {
            'bind': os.environ.get('TANK_BIND', '127.0.0.1') + ':5013',
            'workers': 1,
            'worker_class': 'gthread',
            'threads': 16,
            'preload_app': False,
            'post_worker_init': initialize_worker,
            'worker_exit': stop_worker,
            'graceful_timeout': 5,
            'timeout': 30,
            'accesslog': None,
        }.items():
            self.cfg.set(key, value)

    def load(self):
        from server import app
        return app


if __name__ == '__main__':
    TankServer().run()
