import unittest
from unittest.mock import patch

from src.startup import executable_arguments, startup_command


class StartupTests(unittest.TestCase):
    @patch("src.startup.sys.frozen", True, create=True)
    @patch("src.startup.sys.executable", "C:/Apps/MultiCopy.exe")
    def test_packaged_command(self):
        self.assertIn("MultiCopy.exe", startup_command())
        self.assertIn("--hidden", executable_arguments())
