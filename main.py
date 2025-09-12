import sys  # Importa el módulo sys para manejar la ejecución de la app y salir correctamente
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QFileDialog, QTextEdit, QHBoxLayout, QFrame
)  # Importa los widgets principales de PySide6 para la interfaz
from PySide6.QtGui import QFont, QPalette, QColor  # Para cambiar fuentes y colores
from PySide6.QtCore import Qt  # Constantes de alineación y comportamiento
from processors.processor import process_directory
import logging


class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.widget = text_edit

    def emit(self, record):
        msg = self.format(record)  # Aplica formato al mensaje de log
        self.widget.append(msg)  



# Definimos la ventana principal de la aplicación
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()  # Llama al constructor de QWidget
        self.setWindowTitle("📝 Procesador de Observaciones Fiscales")  # Título de la ventana
        self.setGeometry(200, 200, 800, 600)  # Posición (x,y) y tamaño (ancho, alto)


        # Aplicamos estilos globales usando CSS
        self.setStyleSheet("""
            QWidget {
                background-color: #000;  /* Fondo negro general */
            }
            QLabel {
                color: #fff;  /* Texto blanco */
            }
            QPushButton {
                background-color: #4CAF50;  /* Verde */
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                background-color: rgba(9, 13, 23, 0.2);  /* Fondo tipo terminal transparente */
                color: #00FF00;  /* Color texto verde terminal */
                border: 1px solid rgba(255, 255, 255, 0.2);  /* Borde muy sutil */
                border-radius: 8px;
                padding: 8px;
                font-family: "Courier New", monospace;  /* Fuente monoespaciada */
                font-size: 14px;
            }
        """)


        # Fuente para etiquetas y botones
        font_label = QFont("Arial", 12, QFont.Bold)
        font_result = QFont("Consolas", 10)  # Fuente monoespaciada para resultados

        # Etiqueta principal en la parte superior
        self.label = QLabel("Selecciona archivos o carpeta con documentos .docx")
        self.label.setFont(font_label)  # Asignamos la fuente
        self.label.setAlignment(Qt.AlignCenter)  # Centrar texto

        # Botones de acción
        self.btn_open_chat = QPushButton("Abrir chat con IA")
        self.btn_select_folder = QPushButton("📂 Seleccionar carpeta")
        self.btn_process = QPushButton("⚡ Procesar documentos")
        self.btn_process.setEnabled(False)  # Inicialmente deshabilitado hasta seleccionar archivos

        # Conectar eventos de botones con métodos
        self.btn_open_chat.clicked.connect(self.open_chat) #boton para abrir chat directo con la IA
        self.btn_select_folder.clicked.connect(self.select_folder) #llamada al metodo select files para la carga de archivos alojados en un directorio
        self.btn_process.clicked.connect(self.process_documents) #llamada a la funcion para iniciar con el procesamiento de archivos

        # Área de texto para mostrar resultados de procesamiento
        self.results = QTextEdit()
        self.results.setReadOnly(True)  # Solo lectura, no editable por el usuario
        self.results.setFont(font_result)  # Fuente monoespaciada

        # Separador horizontal para dividir botones y resultados
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)  # Línea horizontal
        separator.setFrameShadow(QFrame.Sunken)  # Efecto “hundido”
        separator.setLineWidth(1)  # Grosor de la línea

        # Layout horizontal para los botones
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.btn_open_chat)
        layout_buttons.addWidget(self.btn_select_folder)
        layout_buttons.addWidget(self.btn_process)

        # Layout principal vertical
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.label)  # Etiqueta superior
        layout_main.addLayout(layout_buttons)  # Botones
        layout_main.addWidget(separator)  # Separador
        layout_main.addWidget(self.results)  # Área de resultados
        self.setLayout(layout_main)  # Aplicamos layout a la ventana

        # Lista donde guardaremos los archivos seleccionados
        self.files_to_process = []

    # Método para seleccionar archivos individuales
    def open_chat(self):
        pass

    # Método para seleccionar una carpeta completa
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder:
            self.files_to_process = folder  # Guardamos la ruta del directorio, NO la lista de archivos
            import os
            num_files = len([f for f in os.listdir(folder) if f.lower().endswith(".docx")])
            self.label.setText(f"📂 {num_files} archivos encontrados")
            self.btn_process.setEnabled(True)

    def process_documents(self):
        self.results.clear()  # Limpiar resultados anteriores
        # Configurar logger para enviar mensajes a QTextEdit
        self.log_handler = QTextEditLogger(self.results)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        if not self.files_to_process:  # Validación
            self.results.setText("No hay carpeta seleccionada.")
            return
        print(self.files_to_process)
        has_endend = process_directory(self.files_to_process) #variable que recibe un booleano para saber si el procesado ha acabado

        self.results.append("✅ Todos los documentos procesados.")


# Código principal para ejecutar la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Crear aplicación
    window = MainWindow()  # Crear ventana principal
    window.show()  # Mostrar ventana
    sys.exit(app.exec())  # Ejecutar bucle principal de la app
