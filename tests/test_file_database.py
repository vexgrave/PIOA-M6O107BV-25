import unittest
import os
import shutil
import json
from pathlib import Path
from src.db.backend.file import JSONDatabase, CSVDatabase
from src.db.backend.errors import (
    TableNotFoundError,
    TableAlreadyExistsError,
    FileDatabaseError,
)


class TestJSONDatabase(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_data_json"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.db = JSONDatabase(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

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

    def test_list_tables_empty(self):
        tables = self.db.list_tables()
        self.assertEqual(len(tables), 0)

    def test_add_and_read_record(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.add({"name": "Anna", "age": 20})
        result = table.read()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Anna")

    def test_persistence(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.add({"name": "Anna", "age": 20})
        self.db.save()
        
        new_db = JSONDatabase(self.test_dir)
        new_table = new_db.get_table("users")
        result = new_table.read()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Anna")

    def test_update_and_delete(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        record_id = table.add({"name": "Anna", "age": 20})
        table.update(record_id, {"age": 21})
        self.db.save()
        
        new_db = JSONDatabase(self.test_dir)
        new_table = new_db.get_table("users")
        result = new_table.read({"id": record_id})
        self.assertEqual(result[0]["age"], 21)

    def test_update_record(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        record_id = table.add({"name": "Anna", "age": 20})
        table.update(record_id, {"age": 21})
        result = table.read({"id": record_id})
        self.assertEqual(result[0]["age"], 21)

    def test_delete_record(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        record_id = table.add({"name": "Anna", "age": 20})
        table.delete(record_id)
        result = table.read()
        self.assertEqual(len(result), 0)

    def test_index_creation(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.create_index("name")
        self.assertIn("name", table.indexes)

    def test_persistence_with_index(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.create_index("name")
        table.add({"name": "Anna", "age": 20})
        self.db.save()
        
        new_db = JSONDatabase(self.test_dir)
        new_table = new_db.get_table("users")
        self.assertIn("name", new_table.indexes)

    def test_sort(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.add({"name": "Bob", "age": 25})
        table.add({"name": "Anna", "age": 20})
        table.sort("age", reverse=False)
        result = table.read()
        self.assertEqual(result[0]["name"], "Anna")

    def test_json_file_creation(self):
        self.db.create_table("users", ["name", "age"])
        json_file = Path(self.test_dir) / "users.json"
        self.assertTrue(json_file.exists())

    def test_load_empty_directory(self):
        new_db = JSONDatabase(self.test_dir)
        self.assertEqual(len(new_db.list_tables()), 0)

    def test_close(self):
        self.db.create_table("users", ["name", "age"])
        self.db.close()
        json_file = Path(self.test_dir) / "users.json"
        self.assertTrue(json_file.exists())

    def test_multiple_tables_persistence(self):
        self.db.create_table("users", ["name"])
        self.db.create_table("products", ["title"])
        users = self.db.get_table("users")
        products = self.db.get_table("products")
        users.add({"name": "Anna"})
        products.add({"title": "Book"})
        self.db.save()
        
        new_db = JSONDatabase(self.test_dir)
        self.assertEqual(len(new_db.list_tables()), 2)
        self.assertEqual(len(new_db.get_table("users").read()), 1)
        self.assertEqual(len(new_db.get_table("products").read()), 1)

    def test_filter_with_index(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.create_index("name")
        table.add({"name": "Anna", "age": 20})
        table.add({"name": "Bob", "age": 25})
        self.db.save()
        
        new_db = JSONDatabase(self.test_dir)
        new_table = new_db.get_table("users")
        result = new_table.read({"name": "Anna"})
        self.assertEqual(len(result), 1)


class TestCSVDatabase(unittest.TestCase):

    def setUp(self):
        self.test_dir = "test_data_csv"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        self.db = CSVDatabase(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

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

    def test_add_and_read_record(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.add({"name": "Anna", "age": 20})
        result = table.read()
        self.assertEqual(len(result), 1)

    def test_persistence(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.add({"name": "Anna", "age": 20})
        self.db.save()
        
        new_db = CSVDatabase(self.test_dir)
        new_table = new_db.get_table("users")
        result = new_table.read()
        self.assertEqual(len(result), 1)

    def test_csv_file_creation(self):
        self.db.create_table("users", ["name", "age"])
        csv_file = Path(self.test_dir) / "users.csv"
        self.assertTrue(csv_file.exists())

    def test_metadata_file_creation(self):
        self.db.create_table("users", ["name", "age"])
        meta_file = Path(self.test_dir) / "metadata.json"
        self.assertTrue(meta_file.exists())

    def test_update_record(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        record_id = table.add({"name": "Anna", "age": 20})
        table.update(record_id, {"age": 21})
        result = table.read({"id": record_id})
        self.assertEqual(result[0]["age"], 21)

    def test_delete_record(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        record_id = table.add({"name": "Anna", "age": 20})
        table.delete(record_id)
        result = table.read()
        self.assertEqual(len(result), 0)

    def test_persistence_after_update(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        record_id = table.add({"name": "Anna", "age": 20})
        table.update(record_id, {"age": 21})
        self.db.save()
        
        new_db = CSVDatabase(self.test_dir)
        new_table = new_db.get_table("users")
        result = new_table.read({"id": record_id})
        self.assertEqual(result[0]["age"], 21)

    def test_load_empty_directory(self):
        new_db = CSVDatabase(self.test_dir)
        self.assertEqual(len(new_db.list_tables()), 0)

    def test_save(self):
        self.db.create_table("users", ["name", "age"])
        self.db.save()
        csv_file = Path(self.test_dir) / "users.csv"
        self.assertTrue(csv_file.exists())

    def test_close(self):
        self.db.create_table("users", ["name", "age"])
        self.db.close()
        csv_file = Path(self.test_dir) / "users.csv"
        self.assertTrue(csv_file.exists())

    def test_metadata_content(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.add({"name": "Anna", "age": 20})
        self.db.save()
        
        meta_file = Path(self.test_dir) / "metadata.json"
        with open(meta_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        self.assertIn("users", metadata)
        self.assertEqual(metadata["users"]["columns"], ["name", "age"])
        self.assertEqual(metadata["users"]["next_id"], 2)

    def test_csv_content(self):
        self.db.create_table("users", ["name", "age"])
        table = self.db.get_table("users")
        table.add({"name": "Anna", "age": 20})
        self.db.save()
        
        csv_file = Path(self.test_dir) / "users.csv"
        with open(csv_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertIn("id,name,age", content)
        self.assertIn("Anna", content)

    def test_multiple_tables_persistence(self):
        self.db.create_table("users", ["name"])
        self.db.create_table("products", ["title"])
        users = self.db.get_table("users")
        products = self.db.get_table("products")
        users.add({"name": "Anna"})
        products.add({"title": "Book"})
        self.db.save()
        
        new_db = CSVDatabase(self.test_dir)
        self.assertEqual(len(new_db.list_tables()), 2)

    def test_data_types_preserved(self):
        self.db.create_table("data", ["number", "text", "float_num"])
        table = self.db.get_table("data")
        table.add({"number": 42, "text": "hello", "float_num": 3.14})
        self.db.save()
        
        new_db = CSVDatabase(self.test_dir)
        new_table = new_db.get_table("data")
        result = new_table.read()
        self.assertEqual(result[0]["number"], 42)
        self.assertEqual(result[0]["text"], "hello")
        self.assertAlmostEqual(result[0]["float_num"], 3.14, places=2)


class TestFileDatabaseEdgeCases(unittest.TestCase):

    def setUp(self):
        self.test_dir_json = "test_edge_json"
        self.test_dir_csv = "test_edge_csv"

    def tearDown(self):
        if os.path.exists(self.test_dir_json):
            shutil.rmtree(self.test_dir_json)
        if os.path.exists(self.test_dir_csv):
            shutil.rmtree(self.test_dir_csv)

    def test_json_load_nonexistent_directory(self):
        db = JSONDatabase("nonexistent_dir_12345")
        self.assertEqual(len(db.list_tables()), 0)
        shutil.rmtree("nonexistent_dir_12345", ignore_errors=True)

    def test_csv_load_nonexistent_directory(self):
        db = CSVDatabase("nonexistent_dir_67890")
        self.assertEqual(len(db.list_tables()), 0)
        shutil.rmtree("nonexistent_dir_67890", ignore_errors=True)

    def test_json_load_corrupted_file(self):
        if os.path.exists(self.test_dir_json):
            shutil.rmtree(self.test_dir_json)
        os.makedirs(self.test_dir_json)
        
        corrupted_file = Path(self.test_dir_json) / "users.json"
        with open(corrupted_file, "w") as f:
            f.write("{ invalid json")
        
        with self.assertRaises(FileDatabaseError):
            JSONDatabase(self.test_dir_json)
        
        shutil.rmtree(self.test_dir_json)

    def test_csv_load_corrupted_metadata(self):
        if os.path.exists(self.test_dir_csv):
            shutil.rmtree(self.test_dir_csv)
        os.makedirs(self.test_dir_csv)
        
        meta_file = Path(self.test_dir_csv) / "metadata.json"
        with open(meta_file, "w") as f:
            f.write("{ invalid json")
        
        db = CSVDatabase(self.test_dir_csv)
        self.assertEqual(len(db.list_tables()), 0)
        
        shutil.rmtree(self.test_dir_csv)


if __name__ == "__main__":
    unittest.main()