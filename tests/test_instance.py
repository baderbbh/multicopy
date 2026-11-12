import importlib.util
import os
import unittest
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("PySide6"), "PySide6 is not installed")
class InstanceNameTests(unittest.TestCase):
    def test_stable_for_same_user(self):
        from src.main import instance_name
        self.assertEqual(instance_name(), instance_name())

    def test_differs_between_users(self):
        from src.main import instance_name
        with patch.dict(os.environ, {"USERNAME": "user-one"}):
            first = instance_name()
        with patch.dict(os.environ, {"USERNAME": "user-two"}):
            second = instance_name()
        self.assertNotEqual(first, second)
