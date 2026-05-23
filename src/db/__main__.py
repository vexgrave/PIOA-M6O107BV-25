import sys
from .tui import DatabaseTUI

if __name__ == "__main__":
    storage = "memory"
    if len(sys.argv) > 1:
        if sys.argv[1] in ("file", "memory"):
            storage = sys.argv[1]
    app = DatabaseTUI(storage_type=storage)
    app.run()