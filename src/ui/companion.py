"""Componente visual principal do assistente HARMES (Companion flutuante)."""

import math
import threading
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QSize, pyqtSignal, QObject
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QIcon, QBrush, QLinearGradient, QAction
)
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QSystemTrayIcon, QMenu, QApplication
)

from ..config import ASSETS_DIR, load_config
from ..core.orchestrator import AIOrchestrator
from .icons import create_vector_icon
from .balloon import SpeechBalloon
from .settings_dialog import SettingsDialog


class WorkerSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


def process_query_in_thread(orchestrator: AIOrchestrator, query: str, signals: WorkerSignals):
    """Executa o processamento da query no orquestrador de forma assíncrona."""
    try:
        reply = orchestrator.process(query)
        signals.finished.emit(reply)
    except Exception as e:
        signals.error.emit(str(e))


class CreatureCompanion(QWidget):
    """Janela principal translúcida com a criatura animada e barra de comando."""

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.orchestrator = AIOrchestrator(self.config)

        self.signals = WorkerSignals()
        self.signals.finished.connect(self.on_processing_finished)
        self.signals.error.connect(self.on_processing_error)

        self.drag_position = QPoint()
        self.is_dragging = False

        # Carregar frames dos sprites
        self.frames = []
        for i in range(8):
            fpath = ASSETS_DIR / f"frame_{i}.png"
            if fpath.exists():
                self.frames.append(QPixmap(str(fpath)))
            else:
                print(f"[Harmes] Aviso: frame não encontrado: {fpath}")

        # Estados: idle, running_away, processing, running_back
        self.state = "idle"
        self.current_frame_idx = 7
        self.scale_factor = 1.0
        self.alpha_factor = 1.0
        self.pending_query = ""
        self.pending_result = ""

        # Timers
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation_step)
        self.anim_step = 0

        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.update_idle_pulse)
        self.idle_phase = 0.0
        self.idle_timer.start(45)

        # Configurações de janela transparente e flutuante
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self.init_ui()
        self.setup_tray_icon()
        self.center_on_screen()

    def setup_tray_icon(self):
        """Configura o ícone na bandeja do sistema."""
        self.tray = QSystemTrayIcon(self)
        if self.frames and len(self.frames) > 7:
            self.tray.setIcon(QIcon(self.frames[7]))

        tray_menu = QMenu()
        show_action = QAction("Mostrar HARMES", self)
        show_action.triggered.connect(self.show_and_raise)
        tray_menu.addAction(show_action)

        settings_action = QAction("Configurações", self)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)

        tray_menu.addSeparator()

        quit_action = QAction("Sair", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_and_raise()

    def show_and_raise(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def init_ui(self):
        self.setFixedSize(480, 620)

        # Controles superiores (Fechar, Minimizar, Configurações)
        self.top_controls = QWidget(self)
        self.top_controls.setGeometry(self.width() - 110, 10, 100, 32)
        top_layout = QHBoxLayout(self.top_controls)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)

        btn_style = """
            QPushButton {
                background: rgba(18, 18, 28, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
            }
            QPushButton:hover {
                background: rgba(168, 85, 247, 0.85);
                border: 1px solid #c084fc;
            }
        """

        self.btn_settings = QPushButton(self.top_controls)
        self.btn_settings.setIcon(create_vector_icon("settings", 20, "#9ca3af"))
        self.btn_settings.setIconSize(QSize(14, 14))
        self.btn_settings.setFixedSize(24, 24)
        self.btn_settings.setToolTip("Configurações (IA / Provedores)")
        self.btn_settings.setStyleSheet(btn_style)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.open_settings)
        top_layout.addWidget(self.btn_settings)

        self.btn_min = QPushButton(self.top_controls)
        self.btn_min.setIcon(create_vector_icon("minimize", 20, "#9ca3af"))
        self.btn_min.setIconSize(QSize(14, 14))
        self.btn_min.setFixedSize(24, 24)
        self.btn_min.setToolTip("Minimizar")
        self.btn_min.setStyleSheet(btn_style)
        self.btn_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_min.clicked.connect(self.showMinimized)
        top_layout.addWidget(self.btn_min)

        self.btn_close = QPushButton(self.top_controls)
        self.btn_close.setIcon(create_vector_icon("close", 20, "#9ca3af"))
        self.btn_close.setIconSize(QSize(14, 14))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setToolTip("Fechar")
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: rgba(18, 18, 28, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
            }
            QPushButton:hover {
                background: #ef4444;
                border: 1px solid #f87171;
            }
        """)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(QApplication.instance().quit)
        top_layout.addWidget(self.btn_close)

        # Balão de fala
        self.balloon = SpeechBalloon(self)
        self.balloon.setGeometry((self.width() - 340) // 2, 20, 340, 210)
        self.balloon.close_requested.connect(self.hide_balloon)
        self.balloon.hide()

        # Barra de Chat inferior
        self.chat_container = QWidget(self)
        self.chat_container.setGeometry(30, self.height() - 75, self.width() - 60, 52)
        self.chat_container.setStyleSheet("""
            QWidget#chat_container {
                background: rgba(18, 18, 28, 0.94);
                border: 1.5px solid rgba(168, 85, 247, 0.45);
                border-radius: 26px;
            }
        """)
        self.chat_container.setObjectName("chat_container")

        chat_layout = QHBoxLayout(self.chat_container)
        chat_layout.setContentsMargins(18, 6, 8, 6)

        self.input_field = QLineEdit(self.chat_container)
        self.input_field.setPlaceholderText("Comande o HARMES...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #f3f4f6;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit::placeholder {
                color: #6b7280;
            }
        """)
        self.input_field.returnPressed.connect(self.send_request)
        chat_layout.addWidget(self.input_field)

        self.btn_send = QPushButton(self.chat_container)
        self.btn_send.setIcon(create_vector_icon("send", 20, "#ffffff"))
        self.btn_send.setIconSize(QSize(18, 18))
        self.btn_send.setFixedSize(36, 36)
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9333ea, stop:1 #7c3aed);
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a855f7, stop:1 #9333ea);
            }
            QPushButton:disabled {
                background: #374151;
            }
        """)
        self.btn_send.clicked.connect(self.send_request)
        chat_layout.addWidget(self.btn_send)

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False

    def hide_balloon(self):
        self.balloon.hide()

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec():
            self.orchestrator.update_config(self.config)

    def send_request(self):
        text = self.input_field.text().strip()
        if not text:
            return
        if self.state != "idle":
            return

        self.hide_balloon()
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.btn_send.setEnabled(False)

        # Oculta elementos para transição limpa
        self.chat_container.hide()
        self.top_controls.hide()

        self.start_running_away(text)

    def start_running_away(self, query: str):
        self.state = "running_away"
        self.anim_step = 0
        self.pending_query = query
        self.anim_timer.start(110)

    def start_running_back(self):
        self.state = "running_back"
        self.anim_step = 0
        self.anim_timer.start(120)

    def update_animation_step(self):
        if self.state == "running_away":
            sequence = [7, 3, 0, 1, 2]
            if self.anim_step < len(sequence):
                self.current_frame_idx = sequence[self.anim_step]
                self.scale_factor = 1.0 - (self.anim_step * 0.12)
                self.alpha_factor = 1.0
                self.anim_step += 1
                self.update()
            elif self.anim_step == len(sequence):
                # Criatura desaparece nas profundezas
                self.scale_factor = 0.3
                self.alpha_factor = 0.0
                self.state = "processing"
                self.anim_timer.stop()
                self.update()

                # Processa através do orquestrador em segundo plano
                threading.Thread(
                    target=process_query_in_thread,
                    args=(self.orchestrator, self.pending_query, self.signals),
                    daemon=True
                ).start()

        elif self.state == "running_back":
            sequence = [4, 5, 6, 7]
            if self.anim_step < len(sequence):
                self.current_frame_idx = sequence[self.anim_step]
                self.scale_factor = 0.5 + (self.anim_step * 0.17)
                self.alpha_factor = 1.0
                self.anim_step += 1
                self.update()
            else:
                self.anim_timer.stop()
                self.state = "idle"
                self.current_frame_idx = 7
                self.scale_factor = 1.0
                self.alpha_factor = 1.0

                self.input_field.setEnabled(True)
                self.btn_send.setEnabled(True)
                self.top_controls.show()
                self.chat_container.show()
                self.update()

                report_file = getattr(self.orchestrator, "last_report_path", None)
                self.balloon.set_text(self.pending_result, report_path=report_file)
                self.balloon.show()
                self.balloon.raise_()

    def on_processing_error(self, message: str):
        self.on_processing_finished(f"<b>Erro no processamento:</b><br><br>{message}")

    def on_processing_finished(self, result_text: str):
        self.pending_result = result_text
        self.start_running_back()

    def update_idle_pulse(self):
        if self.state == "idle":
            self.idle_phase += 0.07
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if self.state == "processing" or self.alpha_factor <= 0.01:
            return

        if not self.frames or self.current_frame_idx >= len(self.frames):
            return

        pix = self.frames[self.current_frame_idx]
        if pix.isNull():
            return

        base_w = pix.width()
        base_h = pix.height()

        # Pulso sutil de respiração idle
        pulse = 1.0
        if self.state == "idle":
            pulse = 1.0 + 0.015 * math.sin(self.idle_phase)

        scale = self.scale_factor * pulse
        w = int(base_w * scale)
        h = int(base_h * scale)

        ground_y = self.height() - 95
        center_x = self.width() // 2

        draw_x = center_x - w // 2
        draw_y = ground_y - h

        # Sombra sob a criatura
        shadow_w = int(w * 0.8)
        shadow_h = int(14 * scale)
        shadow_rect = QRect(center_x - shadow_w // 2, ground_y - 6, shadow_w, shadow_h)
        painter.setPen(Qt.PenStyle.NoPen)
        shadow_grad = QLinearGradient(0, shadow_rect.top(), 0, shadow_rect.bottom())
        shadow_grad.setColorAt(0, QColor(0, 0, 0, int(130 * self.alpha_factor)))
        shadow_grad.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow_grad))
        painter.drawEllipse(shadow_rect)

        # Desenhar sprite com opacidade
        painter.setOpacity(self.alpha_factor)
        painter.drawPixmap(draw_x, draw_y, w, h, pix)
        painter.setOpacity(1.0)
