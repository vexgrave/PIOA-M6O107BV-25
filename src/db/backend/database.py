from abc import ABC, abstractmethod
from .table import Table

class Database(ABC):
    @abstractmethod
    def create_table(self, name: str, columns: list[str]) -> Table:
        pass

    @abstractmethod
    def get_table(self, name: str) -> Table | None:
        pass

    @abstractmethod
    def insert_record(self, table_name: str, record: tuple) -> None:
        pass

    @abstractmethod
    def select_records(
        self,
        table_name: str,
        filters: dict[str, any] | None = None,
        order_by: str | None = None,
        reverse: bool = False,
    ) -> list[tuple]:
        pass

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def load(self) -> None:
        pass