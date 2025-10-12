# AI-Powered Screen Translator Project

## 1. Project Overview

This project is a powerful OCR and translation application for Windows, developed using Python and PyQt5. It allows users to translate text directly from their screen in real-time. The primary use case is for translating text from games, images, or any content that cannot be easily copied.

The application features a movable and resizable overlay window that the user places over the text they wish to translate. A separate control panel allows the user to trigger the translation and close the application.

## 2. Features

- **Live Screen Translation:** Translate text by simply placing an overlay window over it.
- **Resizable and Movable Overlay:** The translation window can be freely moved and resized to fit any text area.
- **GPU Acceleration:** Utilizes the user's GPU (if a CUDA-enabled PyTorch is installed) for fast OCR processing, preventing the UI from freezing.
- **Accurate Overlay Rendering:** The translated text is rendered directly on top of the original text, preserving the layout and position.
- **Multi-threaded Processing:** OCR and translation tasks are run in a separate thread to keep the main UI responsive at all times.
- **Simple Controls:** A separate, small control panel provides simple "Translate" and "Close" buttons.

## 3. Project Structure

The project is organized into several modules to separate concerns:

```
dichmanhinh/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── ai.md                   # This documentation file
|
├── ui/                     # User Interface modules (PyQt5)
│   ├── overlay_window.py   # The main resizable translation window
│   └── control_panel.py    # The small window with Translate/Close buttons
|
├── ocr/                    # Optical Character Recognition modules
│   ├── base_ocr.py         # Abstract base class for OCR engines
│   └── easy_ocr.py         # EasyOCR implementation
|
├── translator/             # Translation modules
│   └── google_translate.py # Google Translate implementation
|
├── core/                   # Core application logic
│   └── worker.py           # QThread worker for handling heavy tasks (OCR/translation)
|
└── assets/                 # For static assets like icons (currently unused)
```

## 4. Core Components

- **`ui/overlay_window.py`:** This is the main visual component. It's a frameless, transparent window that can be moved and resized. Its `paintEvent` is responsible for rendering the translated text results over a dark background, preserving the position of the original text.
- **`ui/control_panel.py`:** A simple widget with two buttons. It emits signals (`translate_requested`, `close_requested`) that are connected to the main application logic.
- **`core/worker.py`:** A `QThread` subclass that performs the heavy lifting. When a translation is requested, a `Worker` instance is created and moved to a new thread. It takes a screenshot, runs it through the OCR engine, translates the results, and emits a `finished` signal with the translated data.
- **`ocr/easy_ocr.py`:** A wrapper for the `easyocr` library. It's configured to run on the GPU if possible and to recognize individual text lines rather than paragraphs for more accurate rendering.

## 5. Workflow

1.  The user launches the application via `main.py`.
2.  `main.py` creates and displays both the `OverlayWindow` and the `ControlPanel`.
3.  Signals from the `ControlPanel` are connected to slots in the `OverlayWindow` and the main `QApplication`.
4.  The user moves and resizes the `OverlayWindow` to cover the desired text.
5.  The user clicks the "Translate" button on the `ControlPanel`.
6.  The `ControlPanel` emits the `translate_requested` signal.
7.  The `OverlayWindow`'s `translate` slot is triggered.
8.  The `OverlayWindow` takes a screenshot of the area it covers.
9.  It creates a `Worker` thread, passing the path to the screenshot.
10. The `Worker` thread starts, runs EasyOCR on the image, and translates each recognized piece of text.
11. Once finished, the `Worker` emits a `finished` signal containing a list of `(bounding_box, translated_text)` tuples.
12. The `OverlayWindow`'s `update_translation` slot receives this data and stores it.
13. It calls `update()`, which triggers the `paintEvent`.
14. The `paintEvent` draws a background over the original text and then draws the new translated text at the correct coordinates.

## 6. Setup and Installation

1.  **Clone the repository.**
2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/Scripts/activate
    ```
3.  **Install dependencies:**
    - The project uses `PyQt5`, `easyocr`, and `googletrans`. `easyocr` requires a specific version of PyTorch for GPU acceleration.
4.  **Install PyTorch with GPU support (IMPORTANT):**
    - First, uninstall any existing CPU-only versions of PyTorch:
      ```bash
      pip uninstall torch torchvision -y
      ```
    - Then, install the version compatible with your NVIDIA driver's CUDA version. For CUDA 12.1 (common for modern GPUs), use the following command:
      ```bash
      pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
      ```
5.  **Install the remaining dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 7. How to Run

After completing the setup, run the application with:

```bash
python main.py
