from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QSizePolicy, QApplication, QLabel, QSizeGrip
from PyQt5.QtCore import Qt, QPoint

class ChatWindow(QWidget):
    def __init__(self, ui_translator, config):
        super().__init__()
        self.ui_translator = ui_translator
        self.config = config
        
        # State for dragging
        self.is_dragging = False
        self.drag_position = QPoint()

        self.setWindowTitle(self.ui_translator.get_string("translation_history_title"))
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("chat_window_container")
        self.setStyleSheet("""
            #chat_window_container {
                background-color: rgba(30, 30, 30, 220);
                border-radius: 10px;
                border: 1px solid #888;
                color: white;
            }
            QLabel#title_bar {
                font-weight: bold;
                padding: 5px;
                color: #EEE;
            }
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.2);
                border: none;
                color: #DDD;
                font-size: 12px;
                border-radius: 5px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1) # Tighter margins for the container
        
        title_bar_layout = QHBoxLayout()
        self.title_bar = QLabel(self.ui_translator.get_string("translation_history_title"))
        self.title_bar.setObjectName("title_bar")
        self.title_bar.setAlignment(Qt.AlignCenter)
        
        self.clear_history_button = QPushButton()
        self.clear_history_button.setFixedSize(20, 20)
        self.clear_history_button.setText("X")
        self.clear_history_button.setStyleSheet("QPushButton { border-radius: 10px; background-color: #808080; color: white; font-weight: bold; } QPushButton:hover { background-color: #A0A0A0; }")
        self.clear_history_button.clicked.connect(self.clear_history)

        title_bar_layout.addWidget(self.clear_history_button)
        title_bar_layout.addWidget(self.title_bar)
        self.layout.addLayout(title_bar_layout)

        self.history_text_edit = QTextEdit()
        self.history_text_edit.setReadOnly(True)
        self.layout.addWidget(self.history_text_edit)

        self.setMinimumSize(200, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create size grips
        self.grip_size = 16
        self.grips = []
        for _ in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.grip_size, self.grip_size)
            self.grips.append(grip)

    def add_message(self, original_text, translated_text):
        """Adds a new entry to the history."""
        t = self.ui_translator.get_string
        translated_color = self.config.get("history_font_color", "#99EEFF")
        original_color = self.config.get("original_font_color", "#CCCCCC")
        
        formatted_entry = (
            f"<p style='color: #999;'>---</p>"
            f"<p style='color: {original_color};'><b>{t('original_text')}:</b> {original_text}</p>"
            f"<p style='color: {translated_color};'><b>{t('translated_text')}:</b> {translated_text}</p>"
        )
        self.history_text_edit.append(formatted_entry)
        # Auto-scroll to the bottom
        self.history_text_edit.verticalScrollBar().setValue(self.history_text_edit.verticalScrollBar().maximum())

    def clear_history(self):
        self.history_text_edit.clear()

    def retranslate_ui(self):
        """Updates the window title when the language changes."""
        title = self.ui_translator.get_string("translation_history_title")
        self.setWindowTitle(title)
        self.title_bar.setText(title)

    def update_config(self, new_config):
        """Receives the updated config object from the controller."""
        self.config = new_config
        # We don't need to redraw existing text, new text will use the new color.

    def set_click_through(self, enabled):
        """Toggles the window's passthrough state."""
        # Save current geometry
        current_geometry = self.geometry()

        current_flags = self.windowFlags()
        if enabled:
            self.setWindowFlags(current_flags | Qt.WindowTransparentForInput)
        else:
            self.setWindowFlags(current_flags & ~Qt.WindowTransparentForInput)
        
        # Re-show the window to apply flag changes
        self.show()
        
        # Restore geometry
        self.setGeometry(current_geometry)

    def resizeEvent(self, event):
        """Called when the window is resized, used to move the grips."""
        super().resizeEvent(event)
        rect = self.rect()
        # Top-left
        self.grips[0].move(rect.topLeft())
        # Top-right
        self.grips[1].move(rect.topRight() - QPoint(self.grip_size, 0))
        # Bottom-left
        self.grips[2].move(rect.bottomLeft() - QPoint(0, self.grip_size))
        # Bottom-right
        self.grips[3].move(rect.bottomRight() - QPoint(self.grip_size, self.grip_size))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if the press is on the title bar for dragging
            if self.title_bar.geometry().contains(event.pos()):
                self.is_dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()
