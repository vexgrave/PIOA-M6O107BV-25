import unittest
import os
import shutil
from pathlib import Path
from src.db.backend.file_csv import CsvDatabase
from src.db.backend.errors import TableAlreadyExistsError, InvalidAgeError, DuplicateIDError

class TestCsvDatabase(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data_csv"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.db = CsvDatabase(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_table(self):
        table = self.db.create_table("students", ["id", "name", "age"])
        self.assertEqual(table.name, "students")
        self.assertTrue((Path(self.test_dir) / "students.csv").exists())
        self.assertTrue((Path(self.test_dir) / "students.meta").exists())

    def test_insert_and_load_record(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        new_db = CsvDatabase(self.test_dir)
        table = new_db.get_table("students")
        records = table.get_records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][0], 1)
        self.assertEqual(records[0][1], "John")

    def test_insert_record_invalid_age(self):
        self.db.create_table("students", ["id", "name", "age"])
        with self.assertRaises(InvalidAgeError):
            self.db.insert_record("students", (1, "John", -5))

    def test_insert_record_duplicate_id(self):
        self.db.create_table("students", ["student_id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        with self.assertRaises(DuplicateIDError):
            self.db.insert_record("students", (1, "Jane", 22))

    def test_select_records_with_filters(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        self.db.insert_record("students", (2, "Jane", 22))
        records = self.db.select_records("students", filters={"age": 20})
        self.assertEqual(len(records), 1)

    def test_select_records_order_by(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 22))
        self.db.insert_record("students", (2, "Jane", 20))
        records = self.db.select_records("students", order_by="age")
        self.assertEqual(records[0][2], 20)

    def test_load_all_tables(self):
        self.db.create_table("students", ["id", "name"])
        self.db.insert_record("students", (1, "John", 20))
        self.db.create_table("courses", ["cid", "title"])
        self.db.insert_record("courses", (101, "Python"))
        self.db.save()
        new_db = CsvDatabase(self.test_dir)
        new_db.load()
        self.assertIsNotNone(new_db.get_table("students"))
        self.assertIsNotNone(new_db.get_table("courses"))