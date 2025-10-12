import sys
import logging
from PyQt5.QtWidgets import QWidget, QApplication, QSizeGrip
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen

class SelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_dragging = False
        
        # Grips for resizing
        self.grip_size = 16
        self.grips = []
        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.grip_size, self.grip_size)
            self.grips.append(grip)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        rect = self.rect()
        self.grips[0].move(rect.topLeft())
        self.grips[1].move(rect.topRight() - QPoint(self.grip_size, 0))
        self.grips[2].move(rect.bottomLeft() - QPoint(0, self.grip_size))
        self.grips[3].move(rect.bottomRight() - QPoint(self.grip_size, self.grip_size))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw semi-transparent background and border
        painter.setPen(QPen(QColor(255, 0, 0, 200), 2))
        painter.setBrush(QColor(0, 0, 0, 20))
        painter.drawRect(self.rect())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SelectionWindow()
    window.setGeometry(100, 100, 400, 200)
    window.show()
    sys.exit(app.exec_())
