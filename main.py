import sys
import logging
import json
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread, QRect, Qt, QTimer

from ui.selection_window import SelectionWindow
from ui.display_window import DisplayWindow
from ui.snip_window import SnipWindow
from ui.control_panel import ControlPanel
from ui.translator import Translator as UiTranslator
from ocr.easy_ocr import EasyOcr
from core.hotkey_manager import HotkeyManager
from core.worker import Worker
from translator.google_translate import GoogleTranslate
from translator.open_router import OpenRouterTranslator
from translator.gemini import GeminiTranslator
from translator.custom_api import CustomApiTranslator

class AppController:
    def __init__(self, app):
        self.app = app
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

        # Create UI components
        self.control_panel = ControlPanel(self.ui_translator)
        self.selection_window = SelectionWindow()
        self.display_window = DisplayWindow()
        self.snip_window = SnipWindow() # Create once and reuse

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
                "fullscreen_translate": "<alt>+<ctrl>+f", "clear_results": "-"
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
            "language": "en"
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
        self.ocr_engine = EasyOcr(languages=ocr_langs)
        print(f"OCR engine loaded for languages: {ocr_langs}")

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

    def setup_connections(self):
        # Control Panel connections
        self.control_panel.new_selection_button.clicked.connect(self.show_selection_window)
        self.control_panel.translate_fullscreen_requested.connect(self.translate_fullscreen)
        self.control_panel.clear_requested.connect(self.display_window.clear)
        self.control_panel.font_size_changed.connect(self.display_window.set_font_size)
        self.control_panel.close_requested.connect(self.app.quit)
        self.snip_window.region_selected.connect(self.start_translation)

        # Auto-translation connections
        self.control_panel.auto_translate_toggled.connect(self.set_auto_translate)
        self.control_panel.interval_changed.connect(self.set_translation_interval)
        self.auto_translate_timer.timeout.connect(self.trigger_auto_translation)
        self.countdown_timer.timeout.connect(self.update_countdown)

        # Config change connection
        self.control_panel.config_changed.connect(self.handle_config_change)

        # Worker thread cleanup
        self.app.aboutToQuit.connect(self.cleanup_worker_thread)

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

        self.hotkey_thread.start()

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

        QMessageBox.information(self.control_panel, "Success",
                                "Configuration has been saved and applied.")

    def set_auto_translate(self, enabled):
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
        self.snip_window.show()
        self.snip_window.activateWindow()
        self.snip_window.raise_()

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
        self.display_window.set_results(results)
        self.display_window.show()
        self.display_window.raise_()
        self.control_panel.raise_()
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
