import sys
import logging
import json
import os
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread, QRect, Qt, QTimer

from ui.selection_window import SelectionWindow
from ui.display_window import DisplayWindow
from ui.snip_window import SnipWindow
from ui.control_panel import ControlPanel
from ui.chat_window import ChatWindow
from ui.translator import Translator as UiTranslator
from ocr.easy_ocr import EasyOcr
from core.hotkey_manager import HotkeyManager
from core.worker import Worker
from core.subtitle_processor import SubtitleProcessor
from core.tts_manager import TTSManager
from translator.google_translate import GoogleTranslate
from translator.open_router import OpenRouterTranslator
from translator.gemini import GeminiTranslator
from translator.custom_api import CustomApiTranslator

# Function to determine the base path for resources (for PyInstaller)
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class AppController:
    def __init__(self, app):
        self.app = app
        self.model_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'model_dump')
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            
        self.ocr_engine = None
        self.translator = None
        self.running_workers = []
        self.config_file = 'config.json'
        self.config = self.load_config()
        self.ui_translator = UiTranslator(self.config.get("language", "en"))

        # Auto-translation state
        self.auto_translate_timer = QTimer()
        self.countdown_timer = QTimer()
        self.auto_translate_enabled = False
        self.translation_interval = 2500  # Default 2.5 seconds in ms
        self.countdown_value = 0
        self.last_translation_mode = None # 'region' or 'fullscreen'
        self.is_translating = False

        # Subtitle mode state
        self.subtitle_mode_enabled = False
        self.subtitle_capture_timer = QTimer()
        self.subtitle_processor = None
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        # Create UI components
        self.tts_manager = TTSManager()
        self.tts_enabled = self.config.get("tts_enabled", False)
        self.control_panel = ControlPanel(self.ui_translator)
        self.selection_window = SelectionWindow()
        self.display_window = DisplayWindow()
        self.snip_window = SnipWindow() # Create once and reuse
        self.chat_window = ChatWindow(self.ui_translator, self.config)

        # Initial setup
        self.selection_window.hide()
        self.display_window.show()
        self.snip_window.hide()

        self.load_services()
        self.setup_connections()
        self.setup_hotkeys()

    def load_config(self):
        default_config = {
            "hotkeys": {
                "snip_translate": "+", "region_translate": "<alt>+<ctrl>+r",
                "fullscreen_translate": "<alt>+<ctrl>+f", "clear_results": "-",
                "toggle_subtitle_mode": "<alt>+<ctrl>+s"
            },
            "ocr_languages": ["en"],
            "translator": "Google",
            "preprocess_enabled": True,
            "upscale_enabled": True,
            "upscale_factor": 2.0,
            "binarize_enabled": True,
            "openrouter_api_key": "",
            "gemini_api_key": "",
            "gemini_model": "gemini-1.5-flash",
            "custom_api_base_url": "",
            "custom_api_key": "",
            "custom_api_model": "",
            "openrouter_model": "google/gemini-flash-1.5",
            "use_custom_prompt": False,
            "custom_prompt": "",
            "language": "en",
            "dest_lang": "vi",
            "dest_lang_custom_enabled": False,
            "history_font_color": "#99EEFF",
            "original_font_color": "#CCCCCC",
            "smart_overlay_enabled": True,
            "tts_enabled": False,
            "language_filter_enabled": True
        }
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Ensure all keys from default_config are present
                for key, value in default_config.items():
                    config.setdefault(key, value)
                return config
        except (FileNotFoundError, json.JSONDecodeError):
            return default_config

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def load_services(self):
        # Load OCR Engine
        print("Loading OCR engine...")
        ocr_langs = self.config.get('ocr_languages', ['en'])
        self.ocr_engine = EasyOcr(languages=ocr_langs, model_storage_directory=self.model_dir)
        print(f"OCR engine loaded for languages: {ocr_langs}")
        print(f"OCR models will be stored in: {self.model_dir}")

        # Load Translator
        print("Loading Translator...")
        translator_name = self.config.get("translator", "Google")
        use_custom_prompt = self.config.get("use_custom_prompt", False)
        custom_prompt = self.config.get("custom_prompt", "")
        
        try:
            if translator_name == "OpenRouter":
                self.translator = OpenRouterTranslator(
                    api_key=self.config.get("openrouter_api_key"),
                    model=self.config.get("openrouter_model"),
                    use_custom_prompt=use_custom_prompt,
                    custom_prompt=custom_prompt
                )
            elif translator_name == "Gemini":
                self.translator = GeminiTranslator(
                    api_key=self.config.get("gemini_api_key"),
                    model=self.config.get("gemini_model"),
                    use_custom_prompt=use_custom_prompt,
                    custom_prompt=custom_prompt
                )
            elif translator_name == "Custom API":
                self.translator = CustomApiTranslator(
                    base_url=self.config.get("custom_api_base_url"),
                    api_key=self.config.get("custom_api_key"),
                    model=self.config.get("custom_api_model"),
                    use_custom_prompt=use_custom_prompt,
                    custom_prompt=custom_prompt
                )
            else: # Default to Google
                translator_name = "Google"
                self.translator = GoogleTranslate()
            print(f"Translator loaded: {translator_name}")
        except ValueError as e:
            print(f"Error loading translator: {e}")
            QMessageBox.critical(self.control_panel, "Translator Error", f"Failed to load {translator_name}: {e}\n\nFalling back to Google Translate.")
            self.translator = GoogleTranslate()
            self.config["translator"] = "Google"

        # Update control panel with loaded config
        self.control_panel.set_config_data(self.config)
        self.display_window.set_smart_overlay(self.config.get("smart_overlay_enabled", True))


    def setup_connections(self):
        # Control Panel connections
        self.control_panel.new_selection_button.clicked.connect(self.show_selection_window)
        self.control_panel.unselect_region_requested.connect(self.selection_window.hide)
        self.control_panel.translate_fullscreen_requested.connect(self.translate_fullscreen)
        self.control_panel.clear_requested.connect(self.display_window.clear)
        self.control_panel.font_size_changed.connect(self.display_window.set_font_size)
        self.control_panel.smart_overlay_toggled.connect(self.display_window.set_smart_overlay)
        self.control_panel.tts_toggled.connect(self.set_tts_enabled)
        self.control_panel.close_requested.connect(self.app.quit)
        self.snip_window.region_selected.connect(self.translate_snip_region)
        self.control_panel.history_toggled.connect(self.toggle_chat_window)
        self.control_panel.click_through_toggled.connect(self.chat_window.set_click_through)

        # Auto-translation connections
        self.control_panel.auto_translate_toggled.connect(self.set_auto_translate)
        self.control_panel.subtitle_mode_toggled.connect(self.set_subtitle_mode)
        self.control_panel.interval_changed.connect(self.set_translation_interval)
        self.auto_translate_timer.timeout.connect(self.trigger_auto_translation)
        self.countdown_timer.timeout.connect(self.update_countdown)

        # Config change connection
        self.control_panel.config_changed.connect(self.handle_config_change)

        # Worker thread cleanup
        self.app.aboutToQuit.connect(self.cleanup_worker_thread)
        self.app.aboutToQuit.connect(self.stop_subtitle_processor)

    def setup_hotkeys(self):
        self.hotkey_thread = QThread()
        self.hotkey_manager = HotkeyManager()
        self.hotkey_manager.moveToThread(self.hotkey_thread)

        self.hotkey_thread.started.connect(self.hotkey_manager.run)
        self.app.aboutToQuit.connect(self.hotkey_manager.stop)
        self.app.aboutToQuit.connect(self.hotkey_thread.quit)
        self.app.aboutToQuit.connect(self.hotkey_thread.wait)

        # Use QueuedConnection to safely invoke slots in the main GUI thread from the hotkey thread
        self.hotkey_manager.snip_translate_hotkey.connect(self.start_snip_mode, Qt.QueuedConnection)
        self.hotkey_manager.region_translate_hotkey.connect(self.translate_selection_region, Qt.QueuedConnection)
        self.hotkey_manager.fullscreen_translate_hotkey.connect(self.translate_fullscreen, Qt.QueuedConnection)
        self.hotkey_manager.clear_results_hotkey.connect(self.display_window.clear, Qt.QueuedConnection)
        self.hotkey_manager.toggle_subtitle_mode_hotkey.connect(self.toggle_subtitle_mode_by_hotkey, Qt.QueuedConnection)

        self.hotkey_thread.start()

    def toggle_subtitle_mode_by_hotkey(self):
        logging.info("Subtitle mode toggled by hotkey.")
        current_state = self.control_panel.subtitle_mode_checkbox.isChecked()
        self.control_panel.subtitle_mode_checkbox.setChecked(not current_state)

    def handle_config_change(self):
        new_config_data = self.control_panel.get_config_data()

        # Validate OCR languages
        if not new_config_data["ocr_languages"]:
            QMessageBox.warning(self.control_panel, "Warning", "OCR language list cannot be empty.")
            # Restore the old value in the UI
            self.control_panel.lang_input.setText(",".join(self.config.get("ocr_languages", ["en"])))
            return

        # Update the main config object
        self.config.update(new_config_data)
        self.save_config()

        # Reload services with the new configuration
        self.load_services()

        # Update UI language if it has changed
        new_lang = self.config.get("language", "en")
        if self.ui_translator.language != new_lang:
            self.ui_translator.set_language(new_lang)
            self.control_panel.retranslate_ui() # A new method to update texts
            self.chat_window.retranslate_ui()
        
        # Push the updated config to the chat window
        self.chat_window.update_config(self.config)
        
        # Push smart overlay setting to display window
        self.display_window.set_smart_overlay(self.config.get("smart_overlay_enabled", True))

        QMessageBox.information(self.control_panel, "Success",
                                "Configuration has been saved and applied.")

    def toggle_chat_window(self, show):
        logging.info(f"toggle_chat_window called with show={show}")
        if show:
            logging.info("Attempting to show chat window...")
            # If showing for the first time or position is weird, center it.
            if self.chat_window.pos().x() == 0 and self.chat_window.pos().y() == 0:
                logging.info("Centering chat window on screen.")
                screen_geometry = QApplication.primaryScreen().geometry()
                center_point = screen_geometry.center()
                window_size = self.chat_window.size()
                self.chat_window.move(center_point.x() - window_size.width() // 2, center_point.y() - window_size.height() // 2)
            
            self.chat_window.show()
            self.chat_window.raise_() # Bring to front
            logging.info(f"Chat window is visible: {self.chat_window.isVisible()}")
            logging.info(f"Chat window position: {self.chat_window.pos()}")
            logging.info(f"Chat window size: {self.chat_window.size()}")
        else:
            logging.info("Attempting to hide chat window...")
            self.chat_window.hide()

    def set_auto_translate(self, enabled):
        if enabled:
            if not self.last_translation_mode:
                QMessageBox.warning(self.control_panel, "Chưa có vùng dịch", "Vui lòng dịch một vùng chọn hoặc toàn màn hình ít nhất một lần trước khi bật Dịch định kỳ.")
                self.control_panel.auto_translate_checkbox.setChecked(False)
                return

            if self.subtitle_mode_enabled:
                self.control_panel.subtitle_mode_checkbox.setChecked(False)

        self.auto_translate_enabled = enabled
        if enabled and self.last_translation_mode:
            self.countdown_value = self.translation_interval // 1000
            self.auto_translate_timer.start(self.translation_interval)
            self.countdown_timer.start(1000) # Tick every second
            self.trigger_auto_translation() # Start immediately
        else:
            self.auto_translate_timer.stop()
            self.countdown_timer.stop()
            self.control_panel.update_bubble_text("V") # Reset bubble

    def set_subtitle_mode(self, enabled):
        if enabled:
            # Check for a valid selection area before starting
            geom = self.selection_window.geometry()
            if geom.width() <= 10 or geom.height() <= 10:
                QMessageBox.warning(self.control_panel, "Vùng chọn không hợp lệ", "Vui lòng chọn một vùng dịch bằng nút 'Vùng chọn mới' trước khi bật Chế độ Phụ đề.")
                self.control_panel.subtitle_mode_checkbox.setChecked(False)
                return

            if self.auto_translate_enabled:
                self.control_panel.auto_translate_checkbox.setChecked(False)
            
            self.subtitle_mode_enabled = True
            self.display_window.set_subtitle_mode(True)
            self.selection_window.hide()
            self.start_subtitle_processor()
        else:
            self.subtitle_mode_enabled = False
            self.display_window.set_subtitle_mode(False)
            self.stop_subtitle_processor()
            self.selection_window.show()

    def start_subtitle_processor(self):
        if self.subtitle_processor and self.subtitle_processor.isRunning():
            logging.warning("Subtitle processor is already running.")
            return

        logging.info("Starting subtitle mode.")
        self.subtitle_processor = SubtitleProcessor(
            cache_dir=self.cache_dir,
            ocr_engine=self.ocr_engine,
            translator=self.translator,
            config=self.config
        )
        self.subtitle_processor.new_translation.connect(self.handle_subtitle_results)
        self.subtitle_processor.no_text_detected.connect(self.display_window.clear)
        self.subtitle_processor.start()

        # Use interval from the UI, but with a minimum cap for performance
        capture_interval_ms = max(200, int(self.control_panel.interval_spinbox.value() * 1000))
        self.subtitle_capture_timer.timeout.connect(self.capture_for_subtitle)
        self.subtitle_capture_timer.start(capture_interval_ms)

    def stop_subtitle_processor(self):
        logging.info("Stopping subtitle mode.")
        self.subtitle_capture_timer.stop()
        if self.subtitle_processor:
            self.subtitle_processor.stop()
            self.subtitle_processor.wait() # Wait for thread to finish cleanly
            self.subtitle_processor = None
        
        # Clean up any remaining images in the cache
        logging.info("Cleaning up cache directory.")
        try:
            for f in os.listdir(self.cache_dir):
                if f.endswith(".png"):
                    os.remove(os.path.join(self.cache_dir, f))
        except Exception as e:
            logging.error(f"Error cleaning cache directory: {e}")

    def capture_for_subtitle(self):
        geom = self.selection_window.geometry()
        if geom.width() <= 10 or geom.height() <= 10:
            logging.warning("Skipping subtitle capture due to invalid selection region.")
            return

        # Hide display window to prevent OCR loop
        self.display_window.hide()
        QApplication.processEvents() # Allow UI to update

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, geom.x(), geom.y(), geom.width(), geom.height())
        
        # Show the window again immediately after capture
        self.display_window.show()

        # Save with a timestamp to ensure order
        timestamp = int(time.time() * 1000)
        image_path = os.path.join(self.cache_dir, f"capture_{timestamp}.png")
        screenshot.save(image_path, "png")

    def set_tts_enabled(self, enabled):
        self.tts_enabled = enabled
        self.config["tts_enabled"] = enabled
        # No need to save the whole config file again, it's saved in handle_config_change

    def handle_subtitle_results(self, results):
        # This is called from the SubtitleProcessor thread
        geom = self.selection_window.geometry()
        self.display_window.setGeometry(geom)
        self.display_window.set_results(results)
        self.display_window.show()
        self.display_window.raise_()
        self.control_panel.raise_()

        # Also add results to chat history if it's visible
        if self.chat_window.isVisible() and results:
            # We only add the first result to avoid spamming the history
            # in case of multiple text boxes in the subtitle region.
            res = results[0]
            self.chat_window.add_message(res['original'], res['translated'])

    def update_countdown(self):
        if self.countdown_value > 0:
            self.control_panel.update_bubble_text(str(self.countdown_value))
            self.countdown_value -= 1
        else:
            # This case handles the last second before the new translation starts
            self.control_panel.update_bubble_text("...")

    def set_translation_interval(self, interval_seconds):
        self.translation_interval = int(interval_seconds * 1000)
        if self.auto_translate_timer.isActive():
            self.auto_translate_timer.start(self.translation_interval)

    def trigger_auto_translation(self):
        if self.is_translating:
            logging.warning("Skipping auto-translate tick, previous translation still running.")
            return
        
        # Reset countdown for the next cycle
        self.countdown_value = self.translation_interval // 1000
        
        logging.info("Auto-translation triggered.")
        if self.last_translation_mode == 'region':
            self.translate_selection_region()
        elif self.last_translation_mode == 'fullscreen':
            self.translate_fullscreen()

    def show_selection_window(self):
        self.selection_window.show()
        self.selection_window.activateWindow()
        self.selection_window.raise_()

    def start_snip_mode(self):
        logging.info("Starting snip mode.")
        self.display_window.clear() # Clear previous results immediately
        self.snip_window.show()
        self.snip_window.activateWindow()
        self.snip_window.raise_()

    def translate_snip_region(self, geometry):
        self.last_translation_mode = 'snip'
        logging.info("Snip & Translate triggered.")
        self.start_translation(geometry)

    def translate_selection_region(self):
        # The window can be hidden, that's fine. We just need its geometry.
        # The check for a valid geometry (e.g., non-zero size) can be implicit
        # as grabWindow on a zero-size rect will just produce a tiny image.
        
        self.last_translation_mode = 'region'
        logging.info("Persistent region translation triggered.")
        geom = self.selection_window.geometry()
        self.selection_window.hide()
        self.start_translation(geom)

    def translate_fullscreen(self):
        self.last_translation_mode = 'fullscreen'
        logging.info("Fullscreen translation triggered.")
        screen_rect = QApplication.primaryScreen().geometry()
        self.start_translation(screen_rect)

    def start_translation(self, geometry):
        if self.is_translating:
            logging.warning("Translation already in progress. Skipping new request.")
            return
        
        self.is_translating = True
        self.display_window.clear()
        
        self.control_panel.hide()
        QApplication.processEvents()

        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0, geometry.x(), geometry.y(), geometry.width(), geometry.height())
        
        self.control_panel.show()

        image_path = "screenshot.png"
        screenshot.save(image_path, "png")

        worker_thread = QThread()
        worker = Worker(image_path, self.ocr_engine, self.translator, self.config)
        worker.moveToThread(worker_thread)

        # Add to list to prevent garbage collection
        self.running_workers.append((worker, worker_thread))

        worker.finished.connect(lambda results: self.handle_results(results, geometry))
        worker_thread.started.connect(worker.run)
        
        # Clean up thread and worker objects after they are finished
        worker.finished.connect(worker.deleteLater)
        worker_thread.finished.connect(worker_thread.deleteLater)
        worker_thread.finished.connect(lambda: self.cleanup_worker(worker, worker_thread))
        
        worker_thread.start()

    def cleanup_worker(self, worker, worker_thread):
        logging.info("Cleaning up a finished worker.")
        try:
            self.running_workers.remove((worker, worker_thread))
        except ValueError:
            logging.warning("Worker was not found in the running list for cleanup.")

    def cleanup_worker_thread(self):
        # This method is no longer necessary with the new local-variable approach for workers.
        # Kept for reference or future use if needed.
        pass

    def handle_results(self, results, geometry):
        logging.info(f"Displaying {len(results)} results.")
        
        # The results from OCR are relative to the screenshot.
        # We need to set the DisplayWindow to the same geometry as the screenshot
        # so the coordinates match up.
        self.display_window.setGeometry(geometry)
        self.display_window.set_results(results) # Pass the full results dictionary
        self.display_window.show()
        self.display_window.raise_()
        self.control_panel.raise_()

        # Show the selection window again only if it was a persistent region translation
        if self.last_translation_mode == 'region':
            self.selection_window.show()

        # If the chat window is visible, add all results to it
        if self.chat_window.isVisible():
            for res in results:
                self.chat_window.add_message(res['original'], res['translated'])

        # Speak the translated text if enabled and not in fullscreen mode
        if self.tts_enabled and self.last_translation_mode != 'fullscreen' and results:
            full_text = " ".join([res['translated'] for res in results])
            lang_code = self.config.get("language", "en")
            self.tts_manager.speak(full_text, lang_code)

        self.is_translating = False

    def run(self):
        self.control_panel.show()
        sys.exit(self.app.exec_())

def main():
    app = QApplication(sys.argv)
    controller = AppController(app)
    controller.run()

if __name__ == '__main__':
    main()
