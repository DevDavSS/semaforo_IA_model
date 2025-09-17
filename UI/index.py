from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QFileSystemModel, QTreeView, QFrame,
    QFileDialog, QTextEdit
)
from PySide6.QtGui import QFont, QPalette, QColor  # Para cambiar fuentes y colores
from PySide6.QtCore import QDir
import logging
from processors.processor import process_directory


class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.widget = text_edit

    def emit(self, record):
        msg = self.format(record)  # Aplica formato al mensaje de log
        self.widget.append(msg)  


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard estilo VS Code")
        self.resize(1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

       # Fuente para etiquetas y botones
        font_label = QFont("Arial", 12, QFont.Bold)
        font_result = QFont("Consolas", 10)  # Fuente monoespaciada para resultados

        # ---------------- HEADER ----------------
        header = QFrame()
        header_layout = QHBoxLayout(header)


        # Botón para seleccionar directorio
        select_dir_btn = QPushButton("📂 Seleccionar carpeta")
        select_dir_btn.clicked.connect(self.choose_directory)
        header_layout.addWidget(select_dir_btn)

        #botones
        self.btn_open_chat = QPushButton("Abrir chat con IA")
        self.btn_select_folder = QPushButton("Configuracion")
        self.btn_process = QPushButton("⚡ Procesar documentos")
        self.btn_process.setEnabled(False)  # Inicialmente deshabilitado hasta seleccionar archivos
        # Botones de ejemplo

        header_layout.addWidget(self.btn_open_chat)
        header_layout.addWidget(self.btn_select_folder)
        header_layout.addStretch()
        main_layout.addWidget(header)
        header_layout.addWidget(self.btn_process)
        #Conexiones con los eventos correspondientes a cada boton:

        #self.btn_open_chat.clicked.connect(self.btn_open_chat) #boton para abrir chat directo con la IA
        self.btn_process.clicked.connect(self.process_documents) #llamada a la funcion para iniciar con el procesamiento de archivos
        # ---------------- CONTENIDO ----------------
        content_layout = QHBoxLayout()
        # Área de texto para mostrar resultados de procesamiento
        self.results = QTextEdit()
        self.results.setReadOnly(True)  # Solo lectura, no editable por el usuario
        self.results.setFont(font_result)  # Fuente monoespaciada

        # Panel lateral izquierdo (explorador de archivos)
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.homePath())  # Inicialmente vacío o home

        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree.setColumnWidth(0, 250)
        self.tree.setHeaderHidden(True)
        content_layout.addWidget(self.tree, 2)

        # Área principal vacía
        content_layout.addWidget(self.results, 5)

        main_layout.addLayout(content_layout)
    def choose_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Selecciona un directorio", QDir.homePath())
        if selected_dir:
            self.files_to_process = selected_dir  # Guardamos la ruta del directorio, NO la lista de archivos
            import os
            self.tree.setRootIndex(self.file_model.index(selected_dir))
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


