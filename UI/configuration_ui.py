import os
import configparser
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFrame, QMessageBox, QTextEdit
)
from PySide6.QtGui import QFont



CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.conf")

# Valores por defecto
DEFAULTS = {
    "model": "deepseek-r1:8b",
    "ai_generative_prompt": "El texto anteriormente proveído, es una observación fiscal hacia una entidad fiscalizada, necesito que hagas un resumen breve pero detallado de la situación y el problema que se está identificando en la observación, no debe ser largo el resumen, pero si conciso y los más detallado posible en montos, contrataciones, servicios, etc. Todo hazlo en un párrafo,  esta es la siguiente observación:"
}


class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración del programa")
        self.resize(600, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        font_inputs = QFont("Consolas", 10)

        # ----------- HEADER -------------
        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.addStretch()
        main_layout.addWidget(header)

        # ----------- FORM ---------------
        form_layout = QVBoxLayout()

        # Campo modelo (una línea)
        self.model_input = QLineEdit()
        self.model_input.setFont(font_inputs)
        form_layout.addWidget(QLabel("Modelo LLM:"))
        form_layout.addWidget(self.model_input)

        # Campo prompt (multi-línea)
        self.prompt_input = QTextEdit()
        self.prompt_input.setFont(font_inputs)
        self.prompt_input.setFixedHeight(200)  # tamaño 
        form_layout.addWidget(QLabel("Instrucción (Editar en caso de que se necesite modificar):"))
        form_layout.addWidget(self.prompt_input)

        main_layout.addLayout(form_layout)

        # ----------- BOTONES ------------
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)

        self.btn_save = QPushButton("Guardar")
        self.btn_default = QPushButton("Default")
        self.btn_cancel = QPushButton("Cancelar")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_default)
        btn_layout.addWidget(self.btn_cancel)

        main_layout.addWidget(btn_frame)

        # Cargar configuración actual
        self.load_config()

        # Conectar botones
        self.btn_save.clicked.connect(self.save_config)
        self.btn_default.clicked.connect(self.restore_defaults)
        self.btn_cancel.clicked.connect(self.close)

    def load_config(self):
        """Leer el archivo .conf"""
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE):
            config.read(CONFIG_FILE, encoding="utf-8")
            if "settings" in config:
                self.model_input.setText(config["settings"].get("model", DEFAULTS["model"]))
                self.prompt_input.setText(config["settings"].get("ai_generative_prompt", DEFAULTS["ai_generative_prompt"]))
        else:
            # Si no existe el archivo, cargamos defaults
            self.restore_defaults()

    def save_config(self):
        """Guardar cambios en el archivo .conf"""
        config = configparser.ConfigParser()
        config["settings"] = {
            "model": self.model_input.text(),
            "ai_generative_prompt": self.prompt_input.toPlainText()
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as configfile:
            config.write(configfile)

        QMessageBox.information(self, "Guardado", "La configuración se guardó correctamente.")

    def restore_defaults(self):
        """Restaurar configuración por defecto"""
        self.model_input.setText(DEFAULTS["model"])
        self.prompt_input.setText(DEFAULTS["ai_generative_prompt"])
        QMessageBox.information(self, "Defaults", "Se restauraron los valores por defecto.")