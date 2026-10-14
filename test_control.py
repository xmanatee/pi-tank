import unittest
from control import Controller


class Processor:
    def __init__(self): self.commands = []; self.stops = 0
    def stop_all(self): self.stops += 1
    def handle_action(self, value): self.commands.append(value)
    def handle_key_press(self, value): self.commands.append(value)
    def handle_key_release(self, value): self.commands.append(value)


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.processor = Processor()
        self.control = Controller(self.processor, clock=lambda: self.now)

    def test_deadman_stops_motion_without_client_disconnect(self):
        self.assertTrue(self.control.command('driver', 'action', {'action': 'forward'}))
        self.now = 0.7; self.control.heartbeat('driver')
        self.now = 1.0; self.control.tick()
        self.assertEqual(self.processor.stops, 0)
        self.now = 1.5; self.control.tick()
        self.assertEqual(self.processor.stops, 1)
        self.assertIsNone(self.control.owner)
        self.control.tick()
        self.assertEqual(self.processor.stops, 1)

    def test_other_client_cannot_control_extend_or_stop_controller(self):
        self.control.command('driver', 'key_press', {'key': 'w'})
        self.assertFalse(self.control.command('observer', 'action', {'action': 'right'}))
        self.control.disconnect('observer')
        self.now = 0.6; self.control.heartbeat('observer')
        self.now = 0.8; self.control.tick()
        self.assertEqual(self.processor.commands, ['w'])
        self.assertEqual(self.processor.stops, 1)

    def test_invalid_input_cannot_touch_hardware(self):
        for data in [None, 'forward', {'action': []}, {'action': 'shell'}, {'action': 'FORWARD'}]:
            self.assertFalse(self.control.command('driver', 'action', data))
        self.assertEqual(self.processor.commands, [])
        self.assertIsNone(self.control.owner)

    def test_controller_disconnect_stops_all_actuators(self):
        self.control.command('driver', 'action', {'action': 'arm_up'})
        self.control.disconnect('driver')
        self.assertEqual(self.processor.stops, 1)
        self.assertTrue(self.control.command('next-driver', 'action', {'action': 'backward'}))


if __name__ == '__main__': unittest.main()
