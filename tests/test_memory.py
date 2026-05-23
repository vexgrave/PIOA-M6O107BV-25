import unittest
from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableAlreadyExistsError, TableNotFoundError, InvalidAgeError, DuplicateIDError

class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        table = self.db.create_table("students", ["id", "name", "age"])
        self.assertEqual(table.name, "students")
        self.assertEqual(table.columns, ["id", "name", "age"])

    def test_create_table_duplicate(self):
        self.db.create_table("students", ["id", "name"])
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ["id", "name", "age"])

    def test_get_table(self):
        self.db.create_table("students", ["id", "name"])
        table = self.db.get_table("students")
        self.assertIsNotNone(table)
        self.assertIsNone(self.db.get_table("unknown"))

    def test_insert_record(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0], (1, "John", 20))

    def test_insert_record_invalid_age(self):
        self.db.create_table("students", ["id", "name", "age"])
        with self.assertRaises(InvalidAgeError):
            self.db.insert_record("students", (1, "John", -5))

    def test_insert_record_duplicate_id(self):
        self.db.create_table("students", ["student_id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        with self.assertRaises(DuplicateIDError):
            self.db.insert_record("students", (1, "Jane", 22))

    def test_select_records_no_filters(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        self.db.insert_record("students", (2, "Jane", 22))
        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)

    def test_select_records_with_filters(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        self.db.insert_record("students", (2, "Jane", 22))
        records = self.db.select_records("students", filters={"age": 20})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0][1], "John")

    def test_select_records_order_by(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 22))
        self.db.insert_record("students", (2, "Jane", 20))
        self.db.insert_record("students", (3, "Bob", 21))
        records = self.db.select_records("students", order_by="age")
        self.assertEqual(records[0][2], 20)
        self.assertEqual(records[2][2], 22)

    def test_select_records_order_by_reverse(self):
        self.db.create_table("students", ["id", "name", "age"])
        self.db.insert_record("students", (1, "John", 20))
        self.db.insert_record("students", (2, "Jane", 22))
        records = self.db.select_records("students", order_by="age", reverse=True)
        self.assertEqual(records[0][2], 22)
        self.assertEqual(records[1][2], 20)

    def test_select_records_unknown_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("unknown")

    def test_save_load_noop(self):
        self.db.create_table("students", ["id", "name"])
        self.db.save()
        self.db.load()
        table = self.db.get_table("students")
        self.assertIsNotNone(table)