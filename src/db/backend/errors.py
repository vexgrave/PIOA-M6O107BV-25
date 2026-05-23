class DatabaseError(Exception):
    pass

class InvalidAgeError(DatabaseError):
    pass

class DuplicateIDError(DatabaseError):
    pass

class RecordNotFoundError(DatabaseError):
    pass

class TableNotFoundError(DatabaseError):
    pass

class FileStorageError(DatabaseError):
    pass