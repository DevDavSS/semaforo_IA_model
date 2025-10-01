from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileSystemModel, QTreeView, QFrame, QFileDialog, QTextEdit, QProgressBar
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QDir, Signal, QObject
import logging
import threading
from processors.processor import process_directory
from AI.ai_processor import start_ai_processor


class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.widget = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)


# ---- Clase para emitir señales desde el hilo ----
class WorkerSignals(QObject):
    log = Signal(str)
    progress = Signal(int)
    finished = Signal(bool)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Semaforizador de Observaciones")
        self.resize(1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Fuente
        font_result = QFont("Consolas", 10)

        # ---------------- HEADER ----------------
        header = QFrame()
        header_layout = QHBoxLayout(header)

        # Botones
        select_dir_btn = QPushButton("📂 Seleccionar carpeta")
        select_dir_btn.clicked.connect(self.choose_directory)
        header_layout.addWidget(select_dir_btn)

        self.btn_open_chat = QPushButton("Abrir chat con IA")
        self.btn_select_folder = QPushButton("Configuración")
        self.btn_process = QPushButton("⚡ Procesar documentos")
        self.btn_process.setEnabled(False)

        header_layout.addWidget(self.btn_open_chat)
        header_layout.addWidget(self.btn_select_folder)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_process)

        main_layout.addWidget(header)

        # ---------------- CONTENIDO ----------------
        content_layout = QHBoxLayout()

        # Resultados y logs text area
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setFont(font_result)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Explorador archivos
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.homePath())

        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree.setColumnWidth(0, 250)
        self.tree.setHeaderHidden(True)
        content_layout.addWidget(self.tree, 2)

        # Text area
        content_layout.addWidget(self.results, 5)

        main_layout.addLayout(content_layout)

        # Conexión botón procesar
        self.btn_process.clicked.connect(self.start_processing)

        self.files_to_process = None

    def choose_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Selecciona un directorio", QDir.homePath())
        if selected_dir:
            self.files_to_process = selected_dir
            self.tree.setRootIndex(self.file_model.index(selected_dir))
            self.btn_process.setEnabled(True)

    def start_processing(self):
        if not self.files_to_process:
            self.results.setText("⚠️ No hay carpeta seleccionada.")
            return

        self.results.clear()
        self.progress_bar.setValue(0)

        # Configurar logger
        self.log_handler = QTextEditLogger(self.results)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)

        self.results.append("📂 Procesando documentos...")

        # Paso 1: procesar documentos locales
        has_endend = process_directory(self.files_to_process)
        self.results.append("✅ Documentos locales procesados.")

        if has_endend:
            # Paso 2: resumir con IA en un hilo
            self.results.append("🤖 Iniciando resumen con IA...")

            self.signals = WorkerSignals()
            self.signals.log.connect(self.results.append)
            self.signals.progress.connect(self.progress_bar.setValue)

            ai_thread = threading.Thread(
                target=start_ai_processor,
                kwargs={
                    "progress_callback": self.signals.progress.emit,
                    "log_callback": self.signals.log.emit
                }
            )
            ai_thread.start()
            self.btn_process.setEnabled(False)
