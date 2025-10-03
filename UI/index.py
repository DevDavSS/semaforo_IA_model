from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileSystemModel, QTreeView, QFrame, QFileDialog, QTextEdit, QProgressBar
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QDir, Signal, QObject, QProcess
import logging
import threading
import configparser
import os
from processors.processor import process_directory
from AI.ai_processor import start_ai_processor, ai_processor  # Import ai_processor for kill_ollama
from .configuration_ui import ConfigWindow
import subprocess
import platform

class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self.widget = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

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
        self.btn_configuration = QPushButton("Configuración")
        self.btn_process = QPushButton("⚡ Procesar documentos")
        self.btn_cancel = QPushButton("Cancelar Proceso")
        self.btn_process.setEnabled(False)
        self.btn_cancel.setEnabled(False)

        header_layout.addWidget(self.btn_cancel)
        header_layout.addWidget(self.btn_open_chat)
        header_layout.addWidget(self.btn_configuration)
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

        # Conexión botones
        self.btn_process.clicked.connect(self.start_processing)
        self.btn_configuration.clicked.connect(self.open_configuration)
        self.btn_open_chat.clicked.connect(self.open_ollama)
        self.btn_cancel.clicked.connect(self.cancel_processing)  # Connect cancel button

        self.files_to_process = None
        self.ai_thread = None  # Track the AI thread

    def choose_directory(self):
        selected_dir = QFileDialog.getExistingDirectory(self, "Selecciona un directorio", QDir.homePath())
        if selected_dir:
            self.files_to_process = selected_dir
            self.tree.setRootIndex(self.file_model.index(selected_dir))
            self.btn_process.setEnabled(True)

    def open_configuration(self):
        self.config_window = ConfigWindow()
        self.config_window.show()

    def open_ollama(self):
        try:
            self.ollama_process = QProcess(self)
            system = platform.system()
            if system == "Windows":
                self.ollama_process.start("ollama app.exe")
            elif system == "Darwin":
                self.ollama_process.start("open", ["-a", "Ollama"])
            else:
                self.ollama_process.start("ollama-gui")
            self.btn_open_chat.setEnabled(False)
            self.ollama_process.finished.connect(self.on_ollama_closed)
        except Exception as e:
            self.results.append(f"Error al abrir GUI de Ollama: {e}")

    def on_ollama_closed(self):
        self.btn_open_chat.setEnabled(True)
        self.ollama_process = None

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

        self.results.append(" Procesando documentos...")

        # Enable cancel button
        self.btn_cancel.setEnabled(True)

        # Paso 1: procesar documentos locales
        has_ended = process_directory(self.files_to_process)
        self.results.append(" Documentos locales procesados.")

        if has_ended:
            # Paso 2: resumir con IA en un hilo
            self.results.append(" Iniciando resumen con IA...")

            self.signals = WorkerSignals()
            self.signals.log.connect(self.results.append)
            self.signals.progress.connect(self.progress_bar.setValue)
            self.signals.finished.connect(self.on_ai_finished)

            # Bloqueamos botones mientras la IA corre
            self.btn_process.setEnabled(False)
            self.btn_configuration.setEnabled(False)
            self.btn_open_chat.setEnabled(False)

            # Ejecutamos la IA en un hilo
            self.ai_thread = threading.Thread(
                target=self.run_ai_thread,
                daemon=True
            )
            self.ai_thread.start()

    def run_ai_thread(self):
        """Ejecuta la IA en un hilo y emite la señal cuando termina"""
        success = start_ai_processor(
            progress_callback=self.signals.progress.emit,
            log_callback=self.signals.log.emit
        )
        # Emitimos señal de finalización
        self.signals.finished.emit(success)

    def on_ai_finished(self, success: bool):
        """Se llama cuando termina la IA o hay error"""
        self.btn_process.setEnabled(True)
        self.btn_configuration.setEnabled(True)
        self.btn_open_chat.setEnabled(True)
        self.btn_cancel.setEnabled(False)  # Disable cancel button
        self.ai_thread = None  # Clear thread reference

        if success:
            self.results.append("Procesamiento con IA finalizado correctamente.")
        else:
            self.results.append("Hubo un error en el procesamiento con IA.")

    def cancel_processing(self):
        """Termina el proceso de Ollama y actualiza la UI"""
        try:
            # Call kill_ollama from ai_processor
            processor = ai_processor()
            processor.kill_ollama()
            self.results.append("Proceso de Ollama cancelado.")
            
            # Reset UI state
            self.btn_process.setEnabled(True)
            self.btn_configuration.setEnabled(True)
            self.btn_open_chat.setEnabled(True)
            self.btn_cancel.setEnabled(False)
            self.progress_bar.setValue(0)
            self.ai_thread = None  # Clear thread reference

            # Remove logger handler to avoid memory leaks
            if hasattr(self, 'log_handler'):
                logging.getLogger().removeHandler(self.log_handler)
                self.log_handler = None

        except Exception as e:
            self.results.append(f" Error al cancelar el proceso: {e}")