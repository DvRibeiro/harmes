"""Diálogo de configurações do HARMES."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)
from ..config import save_config


class SettingsDialog(QDialog):
    """Janela modal para ajuste de chaves, modelos e serviços orquestrados."""

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("HARMES - Configurações de IA e Serviços")
        self.setFixedSize(440, 380)
        self.setStyleSheet("""
            QDialog {
                background: #14141e;
                color: #e5e7eb;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #d1d5db;
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                background: #1e1e2d;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px 12px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #a855f7;
            }
            QPushButton {
                background: #7c3aed;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #9333ea;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Provedor Ativo
        layout.addWidget(QLabel("<b>Provedor Padrão:</b>"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItem("Google Gemini (Nuvem)", "gemini")
        self.provider_combo.addItem("Modo Local / Offline", "local")
        idx = 0 if self.config.get("default_provider", "gemini") == "gemini" else 1
        self.provider_combo.setCurrentIndex(idx)
        layout.addWidget(self.provider_combo)

        # Chave Gemini
        layout.addWidget(QLabel("<b>Gemini API Key:</b>"))
        self.key_input = QLineEdit(self.config.get("gemini_api_key", ""))
        self.key_input.setPlaceholderText("Cole sua chave de API do Gemini aqui...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.key_input)

        # Modelo Gemini
        layout.addWidget(QLabel("<b>Modelo Gemini:</b>"))
        self.model_input = QLineEdit(self.config.get("model", "auto"))
        self.model_input.setPlaceholderText("auto (recomendado) ou ID do modelo")
        layout.addWidget(self.model_input)

        hint = QLabel(
            "Use 'auto' para autodetectar os modelos mais rápidos e recentes. "
            "Se não preencher a chave, o Harmes usará respostas e utilitários locais."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #9ca3af; font-size: 11px;")
        layout.addWidget(hint)

        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.btn_save = QPushButton("Salvar Configurações")
        self.btn_save.clicked.connect(self.save_and_close)
        btn_box.addWidget(self.btn_save)
        layout.addLayout(btn_box)

    def save_and_close(self):
        self.config["default_provider"] = self.provider_combo.currentData()
        self.config["gemini_api_key"] = self.key_input.text().strip()
        self.config["model"] = self.model_input.text().strip() or "auto"
        save_config(self.config)
        self.accept()
