import unittest
import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.__main__ import __name__ as main_module

class TestMainArgs(unittest.TestCase):
    @patch('sys.argv', ['__main__.py', 'memory'])
    @patch('src.db.tui.DatabaseTUI.run')
    def test_memory_arg(self, mock_run):
        from src.db import __main__
        self.assertEqual(__main__.sys.argv[1], 'memory')

    @patch('sys.argv', ['__main__.py', 'file'])
    @patch('src.db.tui.DatabaseTUI.run')
    def test_file_arg(self, mock_run):
        from src.db import __main__
        self.assertEqual(__main__.sys.argv[1], 'file')

    @patch('sys.argv', ['__main__.py'])
    @patch('src.db.tui.DatabaseTUI.run')
    def test_default_arg(self, mock_run):
        from src.db import __main__
        self.assertEqual(len(__main__.sys.argv), 1)

if __name__ == "__main__":
    unittest.main()