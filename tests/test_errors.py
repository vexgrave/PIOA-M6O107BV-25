import unittest
from src.db.backend.errors import (
    DatabaseError,
    TableNotFoundError,
    TableAlreadyExistsError,
    FieldNotFoundError,
    RecordNotFoundError,
    MissingFieldError,
    FileDatabaseError,
    IndexNotFoundError,
)


class TestErrors(unittest.TestCase):
    
    def test_database_error(self):
        with self.assertRaises(DatabaseError):
            raise DatabaseError("Base error")

    def test_table_not_found_error(self):
        with self.assertRaises(TableNotFoundError):
            raise TableNotFoundError("Table not found")

    def test_table_already_exists_error(self):
        with self.assertRaises(TableAlreadyExistsError):
            raise TableAlreadyExistsError("Table exists")

    def test_field_not_found_error(self):
        with self.assertRaises(FieldNotFoundError):
            raise FieldNotFoundError("Field not found")

    def test_record_not_found_error(self):
        with self.assertRaises(RecordNotFoundError):
            raise RecordNotFoundError("Record not found")

    def test_missing_field_error(self):
        with self.assertRaises(MissingFieldError):
            raise MissingFieldError("Missing field")

    def test_file_database_error(self):
        with self.assertRaises(FileDatabaseError):
            raise FileDatabaseError("File error")

    def test_index_not_found_error(self):
        with self.assertRaises(IndexNotFoundError):
            raise IndexNotFoundError("Index not found")

    def test_errors_inheritance(self):
        self.assertTrue(issubclass(TableNotFoundError, DatabaseError))
        self.assertTrue(issubclass(TableAlreadyExistsError, DatabaseError))
        self.assertTrue(issubclass(FieldNotFoundError, DatabaseError))
        self.assertTrue(issubclass(FileDatabaseError, DatabaseError))


if __name__ == "__main__":
    unittest.main()