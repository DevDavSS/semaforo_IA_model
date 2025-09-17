from UI.index import QApplication, MainWindow
from UI.ai_summarizing_ui import process_alert
from AI.ai_processor import start_ai_processor


import sys

def start_index():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())    

def ai_summarizing_ui():
    terminated = start_ai_processor()
    if terminated:
        process_alert()
    else:
        print("error")



if __name__ == "__main__":
    start_index()