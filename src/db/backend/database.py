from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def create_table(self, name, columns):
        pass

    @abstractmethod
    def get_table(self, name):
        pass

    @abstractmethod
    def list_tables(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass