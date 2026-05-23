class DatabaseError(Exception):
    pass


class TableNotFoundError(DatabaseError):
    pass


class TableAlreadyExistsError(DatabaseError):
    pass


class FieldNotFoundError(DatabaseError):
    pass


class RecordNotFoundError(DatabaseError):
    pass


class MissingFieldError(DatabaseError):
    pass


class FileDatabaseError(DatabaseError):
    pass


class IndexNotFoundError(DatabaseError):
    pass