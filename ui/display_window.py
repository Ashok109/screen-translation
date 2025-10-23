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
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        self.translation_results = []
        self.custom_font_size = 0
        self.smart_overlay_enabled = True # Default to on, will be controlled by config later
        self.is_subtitle_mode = False

    def set_subtitle_mode(self, enabled):
        self.is_subtitle_mode = enabled

    def set_results(self, results):
        # In subtitle mode, don't clear the screen if there are no new results.
        # This prevents flickering between subtitles.
        if not results and self.is_subtitle_mode:
            return
            
        self.translation_results = results
        self.update()

    def set_font_size(self, size):
        self.custom_font_size = size
        self.update()

    def set_smart_overlay(self, enabled):
        self.smart_overlay_enabled = enabled
        self.update()

    def clear(self):
        self.translation_results = []
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.translation_results:
            return

        for result in self.translation_results:
            box = result['box']
            translated_text = result['translated']
            bg_color_tuple = result.get('bg_color', (0, 0, 0))
            fg_color_tuple = result.get('fg_color', (255, 255, 255))

            top_left = box[0]
            bottom_right = box[2]
            rect = QRect(QPoint(int(top_left[0]), int(top_left[1])), QPoint(int(bottom_right[0]), int(bottom_right[1])))
            
            if self.smart_overlay_enabled:
                # Smart Overlay: Cover original text with detected background color
                bg_color = QColor(*bg_color_tuple)
                painter.setBrush(bg_color)
                painter.setPen(Qt.NoPen)
                painter.drawRect(rect)
                
                # Set pen to detected foreground color
                fg_color = QColor(*fg_color_tuple)
                painter.setPen(fg_color)
            else:
                # Default Overlay: Semi-transparent black background
                painter.setBrush(QColor(0, 0, 0, 200))
                painter.setPen(Qt.NoPen)
                painter.drawRect(rect)
                
                # Set pen to white
                painter.setPen(QColor(255, 255, 255))

            # Draw the text
            font = QFont()
            if self.custom_font_size > 0:
                font_size = self.custom_font_size
            else:
                # Auto-size font based on box height
                font_size = int(rect.height() * 0.7)
            
            font.setPixelSize(max(1, font_size))
            painter.setFont(font)
            
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, translated_text)
