import sys
import logging
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPainterPath

class DisplayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        # This window is permanently click-through
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        self.translation_results = []
        self.custom_font_size = 0

    def set_results(self, results):
        self.translation_results = results
        self.update()

    def set_font_size(self, size):
        self.custom_font_size = size
        self.update()

    def clear(self):
        self.translation_results = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.translation_results:
            return

        # Draw a single background for all text
        path = QPainterPath()
        for box, _ in self.translation_results:
            top_left = box[0]
            bottom_right = box[2]
            rect = QRect(QPoint(int(top_left[0]), int(top_left[1])), QPoint(int(bottom_right[0]), int(bottom_right[1])))
            path.addRect(QRectF(rect))
        
        painter.setBrush(QColor(0, 0, 0, 200))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

        # Draw translation results
        for box, translated_text in self.translation_results:
            top_left = box[0]
            bottom_right = box[2]
            rect = QRect(QPoint(int(top_left[0]), int(top_left[1])), QPoint(int(bottom_right[0]), int(bottom_right[1])))
            
            painter.setPen(QColor(255, 255, 255))
            
            font = QFont()
            
            if self.custom_font_size > 0:
                font_size = self.custom_font_size
            else:
                font_size = int(rect.height() * 0.7)
            
            font.setPixelSize(max(1, font_size))
            painter.setFont(font)
            
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, translated_text)
