"""Balão de diálogo flutuante do Harmes."""

from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextBrowser, QApplication
)
from .icons import create_vector_icon


class SpeechBalloon(QWidget):
    """Balão de fala com visual dark/neon roxo posicionado sobre a criatura."""

    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 22)

        # Barra de cabeçalho
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 4)

        self.title_lbl = QLabel("HARMES")
        self.title_lbl.setStyleSheet(
            "color: #a855f7; font-size: 11px; font-weight: 700; "
            "font-family: 'Segoe UI', sans-serif; letter-spacing: 1.5px;"
        )
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()

        self.btn_copy = QPushButton()
        self.btn_copy.setIcon(create_vector_icon("copy", 18, "#d8b4fe"))
        self.btn_copy.setIconSize(QSize(16, 16))
        self.btn_copy.setFixedSize(26, 24)
        self.btn_copy.setToolTip("Copiar texto")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setStyleSheet("""
            QPushButton {
                background: rgba(168, 85, 247, 0.15);
                border: 1px solid rgba(168, 85, 247, 0.35);
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(168, 85, 247, 0.45);
            }
        """)
        self.btn_copy.clicked.connect(self.copy_content)
        header_layout.addWidget(self.btn_copy)

        self.btn_close = QPushButton()
        self.btn_close.setIcon(create_vector_icon("close", 18, "#9ca3af"))
        self.btn_close.setIconSize(QSize(14, 14))
        self.btn_close.setFixedSize(26, 24)
        self.btn_close.setToolTip("Fechar balão")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.08);
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #ef4444;
            }
        """)
        self.btn_close.clicked.connect(self.close_requested.emit)
        header_layout.addWidget(self.btn_close)
        layout.addLayout(header_layout)

        # Área de texto
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                color: #f3f4f6;
                border: none;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                font-size: 13px;
                line-height: 1.45;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,0.25);
                width: 5px;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(168, 85, 247, 0.6);
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.text_browser)

        self.setFixedSize(340, 210)

    def set_text(self, text: str):
        """Define e formata o conteúdo textual exibido no balão."""
        formatted = text.replace("\n", "<br>")
        self.text_browser.setHtml(
            f"<div style='color:#f3f4f6; font-family: Segoe UI, sans-serif;'>{formatted}</div>"
        )

    def copy_content(self):
        """Copia o conteúdo do balão para a área de transferência do sistema operacional."""
        clipboard = QApplication.clipboard()
        plain = self.text_browser.toPlainText()
        clipboard.setText(plain)
        self.btn_copy.setToolTip("Copiado com sucesso!")
        QTimer.singleShot(1500, lambda: self.btn_copy.setToolTip("Copiar texto"))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        body_rect = QRect(2, 2, rect.width() - 4, rect.height() - 18)

        path = QPainterPath()
        path.addRoundedRect(
            float(body_rect.x()), float(body_rect.y()),
            float(body_rect.width()), float(body_rect.height()),
            14.0, 14.0
        )

        # Rabicho do balão apontando para a cabeça da criatura
        tail_center = rect.width() // 2
        tail_path = QPainterPath()
        tail_path.moveTo(tail_center - 12, body_rect.bottom() - 1)
        tail_path.lineTo(tail_center, rect.height() - 2)
        tail_path.lineTo(tail_center + 12, body_rect.bottom() - 1)
        tail_path.closeSubpath()

        full_path = path.united(tail_path)

        # Gradiente escuro elegante
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor(20, 20, 28, 248))
        gradient.setColorAt(1, QColor(10, 10, 15, 252))

        painter.fillPath(full_path, QBrush(gradient))

        # Borda com brilho roxo
        pen = QPen(QColor(168, 85, 247, 190), 1.5)
        painter.setPen(pen)
        painter.drawPath(full_path)
