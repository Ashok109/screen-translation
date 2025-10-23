import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QApplication, QSpinBox, QLabel, QCheckBox, QDoubleSpinBox, QLineEdit, QComboBox, QVBoxLayout, QGroupBox, QTextEdit, QStackedLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPoint

from ui.translator import Translator

class ControlPanel(QWidget):
    translate_requested = pyqtSignal()
    unselect_region_requested = pyqtSignal()
    translate_fullscreen_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    font_size_changed = pyqtSignal(int)
    smart_overlay_toggled = pyqtSignal(bool)
    close_requested = pyqtSignal()
    auto_translate_toggled = pyqtSignal(bool)
    subtitle_mode_toggled = pyqtSignal(bool)
    interval_changed = pyqtSignal(float)
    config_changed = pyqtSignal()
    history_toggled = pyqtSignal(bool)
    click_through_toggled = pyqtSignal(bool)
    tts_toggled = pyqtSignal(bool)

    def __init__(self, ui_translator: Translator):
        super().__init__()
        self.ui_translator = ui_translator
        self.is_dragging = False
        self.drag_position = QPoint()
        self.mouse_press_position = None
        self.is_bubble_clicked = False

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- Main Stacked Layout ---
        self.stack = QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)

        # --- Page 1: Bubble Widget ---
        self.bubble_widget = QWidget()
        bubble_layout = QVBoxLayout(self.bubble_widget)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        self.bubble_label = QLabel("V")
        self.bubble_label.setFixedSize(50, 50)
        self.bubble_label.setAlignment(Qt.AlignCenter)
        self.bubble_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                border-radius: 25px;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: rgba(20, 20, 20, 220);
            }
        """)
        bubble_layout.addWidget(self.bubble_label)
        self.stack.addWidget(self.bubble_widget)

        # --- Page 2: Expanded Controls Container ---
        self.controls_container = QWidget()
        self.setup_expanded_controls()
        self.stack.addWidget(self.controls_container)

        # --- Initial State ---
        self.stack.setCurrentIndex(0) # Start with bubble

        # --- Connections ---
        self.connect_signals()

    def update_bubble_text(self, text):
        self.bubble_label.setText(text)

    def toggle_view(self):
        current_index = self.stack.currentIndex()
        next_index = 1 - current_index

        # If collapsing, ensure the bubble will be on screen
        if next_index == 0:
            screen_geometry = QApplication.primaryScreen().availableGeometry()
            current_pos = self.pos()
            bubble_size = self.bubble_label.size()

            new_x = max(screen_geometry.x(), min(current_pos.x(), screen_geometry.right() - bubble_size.width()))
            new_y = max(screen_geometry.y(), min(current_pos.y(), screen_geometry.bottom() - bubble_size.height()))
            
            self.move(new_x, new_y)

        self.stack.setCurrentIndex(next_index)
        self.adjustSize()

    def setup_expanded_controls(self):
        main_layout = QVBoxLayout(self.controls_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.controls_container.setStyleSheet("""
            QWidget#controls_container {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 10px;
            }
            QGroupBox { font-weight: bold; color: #EEE; }
            QLabel, QCheckBox { color: #DDD; }
            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                background-color: #555;
                color: white;
                border: 1px solid #777;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        self.controls_container.setObjectName("controls_container")

        top_layout = QHBoxLayout()
        self.new_selection_button = QPushButton()
        top_layout.addWidget(self.new_selection_button)
        self.unselect_region_button = QPushButton()
        top_layout.addWidget(self.unselect_region_button)
        self.translate_fullscreen_button = QPushButton()
        top_layout.addWidget(self.translate_fullscreen_button)
        self.clear_button = QPushButton()
        top_layout.addWidget(self.clear_button)
        self.close_button = QPushButton()
        top_layout.addWidget(self.close_button)
        self.collapse_button = QPushButton("▲")
        self.collapse_button.setFixedSize(30, 30)
        top_layout.addWidget(self.collapse_button)
        main_layout.addLayout(top_layout)

        settings_layout = QHBoxLayout()
        
        # Language Selection
        lang_group = QGroupBox() # Title will be set by retranslate_ui
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel()
        lang_layout.addWidget(self.lang_label)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "vi"])
        lang_layout.addWidget(self.lang_combo)
        lang_group.setLayout(lang_layout)
        settings_layout.addWidget(lang_group)

        self.font_group = QGroupBox()
        font_layout = QHBoxLayout()
        font_size_layout = QHBoxLayout()
        self.font_size_label = QLabel()
        font_size_layout.addWidget(self.font_size_label)
        self.font_spinbox = QSpinBox()
        self.font_spinbox.setRange(0, 100)
        font_size_layout.addWidget(self.font_spinbox)

        font_color_layout = QHBoxLayout()
        self.history_font_color_label = QLabel()
        font_color_layout.addWidget(self.history_font_color_label)
        self.history_font_color_input = QLineEdit()
        font_color_layout.addWidget(self.history_font_color_input)

        original_font_color_layout = QHBoxLayout()
        self.original_font_color_label = QLabel()
        original_font_color_layout.addWidget(self.original_font_color_label)
        self.original_font_color_input = QLineEdit()
        original_font_color_layout.addWidget(self.original_font_color_input)

        self.smart_overlay_checkbox = QCheckBox()
        self.tts_checkbox = QCheckBox()

        font_group_layout = QVBoxLayout()
        font_group_layout.addLayout(font_size_layout)
        font_group_layout.addLayout(font_color_layout)
        font_group_layout.addLayout(original_font_color_layout)
        font_group_layout.addWidget(self.smart_overlay_checkbox)
        font_group_layout.addWidget(self.tts_checkbox)
        self.font_group.setLayout(font_group_layout)
        settings_layout.addWidget(self.font_group)

        self.auto_group = QGroupBox()
        auto_layout = QVBoxLayout() # Change to QVBoxLayout

        self.auto_translate_checkbox = QCheckBox()
        auto_layout.addWidget(self.auto_translate_checkbox)
        
        self.subtitle_mode_checkbox = QCheckBox()
        auto_layout.addWidget(self.subtitle_mode_checkbox)

        interval_layout = QHBoxLayout()
        self.interval_label = QLabel()
        interval_layout.addWidget(self.interval_label)
        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setRange(0.5, 60.0)
        self.interval_spinbox.setSingleStep(0.5)
        interval_layout.addWidget(self.interval_spinbox)
        auto_layout.addLayout(interval_layout)

        self.auto_group.setLayout(auto_layout)
        settings_layout.addWidget(self.auto_group)

        # History Group
        self.history_group = QGroupBox()
        history_layout = QVBoxLayout() # Changed to QVBoxLayout
        self.history_checkbox = QCheckBox()
        history_layout.addWidget(self.history_checkbox)
        self.click_through_checkbox = QCheckBox()
        history_layout.addWidget(self.click_through_checkbox)
        self.history_group.setLayout(history_layout)
        settings_layout.addWidget(self.history_group)

        main_layout.addLayout(settings_layout)

        # --- Preprocessing Group ---
        self.preprocess_group = QGroupBox()
        preprocess_layout = QVBoxLayout()
        self.preprocess_enabled_checkbox = QCheckBox()
        preprocess_layout.addWidget(self.preprocess_enabled_checkbox)
        
        upscale_layout = QHBoxLayout()
        self.upscale_checkbox = QCheckBox()
        upscale_layout.addWidget(self.upscale_checkbox)
        self.upscale_factor_spinbox = QDoubleSpinBox()
        self.upscale_factor_spinbox.setRange(1.0, 4.0)
        self.upscale_factor_spinbox.setSingleStep(0.1)
        self.upscale_factor_spinbox.setValue(2.0)
        upscale_layout.addWidget(self.upscale_factor_spinbox)
        preprocess_layout.addLayout(upscale_layout)

        self.binarize_checkbox = QCheckBox()
        preprocess_layout.addWidget(self.binarize_checkbox)
        self.preprocess_group.setLayout(preprocess_layout)
        main_layout.addWidget(self.preprocess_group)


        self.config_group = QGroupBox()
        config_layout = QVBoxLayout()

        # --- OCR Language Selection ---
        ocr_v_layout = QVBoxLayout()
        ocr_h_layout = QHBoxLayout()
        self.ocr_langs_label = QLabel()
        ocr_h_layout.addWidget(self.ocr_langs_label)
        
        self.ocr_lang_combo = QComboBox()
        self.ocr_lang_presets = {
            "English": ["en"],
            "English + Japanese": ["en", "ja"],
            "English + Chinese": ["en", "ch_sim"],
            "English + Korean": ["en", "ko"],
            "Vietnamese": ["vi"],
            "Japanese": ["ja"],
            "Korean": ["ko"],
            "Chinese": ["ch_sim"]
        }
        self.ocr_lang_combo.addItems(self.ocr_lang_presets.keys())
        ocr_h_layout.addWidget(self.ocr_lang_combo)
        ocr_v_layout.addLayout(ocr_h_layout)

        self.ocr_custom_checkbox = QCheckBox()
        ocr_v_layout.addWidget(self.ocr_custom_checkbox)
        
        self.lang_input = QLineEdit() # This is the custom input
        self.lang_input.setVisible(False) # Initially hidden
        ocr_v_layout.addWidget(self.lang_input)
        
        config_layout.addLayout(ocr_v_layout)
        # --- End OCR Language Selection ---

        translator_layout = QHBoxLayout()
        self.translator_label = QLabel()
        translator_layout.addWidget(self.translator_label)
        self.translator_combo = QComboBox()
        self.translator_combo.addItems(["Google", "OpenRouter", "Gemini", "Custom API"])
        translator_layout.addWidget(self.translator_combo)
        config_layout.addLayout(translator_layout)

        self.openrouter_key_input = QLineEdit()
        self.openrouter_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addWidget(self.openrouter_key_input)
        self.openrouter_model_input = QLineEdit()
        config_layout.addWidget(self.openrouter_model_input)

        self.gemini_key_input = QLineEdit()
        self.gemini_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addWidget(self.gemini_key_input)
        self.gemini_model_input = QLineEdit()
        config_layout.addWidget(self.gemini_model_input)

        self.custom_api_base_url_input = QLineEdit()
        config_layout.addWidget(self.custom_api_base_url_input)
        self.custom_api_key_input = QLineEdit()
        self.custom_api_key_input.setEchoMode(QLineEdit.Password)
        config_layout.addWidget(self.custom_api_key_input)
        self.custom_api_model_input = QLineEdit()
        config_layout.addWidget(self.custom_api_model_input)
        
        self.config_group.setLayout(config_layout)
        main_layout.addWidget(self.config_group)

        self.prompt_group = QGroupBox()
        prompt_layout = QVBoxLayout()
        self.use_custom_prompt_checkbox = QCheckBox()
        prompt_layout.addWidget(self.use_custom_prompt_checkbox)
        self.custom_prompt_input = QTextEdit()
        prompt_layout.addWidget(self.custom_prompt_input)
        self.prompt_group.setLayout(prompt_layout)
        main_layout.addWidget(self.prompt_group)

        self.save_config_button = QPushButton()
        main_layout.addWidget(self.save_config_button)

        # Footer
        self.footer_label = QLabel()
        self.footer_label.setOpenExternalLinks(True)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("color: #AAA; font-size: 9px;")
        main_layout.addWidget(self.footer_label)
        
        self.retranslate_ui() # Set initial text

    def retranslate_ui(self):
        # This method updates all UI text elements to the current language
        t = self.ui_translator.get_string
        self.new_selection_button.setText(t("new_selection"))
        self.unselect_region_button.setText(t("unselect_region"))
        self.translate_fullscreen_button.setText(t("translate_fullscreen"))
        self.clear_button.setText(t("clear"))
        self.close_button.setText(t("close"))
        self.font_group.setTitle(t("display_group"))
        self.font_size_label.setText(t("font_size_label"))
        self.history_font_color_label.setText(t("history_font_color_label"))
        self.original_font_color_label.setText(t("original_font_color_label"))
        self.smart_overlay_checkbox.setText(t("smart_overlay_checkbox"))
        self.tts_checkbox.setText(t("tts_checkbox"))
        self.auto_group.setTitle(t("auto_translate_group"))
        self.auto_translate_checkbox.setText(t("auto_translate_checkbox"))
        self.subtitle_mode_checkbox.setText(t("subtitle_mode_checkbox"))
        self.interval_label.setText(t("interval_label"))
        self.history_group.setTitle(t("history_group"))
        self.history_checkbox.setText(t("show_history_checkbox"))
        self.click_through_checkbox.setText(t("click_through_checkbox"))
        self.preprocess_group.setTitle(t("preprocessing_group"))
        self.preprocess_enabled_checkbox.setText(t("enable_preprocessing_checkbox"))
        self.upscale_checkbox.setText(t("upscale_checkbox"))
        self.binarize_checkbox.setText(t("binarize_checkbox"))
        self.config_group.setTitle(t("config_group"))
        self.ocr_langs_label.setText(t("ocr_langs_label"))
        self.ocr_custom_checkbox.setText(t("ocr_custom_checkbox"))
        self.translator_label.setText(t("translator_label"))
        self.openrouter_key_input.setPlaceholderText(t("openrouter_api_key_placeholder"))
        self.openrouter_model_input.setPlaceholderText(t("openrouter_model_placeholder"))
        self.gemini_key_input.setPlaceholderText(t("gemini_api_key_placeholder"))
        self.gemini_model_input.setPlaceholderText(t("gemini_model_placeholder"))
        self.custom_api_base_url_input.setPlaceholderText(t("custom_api_base_url_placeholder"))
        self.custom_api_key_input.setPlaceholderText(t("custom_api_key_placeholder"))
        self.custom_api_model_input.setPlaceholderText(t("custom_api_model_placeholder"))
        self.prompt_group.setTitle(t("custom_prompt_group"))
        self.use_custom_prompt_checkbox.setText(t("use_custom_prompt_checkbox"))
        self.custom_prompt_input.setPlaceholderText(t("custom_prompt_placeholder"))
        self.save_config_button.setText(t("save_button"))
        # Assuming lang_group was added in setup_expanded_controls
        self.lang_label.setText(t("language_label"))
        self.footer_label.setText(t("footer_text"))


    def connect_signals(self):
        self.collapse_button.clicked.connect(self.toggle_view)
        # self.bubble_button is now a label, click is handled in mouseReleaseEvent
        self.new_selection_button.clicked.connect(self.translate_requested)
        self.unselect_region_button.clicked.connect(self.unselect_region_requested)
        self.translate_fullscreen_button.clicked.connect(self.translate_fullscreen_requested)
        self.clear_button.clicked.connect(self.clear_requested)
        self.close_button.clicked.connect(self.close_requested)
        self.font_spinbox.valueChanged.connect(self.font_size_changed)
        self.smart_overlay_checkbox.toggled.connect(self.smart_overlay_toggled)
        self.auto_translate_checkbox.toggled.connect(self.auto_translate_toggled)
        self.subtitle_mode_checkbox.toggled.connect(self.subtitle_mode_toggled)
        self.interval_spinbox.valueChanged.connect(self.interval_changed)
        self.save_config_button.clicked.connect(self.config_changed)
        self.history_checkbox.toggled.connect(self.history_toggled)
        self.click_through_checkbox.toggled.connect(self.click_through_toggled)
        self.tts_checkbox.toggled.connect(self.tts_toggled)
        self.translator_combo.currentIndexChanged.connect(self.update_visibility)
        self.use_custom_prompt_checkbox.toggled.connect(self.update_visibility)
        self.ocr_custom_checkbox.toggled.connect(self.update_ocr_input_visibility)

    def update_ocr_input_visibility(self, checked):
        self.ocr_lang_combo.setDisabled(checked)
        self.lang_input.setVisible(checked)
        self.adjustSize()

    def update_visibility(self):
        selected_translator = self.translator_combo.currentText()
        is_openrouter = selected_translator == "OpenRouter"
        is_gemini = selected_translator == "Gemini"
        is_custom = selected_translator == "Custom API"
        is_ai = is_openrouter or is_gemini or is_custom

        self.openrouter_key_input.setVisible(is_openrouter)
        self.openrouter_model_input.setVisible(is_openrouter)
        self.gemini_key_input.setVisible(is_gemini)
        self.gemini_model_input.setVisible(is_gemini)
        self.custom_api_base_url_input.setVisible(is_custom)
        self.custom_api_key_input.setVisible(is_custom)
        self.custom_api_model_input.setVisible(is_custom)
        self.prompt_group.setVisible(is_ai)
        self.custom_prompt_input.setEnabled(self.use_custom_prompt_checkbox.isChecked())
        self.adjustSize()

    def get_config_data(self):
        ocr_langs = []
        if self.ocr_custom_checkbox.isChecked():
            ocr_langs = [lang.strip() for lang in self.lang_input.text().split(',') if lang.strip()]
        else:
            selected_preset = self.ocr_lang_combo.currentText()
            ocr_langs = self.ocr_lang_presets.get(selected_preset, ["en"])

        return {
            "preprocess_enabled": self.preprocess_enabled_checkbox.isChecked(),
            "upscale_enabled": self.upscale_checkbox.isChecked(),
            "upscale_factor": self.upscale_factor_spinbox.value(),
            "binarize_enabled": self.binarize_checkbox.isChecked(),
            "ocr_languages": ocr_langs,
            "translator": self.translator_combo.currentText(),
            "openrouter_api_key": self.openrouter_key_input.text(),
            "openrouter_model": self.openrouter_model_input.text(),
            "gemini_api_key": self.gemini_key_input.text(),
            "gemini_model": self.gemini_model_input.text(),
            "custom_api_base_url": self.custom_api_base_url_input.text(),
            "custom_api_key": self.custom_api_key_input.text(),
            "custom_api_model": self.custom_api_model_input.text(),
            "use_custom_prompt": self.use_custom_prompt_checkbox.isChecked(),
            "custom_prompt": self.custom_prompt_input.toPlainText(),
            "language": self.lang_combo.currentText(),
            "history_font_color": self.history_font_color_input.text(),
            "original_font_color": self.original_font_color_input.text(),
            "smart_overlay_enabled": self.smart_overlay_checkbox.isChecked(),
            "tts_enabled": self.tts_checkbox.isChecked()
        }

    def set_config_data(self, config):
        self.lang_combo.setCurrentText(config.get("language", "en"))
        self.preprocess_enabled_checkbox.setChecked(config.get("preprocess_enabled", True))
        self.upscale_checkbox.setChecked(config.get("upscale_enabled", True))
        self.upscale_factor_spinbox.setValue(config.get("upscale_factor", 2.0))
        self.binarize_checkbox.setChecked(config.get("binarize_enabled", True))
        
        # Set OCR language input based on config
        config_langs = sorted(config.get("ocr_languages", ["en"]))
        preset_match = None
        for preset_name, preset_langs in self.ocr_lang_presets.items():
            if sorted(preset_langs) == config_langs:
                preset_match = preset_name
                break
        
        if preset_match:
            self.ocr_custom_checkbox.setChecked(False)
            self.ocr_lang_combo.setCurrentText(preset_match)
        else:
            self.ocr_custom_checkbox.setChecked(True)
            self.lang_input.setText(",".join(config_langs))

        self.update_ocr_input_visibility(self.ocr_custom_checkbox.isChecked())

        self.translator_combo.setCurrentText(config.get("translator", "Google"))
        self.openrouter_key_input.setText(config.get("openrouter_api_key", ""))
        self.openrouter_model_input.setText(config.get("openrouter_model", ""))
        self.gemini_key_input.setText(config.get("gemini_api_key", ""))
        self.gemini_model_input.setText(config.get("gemini_model", ""))
        self.custom_api_base_url_input.setText(config.get("custom_api_base_url", ""))
        self.custom_api_key_input.setText(config.get("custom_api_key", ""))
        self.custom_api_model_input.setText(config.get("custom_api_model", ""))
        self.use_custom_prompt_checkbox.setChecked(config.get("use_custom_prompt", False))
        self.custom_prompt_input.setPlainText(config.get("custom_prompt", ""))
        self.history_font_color_input.setText(config.get("history_font_color", "#99EEFF"))
        self.original_font_color_input.setText(config.get("original_font_color", "#CCCCCC"))
        self.smart_overlay_checkbox.setChecked(config.get("smart_overlay_enabled", True))
        self.tts_checkbox.setChecked(config.get("tts_enabled", False))
        self.update_visibility()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.mouse_press_position = event.globalPos()
            # Check if the click is on the bubble
            if self.stack.currentIndex() == 0:
                self.is_bubble_clicked = True
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            # If the mouse has moved significantly, it's a drag, not a click
            if self.mouse_press_position and (event.globalPos() - self.mouse_press_position).manhattanLength() > QApplication.startDragDistance():
                self.is_bubble_clicked = False

            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # If it was a click on the bubble (not a drag), toggle the view
            if self.is_bubble_clicked:
                self.toggle_view()

            self.is_dragging = False
            self.is_bubble_clicked = False
            self.mouse_press_position = None
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    panel = ControlPanel()
    panel.show()
    sys.exit(app.exec_())
