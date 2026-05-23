import unittest
from src.db.backend.memory import InMemoryDB
from src.db.backend.table import Table
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    FieldNotFoundError,
    MissingFieldError,
)


class TestTable(unittest.TestCase):

    def setUp(self):
        self.table = Table("users", ["name", "age"])

    def test_add_record(self):
        record_id = self.table.add({"name": "Anna", "age": 20})
        self.assertEqual(record_id, 1)
        self.assertEqual(len(self.table.rows), 1)

    def test_add_missing_field(self):
        with self.assertRaises(MissingFieldError):
            self.table.add({"name": "Bob"})

    def test_read_all(self):
        self.table.add({"name": "Anna", "age": 20})
        self.table.add({"name": "Bob", "age": 25})
        result = self.table.read()
        self.assertEqual(len(result), 2)

    def test_read_with_filter(self):
        self.table.add({"name": "Anna", "age": 20})
        self.table.add({"name": "Bob", "age": 25})
        result = self.table.read({"age": "20"})
        self.assertEqual(len(result), 1)

    def test_read_invalid_field(self):
        with self.assertRaises(FieldNotFoundError):
            self.table.read({"invalid_field": "value"})

    def test_read_empty_table(self):
        result = self.table.read()
        self.assertEqual(len(result), 0)

    def test_read_no_matches(self):
        self.table.add({"name": "Anna", "age": 20})
        result = self.table.read({"name": "NonExistent"})
        self.assertEqual(len(result), 0)

    def test_update_existing(self):
        record_id = self.table.add({"name": "Anna", "age": 20})
        self.table.update(record_id, {"age": 21})
        updated = self.table.read({"id": record_id})
        self.assertEqual(updated[0]["age"], 21)

    def test_update_nonexistent(self):
        result = self.table.update(999, {"name": "Test"})
        self.assertFalse(result)

    def test_delete_existing(self):
        record_id = self.table.add({"name": "Anna", "age": 20})
        result = self.table.delete(record_id)
        self.assertTrue(result)
        self.assertEqual(len(self.table.rows), 0)

    def test_delete_nonexistent(self):
        result = self.table.delete(999)
        self.assertFalse(result)

    def test_sort_ascending(self):
        self.table.add({"name": "Bob", "age": 25})
        self.table.add({"name": "Anna", "age": 20})
        self.table.add({"name": "Charlie", "age": 30})
        sorted_rows = self.table.sort("age", reverse=False)
        self.assertEqual(sorted_rows[0]["name"], "Anna")
        self.assertEqual(sorted_rows[1]["name"], "Bob")
        self.assertEqual(sorted_rows[2]["name"], "Charlie")

    def test_sort_descending(self):
        self.table.add({"name": "Bob", "age": 25})
        self.table.add({"name": "Anna", "age": 20})
        self.table.add({"name": "Charlie", "age": 30})
        sorted_rows = self.table.sort("age", reverse=True)
        self.assertEqual(sorted_rows[0]["name"], "Charlie")
        self.assertEqual(sorted_rows[1]["name"], "Bob")
        self.assertEqual(sorted_rows[2]["name"], "Anna")

    def test_sort_invalid_field(self):
        with self.assertRaises(FieldNotFoundError):
            self.table.sort("invalid_field")

    def test_sort_by_id(self):
        self.table.add({"name": "Bob", "age": 25})
        self.table.add({"name": "Anna", "age": 20})
        sorted_rows = self.table.sort("id", reverse=False)
        self.assertEqual(sorted_rows[0]["name"], "Bob")

    def test_create_index(self):
        self.table.create_index("name")
        self.assertIn("name", self.table.indexes)

    def test_create_index_invalid_field(self):
        with self.assertRaises(FieldNotFoundError):
            self.table.create_index("invalid_field")

    def test_drop_index(self):
        self.table.create_index("name")
        self.assertIn("name", self.table.indexes)
        self.table.drop_index("name")
        self.assertNotIn("name", self.table.indexes)

    def test_drop_nonexistent_index(self):
        self.table.drop_index("nonexistent")
        self.assertNotIn("nonexistent", self.table.indexes)

    def test_read_with_index(self):
        self.table.create_index("name")
        self.table.add({"name": "Anna", "age": 20})
        self.table.add({"name": "Bob", "age": 25})
        result = self.table.read({"name": "Anna"})
        self.assertEqual(len(result), 1)

    def test_index_update_on_add(self):
        self.table.create_index("name")
        self.table.add({"name": "Anna", "age": 20})
        self.assertIn("Anna", self.table.indexes["name"])

    def test_index_update_on_delete(self):
        self.table.create_index("name")
        record_id = self.table.add({"name": "Anna", "age": 20})
        self.table.delete(record_id)
        self.assertNotIn("Anna", self.table.indexes["name"])

    def test_index_update_on_update(self):
        self.table.create_index("name")
        record_id = self.table.add({"name": "Anna", "age": 20})
        self.table.update(record_id, {"name": "Bob"})
        self.assertNotIn("Anna", self.table.indexes["name"])
        self.assertIn("Bob", self.table.indexes["name"])

    def test_to_dict(self):
        self.table.add({"name": "Anna", "age": 20})
        data = self.table.to_dict()
        self.assertEqual(data["name"], "users")
        self.assertEqual(data["columns"], ["name", "age"])
        self.assertEqual(len(data["rows"]), 1)
        self.assertEqual(data["next_id"], 2)

    def test_from_dict(self):
        data = {
            "name": "students",
            "columns": ["name", "grade"],
            "rows": [{"id": 1, "name": "Anna", "grade": 5}],
            "next_id": 2,
            "indexes": {}
        }
        table = Table.from_dict(data)
        self.assertEqual(table.name, "students")
        self.assertEqual(table.columns, ["name", "grade"])
        self.assertEqual(len(table.rows), 1)

    def test_multiple_filters(self):
        self.table.add({"name": "Anna", "age": 20})
        self.table.add({"name": "Anna", "age": 25})
        self.table.add({"name": "Bob", "age": 20})
        result = self.table.read({"name": "Anna", "age": "20"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Anna")


class TestInMemoryDB(unittest.TestCase):

    def setUp(self):
        self.db = InMemoryDB()

    def test_create_table(self):
        self.db.create_table("users", ["name", "age"])
        self.assertIn("users", self.db.list_tables())

    def test_create_duplicate_table(self):
        self.db.create_table("users", ["name", "age"])
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("users", ["name", "age"])

    def test_get_table(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        self.assertEqual(table.name, "users")

    def test_get_nonexistent_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.get_table("users")

    def test_list_tables(self):
        self.db.create_table("users", ["name", "age"])
        self.db.create_table("products", ["title", "price"])
        tables = self.db.list_tables()
        self.assertEqual(len(tables), 2)
        self.assertIn("users", tables)
        self.assertIn("products", tables)

    def test_list_tables_empty(self):
        tables = self.db.list_tables()
        self.assertEqual(len(tables), 0)

    def test_full_crud(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        id1 = table.add({"name": "Anna", "age": 20})
        id2 = table.add({"name": "Bob", "age": 25})
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)
        all_records = table.read()
        self.assertEqual(len(all_records), 2)
        filtered = table.read({"age": "20"})
        self.assertEqual(len(filtered), 1)
        table.update(id1, {"age": 21})
        updated = table.read({"id": id1})
        self.assertEqual(updated[0]["age"], 21)
        table.delete(id2)
        self.assertEqual(len(table.read()), 1)

    def test_save_and_load_noop(self):
        self.db.create_table("users", ["name", "age"])
        self.db.save()
        self.db.load()
        self.assertIn("users", self.db.list_tables())


if __name__ == "__main__":
    unittest.main()