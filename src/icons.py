from math import cos, pi, sin

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def icon_pixmap(name, color="#d5d9dc", size=24):
    canvas = QPixmap(size * 2, size * 2)
    canvas.setDevicePixelRatio(2)
    canvas.fill(Qt.GlobalColor.transparent)

    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.scale(size / 24, size / 24)
    painter.setPen(QPen(QColor(color), 1.9, Qt.PenStyle.SolidLine,
                        Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if name == "copy":
        painter.drawRoundedRect(QRectF(8, 7, 12, 13), 2, 2)
        path = QPainterPath()
        path.moveTo(16, 7)
        path.lineTo(16, 5.5)
        path.cubicTo(16, 4, 15, 3, 13.5, 3)
        path.lineTo(5.5, 3)
        path.cubicTo(4, 3, 3, 4, 3, 5.5)
        path.lineTo(3, 13.5)
        path.cubicTo(3, 15, 4, 16, 5.5, 16)
        path.lineTo(8, 16)
        painter.drawPath(path)
    elif name == "star":
        path = QPainterPath()
        for i in range(10):
            angle = -pi / 2 + i * pi / 5
            radius = 9 if i % 2 == 0 else 4.2
            point = QPointF(12 + radius * cos(angle), 12 + radius * sin(angle))
            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)
        path.closeSubpath()
        painter.drawPath(path)
    elif name == "link":
        upper = QPainterPath()
        upper.moveTo(9.7, 7.1)
        upper.lineTo(11.8, 5)
        upper.cubicTo(14, 2.8, 17.6, 2.8, 19.7, 5)
        upper.cubicTo(21.9, 7.2, 21.9, 10.7, 19.7, 12.8)
        upper.lineTo(16.9, 15.6)
        upper.cubicTo(15, 17.5, 12.2, 17.8, 10.1, 16.5)
        lower = QPainterPath()
        lower.moveTo(14.3, 16.9)
        lower.lineTo(12.2, 19)
        lower.cubicTo(10, 21.2, 6.4, 21.2, 4.3, 19)
        lower.cubicTo(2.1, 16.8, 2.1, 13.3, 4.3, 11.2)
        lower.lineTo(7.1, 8.4)
        lower.cubicTo(9, 6.5, 11.8, 6.2, 13.9, 7.5)
        painter.drawPath(upper)
        painter.drawPath(lower)
        painter.drawLine(QPointF(8.9, 15.1), QPointF(15.1, 8.9))
    elif name == "image":
        painter.drawRoundedRect(QRectF(3, 4, 18, 16), 2, 2)
        painter.drawEllipse(QRectF(6.3, 7.1, 3, 3))
        landscape = QPainterPath()
        landscape.moveTo(3.5, 17.5)
        landscape.lineTo(9.2, 12)
        landscape.lineTo(12.2, 15)
        landscape.lineTo(15, 12.2)
        landscape.lineTo(20.4, 17.8)
        painter.drawPath(landscape)
    elif name == "text":
        painter.drawLine(QPointF(4, 6), QPointF(20, 6))
        painter.drawLine(QPointF(4, 12), QPointF(20, 12))
        painter.drawLine(QPointF(4, 18), QPointF(16.5, 18))
    elif name == "settings":
        painter.drawEllipse(QRectF(6.5, 6.5, 11, 11))
        painter.drawEllipse(QRectF(10, 10, 4, 4))
        for i in range(8):
            angle = i * pi / 4
            painter.drawLine(QPointF(12 + 8 * cos(angle), 12 + 8 * sin(angle)),
                             QPointF(12 + 10 * cos(angle), 12 + 10 * sin(angle)))
    elif name == "export":
        painter.drawLine(QPointF(12, 3), QPointF(12, 15))
        painter.drawLine(QPointF(8, 7), QPointF(12, 3))
        painter.drawLine(QPointF(16, 7), QPointF(12, 3))
        painter.drawLine(QPointF(4, 15), QPointF(4, 20))
        painter.drawLine(QPointF(4, 20), QPointF(20, 20))
        painter.drawLine(QPointF(20, 20), QPointF(20, 15))
    elif name == "about":
        painter.drawEllipse(QRectF(3, 3, 18, 18))
        painter.drawLine(QPointF(12, 11), QPointF(12, 17))
        painter.drawPoint(QPointF(12, 7.5))
    else:
        painter.end()
        raise ValueError(f"Unknown icon: {name}")

    painter.end()
    return canvas


def app_icon(name, color="#d5d9dc", size=24):
    return QIcon(icon_pixmap(name, color, size))
