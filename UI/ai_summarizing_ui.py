import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget


def process_alert():
    app = QApplication(sys.argv)
    window = QWidget()

    # Crear mensaje tipo alerta
    msg = QMessageBox(window)
    msg.setWindowTitle("Proceso terminado")
    msg.setText("Se han semaforizado con éxito los documentos")
    msg.setIcon(QMessageBox.Information)
    msg.addButton("Aceptar", QMessageBox.AcceptRole)

    # Mostrar
    msg.exec()
    sys.exit(0)
