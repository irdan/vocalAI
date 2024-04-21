import unittest
from unittest.mock import Mock
from event_manager import EventManager

class TestEventManager(unittest.TestCase):

    def setUp(self):
        EventManager.reset_instance()

    def tearDown(self):
        EventManager.reset_instance()

    def test_get_instance(self):
        self.assertIsNone(EventManager._instance)
        event_manager = EventManager()
        self.assertIsNotNone(EventManager._instance)

    def test_init(self):
        self.assertIsNone(EventManager._instance)
        event_manager = EventManager()
        self.assertIsNotNone(event_manager)

    def test_singleton_behavior(self):
        self.assertIsNone(EventManager._instance)
        event_manager1 = EventManager()
        with self.assertRaises(Exception):
            event_manager2 = EventManager()
        event_manager2 = EventManager.get_instance()
        self.assertIs(event_manager1, event_manager2)

    def test_subscribe(self):
        event_manager = EventManager()
        mock_callback = Mock()
        event_manager.subscribe("event_name", mock_callback)
        self.assertIn("event_name", event_manager.listeners)
        self.assertEqual(mock_callback, event_manager.listeners["event_name"][0])

        mock_callback1 = Mock()
        event_manager.subscribe("event_name", mock_callback1)
        self.assertIn("event_name", event_manager.listeners)
        self.assertEqual(mock_callback, event_manager.listeners["event_name"][0])
        self.assertEqual(mock_callback1, event_manager.listeners["event_name"][1])

    def test_publish(self):
        event_manager = EventManager()
        mock_callback = Mock()
        event_manager.subscribe("event_name", mock_callback)
        event_manager.publish("event_name", "data")
        mock_callback.assert_called_once()
        mock_callback.assert_called_with("data")

    def test_unsubscribe(self):
        event_manager = EventManager()
        mock_callback = Mock()
        event_manager.subscribe("event_name", mock_callback)
        self.assertIn("event_name", event_manager.listeners)
        self.assertEqual(mock_callback, event_manager.listeners["event_name"][0])
        
        event_manager.unsubscribe("event_name", mock_callback)
        self.assertNotIn("event_name", event_manager.listeners)

        event_manager.subscribe("event_name", mock_callback)
        mock_callback1 = Mock()
        event_manager.subscribe("event_name", mock_callback1)
        event_manager.unsubscribe("event_name", mock_callback)
        self.assertIn("event_name", event_manager.listeners)
