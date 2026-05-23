from .errors import MissingColumnError, UnknownColumnError, InvalidAgeError, DuplicateIDError

type Record = tuple

class Table:
    def __init__(self, name: str, columns: list[str]) -> None:
        self.name = name
        self.columns = columns
        self._records: list[Record] = []
        self._indexes: dict[str, dict] = {}

    def add_record(self, record: Record) -> None:
        if len(record) != len(self.columns):
            raise MissingColumnError("Количество значений не совпадает с количеством колонок")
        self._records.append(record)

    def get_records(self) -> list[Record]:
        return self._records.copy()

    def select(
        self,
        filters: dict[str, any] | None = None,
        order_by: str | None = None,
        reverse: bool = False,
    ) -> list[Record]:
        result = self._records.copy()

        if filters:
            for column, value in filters.items():
                if column not in self.columns:
                    raise UnknownColumnError(f"Неизвестная колонка: {column}")
                index = self.columns.index(column)
                result = [r for r in result if r[index] == value]

        if order_by:
            if order_by not in self.columns:
                raise UnknownColumnError(f"Неизвестная колонка: {order_by}")
            index = self.columns.index(order_by)
            if order_by in self._indexes and not filters:
                index_data = self._indexes[order_by]
                if value in index_data:
                    result = [r for r in result if r in index_data[value]]
            else:
                result = sorted(result, key=lambda x: x[index], reverse=reverse)

        return result

    def create_index(self, column: str) -> None:
        if column not in self.columns:
            raise UnknownColumnError(f"Неизвестная колонка: {column}")
        index = self.columns.index(column)
        self._indexes[column] = {}
        for record in self._records:
            value = record[index]
            if value not in self._indexes[column]:
                self._indexes[column][value] = []
            self._indexes[column][value].append(record)

    def update_index(self, column: str, record: Record, operation: str) -> None:
        if column not in self._indexes:
            return
        index = self.columns.index(column)
        value = record[index]
        if operation == "add":
            if value not in self._indexes[column]:
                self._indexes[column][value] = []
            self._indexes[column][value].append(record)
        elif operation == "remove":
            if value in self._indexes[column]:
                if record in self._indexes[column][value]:
                    self._indexes[column][value].remove(record)
                if not self._indexes[column][value]:
                    del self._indexes[column][value]

    def clear(self) -> None:
        self._records.clear()
        for index in self._indexes:
            self._indexes[index].clear()