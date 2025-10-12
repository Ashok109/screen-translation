import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

class SnipWindow(QWidget):
    region_selected = pyqtSignal(QRect)

    def __init__(self):
        super().__init__()
        screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

        self.begin = QPoint()
        self.end = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        # Dim the screen
        painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
        painter.drawRect(self.rect())

        # Draw the selection rectangle
        if not self.begin.isNull() and not self.end.isNull():
            selection_rect = QRect(self.begin, self.end).normalized()
            # Clear the dimmed area inside the selection
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.drawRect(selection_rect)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            # Draw a border around the selection
            painter.setPen(QPen(QColor(255, 0, 0, 200), 2))
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.end = self.begin
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.hide()
            selection_rect = QRect(self.begin, self.end).normalized()
            
            # Reset points for next use
            self.begin = QPoint()
            self.end = QPoint()

            # Ensure the rect has a valid size
            if selection_rect.width() > 5 and selection_rect.height() > 5:
                self.region_selected.emit(selection_rect)
            # Do not close, just hide. The window will be reused.
