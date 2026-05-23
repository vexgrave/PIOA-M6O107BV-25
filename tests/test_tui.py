import unittest
from io import StringIO
from unittest.mock import patch, MagicMock
from src.db.backend.memory import StudentTable
from src.db.tui import TUI

class TestTUI(unittest.TestCase):
    def setUp(self):
        self.table = StudentTable()
        self.tui = TUI(self.table)

    def test_tui_initialization(self):
        self.assertIsInstance(self.tui, TUI)
        self.assertEqual(self.tui.table, self.table)

    def test_display_records_empty(self):
        with patch('builtins.print') as mock_print:
            self.tui.display_records([])
            mock_print.assert_called_with("Нет данных для отображения")

    def test_display_records_with_data(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('builtins.print') as mock_print:
            self.tui.display_records(self.table.select_record())
            self.assertEqual(mock_print.call_count, 2)

    @patch('builtins.input', side_effect=['1', 'John', 'Doe', '20', 'M'])
    @patch('builtins.print')
    def test_add_record_success(self, mock_print, mock_input):
        self.tui._add_record()
        mock_print.assert_called()

    @patch('builtins.input', side_effect=['1', 'John', 'Doe', '-1', 'M'])
    @patch('builtins.print')
    def test_add_record_invalid_age(self, mock_print, mock_input):
        self.tui._add_record()
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Ошибка' in str(call) for call in calls))

    @patch('builtins.input', side_effect=['1', 'John', 'Doe', '20', 'M', 
                                           '1', 'Jane', 'Smith', '22', 'F'])
    @patch('builtins.print')
    def test_add_record_duplicate_id(self, mock_print, mock_input):
        self.tui._add_record()
        self.tui._add_record()
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Ошибка' in str(call) for call in calls))

    @patch('builtins.input', side_effect=['abc', 'John', 'Doe', '20', 'M'])
    @patch('builtins.print')
    def test_add_record_invalid_id(self, mock_print, mock_input):
        self.tui._add_record()
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Ошибка' in str(call) for call in calls))

    @patch('builtins.input', side_effect=['', '', '', '', ''])
    @patch('builtins.print')
    def test_search_records_no_filters(self, mock_print, mock_input):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.tui._search_records()
        mock_print.assert_called()

    @patch('builtins.input', side_effect=['1', '', '', '', ''])
    @patch('builtins.print')
    def test_search_records_by_id(self, mock_print, mock_input):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        self.tui._search_records()
        mock_print.assert_called()

    @patch('builtins.input', side_effect=['', 'John', '', '', ''])
    @patch('builtins.print')
    def test_search_records_by_name(self, mock_print, mock_input):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.tui._search_records()
        mock_print.assert_called()

    @patch('builtins.input', side_effect=['', '', '', '', ''])
    @patch('builtins.print')
    def test_search_records_not_found(self, mock_print, mock_input):
        self.tui._search_records()
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('не найдены' in str(call).lower() for call in calls))

    @patch('builtins.input', side_effect=['age', 'desc'])
    @patch('builtins.print')
    def test_sort_records_desc(self, mock_print, mock_input):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        self.table.create_record(3, "Alice", "Johnson", 19, "F")
        self.tui._sort_records()
        mock_print.assert_called()

    @patch('builtins.input', side_effect=['first_name', 'asc'])
    @patch('builtins.print')
    def test_sort_records_asc(self, mock_print, mock_input):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        self.tui._sort_records()
        mock_print.assert_called()

    @patch('builtins.input', side_effect=['invalid_field', 'asc'])
    @patch('builtins.print')
    def test_sort_records_invalid_field(self, mock_print, mock_input):
        self.tui._sort_records()
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Ошибка' in str(call) for call in calls))

    @patch('builtins.input', side_effect=['4'])
    @patch('builtins.print')
    def test_run_exit(self, mock_print, mock_input):
        self.tui.run()

    @patch('builtins.input', side_effect=['5', '4'])
    @patch('builtins.print')
    def test_run_invalid_choice(self, mock_print, mock_input):
        self.tui.run()
        calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Неверный выбор' in str(call) for call in calls))

    @patch('builtins.input', side_effect=['2', '1', '', '', '', '', '4'])
    @patch('builtins.print')
    def test_run_search(self, mock_print, mock_input):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.tui.run()

    @patch('builtins.input', side_effect=['3', 'age', 'desc', '4'])
    @patch('builtins.print')
    def test_run_sort(self, mock_print, mock_input):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.tui.run()