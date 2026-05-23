import sys
from .tui import TUI

def main():
    db_type = "memory"
    data_dir = "data"
    if len(sys.argv) > 1:
        db_type = sys.argv[1]
    if len(sys.argv) > 2:
        data_dir = sys.argv[2]
    tui = TUI(db_type, data_dir)
    tui.run()

if __name__ == "__main__":
    main()