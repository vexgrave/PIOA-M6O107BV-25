import sys
from .tui import DatabaseTUI

if __name__ == "__main__":
    db_type = "memory"
    if len(sys.argv) > 1:
        db_type = sys.argv[1]
    
    if db_type not in ["memory", "json", "csv"]:
        print("Ошибка: неверный тип базы данных.")
        print("Доступные варианты: memory, json, csv")
        sys.exit(1)
    
    app = DatabaseTUI(db_type)
    app.run()