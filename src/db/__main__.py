from .backend.memory import StudentTable
from .tui import TUI

def main():
    table = StudentTable()
    tui = TUI(table)
    tui.run()

if __name__ == "__main__":
    main()