import unittest
import sys
import io
from unittest.mock import patch
from src.db.tui import DatabaseTUI


class TestDatabaseTUI(unittest.TestCase):

    def setUp(self):
        self.tui = DatabaseTUI("memory")

    def test_create_table_menu_success(self):
        inputs = ['users', 'name,age']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.create_table_menu()
                self.assertIn('users', self.tui.db.list_tables())
                self.assertIn('успешно создана', mock_out.getvalue())

    def test_create_table_menu_empty_columns(self):
        inputs = ['users', '']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.create_table_menu()
                self.assertNotIn('users', self.tui.db.list_tables())
                self.assertIn('введите хотя бы одно поле', mock_out.getvalue())

    def test_add_record_menu_success(self):
        self.tui.db.create_table('users', ['name', 'age'])
        inputs = ['users', 'Alice', '25']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.add_record_menu()
                self.assertEqual(len(self.tui.db.get_table('users').rows), 1)
                self.assertIn('Запись добавлена', mock_out.getvalue())

    def test_add_record_menu_no_tables(self):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
            self.tui.add_record_menu()
            self.assertIn('Создайте таблицу сначала', mock_out.getvalue())

    def test_read_records_menu_all(self):
        self.tui.db.create_table('users', ['name'])
        self.tui.db.get_table('users').add({'name': 'Alice'})
        inputs = ['users', '']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.read_records_menu()
                output = mock_out.getvalue()
                self.assertIn('Найдено записей: 1', output)
                self.assertIn('Alice', output)

    def test_read_records_menu_filter(self):
        self.tui.db.create_table('users', ['name'])
        self.tui.db.get_table('users').add({'name': 'Alice'})
        self.tui.db.get_table('users').add({'name': 'Bob'})
        inputs = ['users', 'name=Alice']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.read_records_menu()
                self.assertIn('Найдено записей: 1', mock_out.getvalue())

    def test_read_records_menu_no_tables(self):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
            self.tui.read_records_menu()
            self.assertIn('Нет доступных таблиц', mock_out.getvalue())

    def test_update_record_menu_success(self):
        self.tui.db.create_table('users', ['name', 'age'])
        table = self.tui.db.get_table('users')
        table.add({'name': 'Old', 'age': 20})
        inputs = ['users', '1', 'New', '30']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.update_record_menu()
                self.assertEqual(table.rows[0]['name'], 'New')
                self.assertIn('успешно обновлена', mock_out.getvalue())

    def test_update_record_menu_invalid_id(self):
        self.tui.db.create_table('users', ['name'])
        inputs = ['users', 'abc']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.update_record_menu()
                self.assertIn('ID должен быть числом', mock_out.getvalue())

    def test_update_record_menu_not_found(self):
        self.tui.db.create_table('users', ['name'])
        inputs = ['users', '99', '']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.update_record_menu()
                self.assertIn('Запись с таким ID не найдена', mock_out.getvalue())

    def test_delete_record_menu_success(self):
        self.tui.db.create_table('users', ['name'])
        table = self.tui.db.get_table('users')
        table.add({'name': 'ToDelete'})
        inputs = ['users', '1']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.delete_record_menu()
                self.assertEqual(len(table.rows), 0)
                self.assertIn('успешно удалена', mock_out.getvalue())

    def test_delete_record_menu_not_found(self):
        self.tui.db.create_table('users', ['name'])
        inputs = ['users', '99']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.delete_record_menu()
                self.assertIn('Запись с таким ID не найдена', mock_out.getvalue())

    def test_sort_records_menu_success(self):
        self.tui.db.create_table('users', ['name'])
        table = self.tui.db.get_table('users')
        table.add({'name': 'Bob'})
        table.add({'name': 'Alice'})
        inputs = ['users', 'name', '1']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.sort_records_menu()
                self.assertIn('отсортированы', mock_out.getvalue())

    def test_create_index_menu_success(self):
        self.tui.db.create_table('users', ['name'])
        inputs = ['users', 'name']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.create_index_menu()
                self.assertIn('Индекс создан', mock_out.getvalue())

    def test_run_menu_invalid_choice(self):
        inputs = ['99', '8']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.run()
                output = mock_out.getvalue()
                self.assertIn('Неверный пункт меню', output)
                self.assertIn('Выход из программы', output)

    def test_run_menu_exit(self):
        inputs = ['8']
        with patch('builtins.input', side_effect=inputs):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_out:
                self.tui.run()
                self.assertIn('Выход из программы', mock_out.getvalue())


if __name__ == "__main__":
    unittest.main()