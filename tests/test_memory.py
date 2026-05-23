import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import InvalidAgeError, RecordNotFoundError, TableNotFoundError

class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        self.db.create_table("students", ["name", "age"])
        self.assertIn("students", self.db.list_tables())

    def test_create_table_duplicate(self):
        self.db.create_table("students", ["name"])
        with self.assertRaises(ValueError):
            self.db.create_table("students", ["age"])

    def test_get_table(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        self.assertEqual(table.name, "students")

    def test_get_table_not_found(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table("unknown")

    def test_create_record(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        record_id = table.create_record({"name": "Иван", "age": 20})
        self.assertEqual(record_id, 1)

    def test_create_record_invalid_age(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        with self.assertRaises(InvalidAgeError):
            table.create_record({"name": "Иван", "age": -5})

    def test_select_record(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 20})
        record = table.select_record(1)
        self.assertEqual(record["name"], "Иван")

    def test_select_record_not_found(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        with self.assertRaises(RecordNotFoundError):
            table.select_record(999)

    def test_select_all(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван"})
        table.create_record({"name": "Петр"})
        records = table.select_all()
        self.assertEqual(len(records), 2)

    def test_select_by_filter(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 20})
        table.create_record({"name": "Петр", "age": 21})
        results = table.select_by_filter("age", 20)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Иван")

    def test_select_by_filter_invalid_field(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        with self.assertRaises(ValueError):
            table.select_by_filter("invalid", "val")

    def test_update_record(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 20})
        table.update_record(1, {"age": 21})
        record = table.select_record(1)
        self.assertEqual(record["age"], 21)

    def test_update_record_invalid_age(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 20})
        with self.assertRaises(InvalidAgeError):
            table.update_record(1, {"age": -5})

    def test_update_record_not_found(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        with self.assertRaises(RecordNotFoundError):
            table.update_record(999, {"name": "Test"})

    def test_delete_record(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван"})
        table.delete_record(1)
        with self.assertRaises(RecordNotFoundError):
            table.select_record(1)

    def test_delete_record_not_found(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        with self.assertRaises(RecordNotFoundError):
            table.delete_record(999)

    def test_sort_records_ascending(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 25})
        table.create_record({"name": "Петр", "age": 20})
        sorted_records = table.sort_records("age", ascending=True)
        self.assertEqual(sorted_records[0]["age"], 20)
        self.assertEqual(sorted_records[1]["age"], 25)

    def test_sort_records_descending(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 25})
        table.create_record({"name": "Петр", "age": 20})
        sorted_records = table.sort_records("age", ascending=False)
        self.assertEqual(sorted_records[0]["age"], 25)
        self.assertEqual(sorted_records[1]["age"], 20)

    def test_sort_invalid_field(self):
        self.db.create_table("students", ["name"])
        table = self.db.get_table("students")
        with self.assertRaises(ValueError):
            table.sort_records("invalid")

    def test_to_dict_and_from_dict(self):
        self.db.create_table("students", ["name", "age"])
        table = self.db.get_table("students")
        table.create_record({"name": "Иван", "age": 20})
        data = table.to_dict()
        new_table = table.__class__.from_dict(data)
        self.assertEqual(new_table.select_record(1)["name"], "Иван")

if __name__ == "__main__":
    unittest.main()