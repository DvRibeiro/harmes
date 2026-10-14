"""Gerador de ícones vetoriais com QPainter para a interface do Harmes."""

import math
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath, QIcon


def create_vector_icon(icon_type: str, size: int = 24, color: str = "#9ca3af") -> QIcon:
    """Desenha dinamicamente ícones vetoriais modernos sem depender de fontes ou SVGs externos."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    pen = QPen(QColor(color), 1.75)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    w, h = float(size), float(size)
    pad = size * 0.25

    if icon_type == "close":
        painter.drawLine(int(pad), int(pad), int(w - pad), int(h - pad))
        painter.drawLine(int(w - pad), int(pad), int(pad), int(h - pad))

    elif icon_type == "minimize":
        painter.drawLine(int(pad), int(h / 2), int(w - pad), int(h / 2))

    elif icon_type == "settings":
        cx, cy = w / 2, h / 2
        r_outer = size * 0.32
        r_inner = size * 0.16
        painter.drawEllipse(QRectF(cx - r_inner, cy - r_inner, r_inner * 2, r_inner * 2))
        teeth = 6
        for i in range(teeth):
            angle = i * (2 * math.pi / teeth)
            x1 = cx + (r_inner + 1) * math.cos(angle)
            y1 = cy + (r_inner + 1) * math.sin(angle)
            x2 = cx + r_outer * math.cos(angle)
            y2 = cy + r_outer * math.sin(angle)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    elif icon_type == "send":
        path = QPainterPath()
        path.moveTo(w * 0.28, h * 0.24)
        path.lineTo(w * 0.76, h * 0.5)
        path.lineTo(w * 0.28, h * 0.76)
        path.lineTo(w * 0.40, h * 0.5)
        path.closeSubpath()
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

    elif icon_type == "copy":
        painter.drawRoundedRect(QRectF(w * 0.32, w * 0.32, w * 0.44, h * 0.44), 2, 2)
        painter.drawLine(int(w * 0.22), int(h * 0.55), int(w * 0.22), int(h * 0.22))
        painter.drawLine(int(w * 0.22), int(h * 0.22), int(w * 0.55), int(h * 0.22))

    elif icon_type == "report":
        painter.drawRoundedRect(QRectF(w * 0.26, h * 0.18, w * 0.48, h * 0.64), 2, 2)
        painter.drawLine(int(w * 0.36), int(h * 0.36), int(w * 0.64), int(h * 0.36))
        painter.drawLine(int(w * 0.36), int(h * 0.50), int(w * 0.64), int(h * 0.50))
        painter.drawLine(int(w * 0.36), int(h * 0.64), int(w * 0.54), int(h * 0.64))

    painter.end()
    return QIcon(pixmap)
