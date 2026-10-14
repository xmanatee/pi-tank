import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class StopMotorTests(unittest.TestCase):
    def load(self, connected=True, result=0):
        connection = Mock(connected=connected)
        connection.set_PWM_dutycycle.return_value = result
        spec = importlib.util.spec_from_file_location('stop_motors', Path(__file__).with_name('stop_motors.py'))
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'pigpio': types.SimpleNamespace(pi=lambda _host: connection)}):
            spec.loader.exec_module(module)
        return module, connection

    def test_stops_each_motor_output_and_closes_connection(self):
        module, connection = self.load()
        module.stop()
        self.assertEqual([call.args for call in connection.set_PWM_dutycycle.call_args_list], [(24, 0), (23, 0), (5, 0), (6, 0)])
        connection.stop.assert_called_once()

    def test_unavailable_daemon_fails_visibly(self):
        module, connection = self.load(connected=False)
        with self.assertRaises(RuntimeError): module.stop()
        connection.set_PWM_dutycycle.assert_not_called()

    def test_rejected_stop_fails_visibly_and_closes_connection(self):
        module, connection = self.load(result=-1)
        with self.assertRaises(RuntimeError): module.stop()
        connection.stop.assert_called_once()


if __name__ == '__main__':
    unittest.main()
