import unittest
import sys
import os
import shutil
from unittest.mock import patch, mock_open
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.file import FileDatabase
from src.db.backend.errors import InvalidAgeError, RecordNotFoundError, TableNotFoundError, FileStorageError

class TestFileDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.db = FileDatabase(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_table(self):
        self.db.create_table("students", ["name", "age"])
        self.assertIn("students", self.db.list_tables())

    def test_create_table_persists(self):
        self.db.create_table("students", ["name"])
        self.db.save()
        new_db = FileDatabase(self.test_dir)
        self.assertIn("students", new_db.list_tables())

    def test_create_record_and_load(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 20})
        self.db.save()
        new_db = FileDatabase(self.test_dir)
        table = new_db.get_table("students")
        records = table.select_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Иван")

    def test_update_record_persists(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 20})
        table.update_record(1, {"age": 21})
        self.db.save()
        new_db = FileDatabase(self.test_dir)
        table = new_db.get_table("students")
        record = table.select_record(1)
        self.assertEqual(record["age"], 21)

    def test_delete_record_persists(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван"})
        table.delete_record(1)
        self.db.save()
        new_db = FileDatabase(self.test_dir)
        table = new_db.get_table("students")
        with self.assertRaises(RecordNotFoundError):
            table.select_record(1)

    def test_invalid_age_error(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        with self.assertRaises(InvalidAgeError):
            table.create_record({"name": "Иван", "age": -5})

    def test_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table("unknown")

    def test_sort_records(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 25})
        table.create_record({"name": "Петр", "age": 20})
        sorted_records = table.sort_records("age", ascending=True)
        self.assertEqual(sorted_records[0]["age"], 20)

    def test_explicit_load(self):
        self.db.create_table("load_test", ["val"])
        self.db.get_table("load_test").create_record({"val": 1})
        self.db.save()
        new_db = FileDatabase(self.test_dir)
        new_db.load()
        self.assertIn("load_test", new_db.list_tables())

    def test_list_tables_empty_dir(self):
        os.makedirs(self.test_dir, exist_ok=True)
        tables = self.db.list_tables()
        self.assertEqual(len(tables), 0)

    def test_file_storage_error_on_write(self):
        self.db.create_table("test", ["name"])
        with patch("builtins.open", side_effect=IOError("Disk full")):
            with self.assertRaises(FileStorageError):
                self.db.save()

    def test_file_storage_error_on_read(self):
        path = self.db._get_table_path("corrupt")
        os.makedirs(self.test_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        with self.assertRaises(FileStorageError):
            self.db.get_table("corrupt")

if __name__ == "__main__":
    unittest.main()