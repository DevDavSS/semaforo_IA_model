import sys
from PySide6.QtWidgets import QApplication
from UI.index import MainWindow

def start_index():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    start_index()
