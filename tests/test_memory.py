import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError, StudentTableError


class TestStudentTableCreate(unittest.TestCase):
    def setUp(self):
        self.table = StudentTable()

    def test_create_record_success(self):
        record_id = self.table.create_record("Иван", "Иванов", 20, "М")
        self.assertEqual(record_id, 1)

    def test_create_multiple_records(self):
        id1 = self.table.create_record("Иван", "Иванов", 20, "М")
        id2 = self.table.create_record("Петр", "Петров", 21, "М")
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)

    def test_create_record_invalid_age(self):
        with self.assertRaises(InvalidAgeError):
            self.table.create_record("Иван", "Иванов", -5, "М")


class TestStudentTableSelect(unittest.TestCase):
    def setUp(self):
        self.table = StudentTable()
        self.table.create_record("Иван", "Иванов", 20, "М")
        self.table.create_record("Петр", "Петров", 21, "Ж")

    def test_select_record_by_id(self):
        record = self.table.select_record(1)
        self.assertEqual(record[1], "Иван")
        self.assertEqual(record[2], "Иванов")
        self.assertEqual(record[3], 20)

    def test_select_record_not_found(self):
        with self.assertRaises(KeyError):
            self.table.select_record(999)

    def test_select_all(self):
        records = self.table.select_all()
        self.assertEqual(len(records), 2)

    def test_select_by_filter_first_name(self):
        results = self.table.select_by_filter("first_name", "Иван")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Иван")

    def test_select_by_filter_age(self):
        results = self.table.select_by_filter("age", 21)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][2], "Петров")

    def test_select_by_filter_invalid_field(self):
        with self.assertRaises(ValueError):
            self.table.select_by_filter("invalid_field", "value")


class TestStudentTableUpdate(unittest.TestCase):
    def setUp(self):
        self.table = StudentTable()
        self.table.create_record("Иван", "Иванов", 20, "М")

    def test_update_record_success(self):
        result = self.table.update_record(1, first_name="Петр")
        self.assertTrue(result)
        record = self.table.select_record(1)
        self.assertEqual(record[1], "Петр")

    def test_update_record_partial(self):
        self.table.update_record(1, age=25)
        record = self.table.select_record(1)
        self.assertEqual(record[3], 25)
        self.assertEqual(record[1], "Иван")

    def test_update_record_not_found(self):
        with self.assertRaises(KeyError):
            self.table.update_record(999, first_name="Test")

    def test_update_record_invalid_age(self):
        with self.assertRaises(InvalidAgeError):
            self.table.update_record(1, age=-10)


class TestStudentTableDelete(unittest.TestCase):
    def setUp(self):
        self.table = StudentTable()
        self.table.create_record("Иван", "Иванов", 20, "М")

    def test_delete_record_success(self):
        result = self.table.delete_record(1)
        self.assertTrue(result)
        with self.assertRaises(KeyError):
            self.table.select_record(1)

    def test_delete_record_not_found(self):
        with self.assertRaises(KeyError):
            self.table.delete_record(999)


class TestStudentTableSort(unittest.TestCase):
    def setUp(self):
        self.table = StudentTable()
        self.table.create_record("Иван", "Иванов", 25, "М")
        self.table.create_record("Петр", "Петров", 20, "Ж")
        self.table.create_record("Анна", "Сидорова", 30, "Ж")

    def test_sort_by_age_ascending(self):
        sorted_records = self.table.sort_records("age", ascending=True)
        self.assertEqual(sorted_records[0][3], 20)
        self.assertEqual(sorted_records[2][3], 30)

    def test_sort_by_age_descending(self):
        sorted_records = self.table.sort_records("age", ascending=False)
        self.assertEqual(sorted_records[0][3], 30)
        self.assertEqual(sorted_records[2][3], 20)

    def test_sort_by_first_name(self):
        sorted_records = self.table.sort_records("first_name", ascending=True)
        self.assertEqual(sorted_records[0][1], "Анна")

    def test_sort_invalid_field(self):
        with self.assertRaises(ValueError):
            self.table.sort_records("invalid", True)


class TestStudentTableEdgeCases(unittest.TestCase):
    def setUp(self):
        self.table = StudentTable()

    def test_empty_table_select_all(self):
        records = self.table.select_all()
        self.assertEqual(len(records), 0)

    def test_empty_table_sort(self):
        sorted_records = self.table.sort_records("age")
        self.assertEqual(len(sorted_records), 0)

    def test_create_record_empty_strings(self):
        record_id = self.table.create_record("", "", 0, "")
        self.assertEqual(record_id, 1)
        record = self.table.select_record(1)
        self.assertEqual(record[1], "")
        self.assertEqual(record[3], 0)


if __name__ == "__main__":
    unittest.main()