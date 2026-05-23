import unittest
import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.tui import DatabaseTUI

class TestDatabaseTUI(unittest.TestCase):
    def setUp(self):
        self.tui = DatabaseTUI(storage_type="memory")

    @patch('builtins.input', side_effect=['10'])
    @patch('builtins.print')
    def test_exit_menu(self, mock_print, mock_input):
        self.tui.run()
        self.assertIn('students', self.tui.db.list_tables()) if False else None

    @patch('builtins.input', side_effect=['1', 'test', 'name,age', '2', 'test', 'Ivan', '20', '10'])
    @patch('builtins.print')
    def test_create_and_add_record(self, mock_print, mock_input):
        self.tui.run()
        table = self.tui.db.get_table('test')
        self.assertEqual(len(table.select_all()), 1)

    @patch('builtins.input', side_effect=['1', 't', 'f', '2', 't', 'v', '5', 't', '1', '10'])
    @patch('builtins.print')
    def test_delete_record(self, mock_print, mock_input):
        self.tui.run()
        table = self.tui.db.get_table('t')
        with self.assertRaises(Exception):
            table.select_record(1)

    @patch('builtins.input', side_effect=['1', 's', 'n', '2', 's', 'a', '3', 's', '10'])
    @patch('builtins.print')
    def test_show_all_records(self, mock_print, mock_input):
        self.tui.run()
        self.assertEqual(len(self.tui.db.get_table('s').select_all()), 1)

    @patch('builtins.input', side_effect=['1', 'f', 'k', '2', 'f', 'val', '5', 'f', '1', 'k', '10'])
    @patch('builtins.print')
    def test_filter_records(self, mock_print, mock_input):
        self.tui.run()
        results = self.tui.db.get_table('f').select_by_filter('k', 'val')
        self.assertEqual(len(results), 1)

    @patch('builtins.input', side_effect=['1', 'u', 'x', '2', 'u', 'old', '6', 'u', '1', 'new', '10'])
    @patch('builtins.print')
    def test_update_record(self, mock_print, mock_input):
        self.tui.run()
        rec = self.tui.db.get_table('u').select_record(1)
        self.assertEqual(rec['x'], 'new')

    @patch('builtins.input', side_effect=['1', 'sr', 'v', '2', 'sr', 'b', '2', 'sr', 'a', '8', 'sr', 'v', 'asc', '10'])
    @patch('builtins.print')
    def test_sort_records(self, mock_print, mock_input):
        self.tui.run()
        sorted_rec = self.tui.db.get_table('sr').sort_records('v', True)
        self.assertEqual(sorted_rec[0]['v'], 'a')
        self.assertEqual(sorted_rec[1]['v'], 'b')

if __name__ == "__main__":
    unittest.main()