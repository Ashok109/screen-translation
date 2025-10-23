import logging
import json
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard

class HotkeyManager(QObject):
    snip_translate_hotkey = pyqtSignal()
    region_translate_hotkey = pyqtSignal()
    fullscreen_translate_hotkey = pyqtSignal()
    clear_results_hotkey = pyqtSignal()
    toggle_subtitle_mode_hotkey = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listener = None
        self.config_file = 'config.json'
        self.hotkeys = self.load_hotkeys()
        
        # Define callbacks for each hotkey
        self.callbacks = {
            self.hotkeys['snip_translate']: self.snip_translate_hotkey.emit,
            self.hotkeys['region_translate']: self.region_translate_hotkey.emit,
            self.hotkeys['fullscreen_translate']: self.fullscreen_translate_hotkey.emit,
            self.hotkeys['clear_results']: self.clear_results_hotkey.emit,
            self.hotkeys['toggle_subtitle_mode']: self.toggle_subtitle_mode_hotkey.emit,
        }

    def get_default_hotkeys(self):
        return {
            "snip_translate": "<alt>+<ctrl>+t",
            "region_translate": "<alt>+<ctrl>+r",
            "fullscreen_translate": "<alt>+<ctrl>+f",
            "clear_results": "-",
            "toggle_subtitle_mode": "<alt>+<ctrl>+s"
        }

    def load_hotkeys(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('hotkeys', self.get_default_hotkeys())
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning(f"'{self.config_file}' not found or invalid. Creating with default hotkeys.")
            default_config = {"hotkeys": self.get_default_hotkeys()}
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config['hotkeys']

    def run(self):
        logging.info("Starting hotkey listener...")
        # Use pynput's built-in HotKey class for robust detection
        hotkeys = keyboard.GlobalHotKeys(self.callbacks)
        self.listener = hotkeys
        self.listener.start()
        logging.info("Hotkey listener started.")

    def stop(self):
        if self.listener:
            self.listener.stop()
            logging.info("Hotkey listener stopped.")
