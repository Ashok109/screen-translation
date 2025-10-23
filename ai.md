# Screen Translator - Development Log & Technical Overview

## 1. Project Overview

This project is a powerful OCR and translation application for Windows, developed using Python and PyQt5. It allows users to translate text directly from their screen in real-time. The application has evolved significantly to include multiple translation modes, support for various services, and numerous user experience improvements.

## 2. Core Architecture

The application's architecture is designed to be modular and responsive, separating the UI from heavy processing tasks.

- **`main.py` (AppController):** The central orchestrator. It initializes all components, manages application state (like auto-translation modes), handles configuration loading/saving, and connects signals from the UI to the appropriate backend logic.
- **`ui/` Modules:** All PyQt5 components responsible for the user interface.
    - `control_panel.py`: The main control hub for all user settings and actions.
    - `display_window.py`: The transparent overlay that renders translation results.
    - `selection_window.py`: The draggable/resizable frame for defining a persistent translation region.
    - `snip_window.py`: A temporary overlay for the "Snip & Translate" feature.
- **`core/` Modules:** Backend logic and processing threads.
    - `worker.py`: A `QThread` that handles the primary OCR and translation workflow for single-shot translations (region, fullscreen, snip).
    - `subtitle_processor.py`: A specialized `QThread` for the continuous subtitle translation mode. It manages a queue of screenshots to provide a smooth, real-time experience.
    - `hotkey_manager.py`: Runs in a separate thread to listen for global hotkeys using `pynput`.
    - `tts_manager.py`: Manages Text-to-Speech functionality in a non-blocking thread.
- **`ocr/` and `translator/` Modules:** Wrappers for external OCR and translation services, providing a consistent interface for the core logic.

## 3. Recent Changes & Features (Development Log)

This section details the implementation of recent features and bug fixes.

### 3.1. Text-to-Speech (TTS) Implementation
- **Goal:** Read the translated text aloud.
- **Implementation:**
    - Integrated `gTTS` (Google Text-to-Speech) for high-quality voice and `playsound` for audio playback.
    - Created `core/tts_manager.py` to handle TTS operations in a separate `threading.Thread`. This prevents the main UI from freezing while the audio is being generated and played.
    - Added a checkbox to `ui/control_panel.py` and connected its `toggled` signal to `main.py` to enable/disable the feature.
    - Logic was added in `main.py`'s `handle_results` to call `tts_manager.speak()` only if TTS is enabled and the translation mode is not 'fullscreen' (to avoid reading the entire screen).

### 3.2. Subtitle Mode Enhancements
- **Goal:** Reduce flickering and automatically clear the overlay when no text is present.
- **Flicker Reduction:**
    - **Problem:** The overlay would flash blankly between subtitle updates because it was cleared before new text was rendered.
    - **Solution:** Modified `ui/display_window.py`. The `set_results` method now checks if it's in subtitle mode. If it is, and if the incoming result list is empty, it simply `return`s, preserving the last displayed text. This turns a "blank" flicker into a "static" frame, which is much less jarring.
- **Auto-Clear on No Text:**
    - **Problem:** The last translated subtitle would remain on screen indefinitely even after dialogue ended.
    - **Solution:**
        1.  Added a new `no_text_detected = pyqtSignal()` to `core/subtitle_processor.py`.
        2.  In the processor's `run` loop, if the OCR result is empty, this signal is emitted.
        3.  In `main.py`, this new signal is connected directly to the `self.display_window.clear` method. This ensures the overlay is cleared explicitly and only when the OCR confirms no text is present.

### 3.3. OCR Language Filtering
- **Goal:** Prevent translating nonsensical text when the wrong OCR language is configured.
- **Implementation:**
    - Integrated the `langdetect` library.
    - In `core/worker.py`, after OCR is performed, the code now iterates through the results.
    - For each text block, it uses `langdetect.detect()` (within a `try...except` block to handle errors on short/invalid strings).
    - It checks if the detected language is present in the user's configured `ocr_languages` list.
    - Only text blocks that pass this language check are added to the list for translation, effectively filtering out garbage results.

### 3.4. UI/UX Improvements
- **Goal:** Make OCR language selection more user-friendly.
- **Implementation:**
    - In `ui/control_panel.py`, the `QLineEdit` for OCR languages was replaced with a more complex layout.
    - A `QComboBox` was added with presets for common languages and language pairs (e.g., "English + Japanese").
    - A `QCheckBox` ("Custom OCR Languages") was added.
    - Logic was implemented to toggle the visibility and enabled state: when unchecked, the user selects from the preset `QComboBox`; when checked, the `QComboBox` is disabled and the original `QLineEdit` appears for custom input.
    - The `get_config_data` and `set_config_data` methods were updated to handle this conditional logic, providing a seamless user experience.

### 3.5. PyInstaller Packaging & Portability
- **Goal:** Create a single, portable `.exe` file for easy distribution.
- **Implementation:**
    - **PyInstaller Setup:** Added `pyinstaller` to `requirements.txt` and created `build.spec` and `build.bat` files.
    - **Portability Challenge:** By default, EasyOCR downloads models to a system-wide user directory (e.g., `~/.EasyOCR`). This is not portable.
    - **Solution:**
        1.  Modified `main.py` to create a `model_dump` directory in the same folder as the executable.
        2.  Researched the `easyocr.Reader` class constructor to find the correct parameter for specifying a model directory.
        3.  **Troubleshooting:** Initially failed with `TypeError` for `model_dir` and `model_storage_directory`. The final investigation of the library's source code revealed the correct parameter was indeed `model_storage_directory`, but the custom wrapper in `ocr/easy_ocr.py` was not built to accept it.
        4.  **Final Fix:** Modified the `__init__` method of the `EasyOcr` class in `ocr/easy_ocr.py` to accept the `model_storage_directory` argument and pass it down to the underlying `easyocr.Reader`. This fixed the `TypeError` and enabled fully portable model storage.
    - The `build.spec` file was configured to be simple, only including necessary data files like `translations.json` and letting the application download models at runtime.
