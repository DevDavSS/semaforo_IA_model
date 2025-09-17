from UI.index import QApplication, MainWindow
import sys

def start_index():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())    


if __name__ == "__main__":
    start_index()