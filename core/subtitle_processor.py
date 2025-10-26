import logging
import os
import time
import glob
import re
from fuzzywuzzy import fuzz
from PyQt5.QtCore import QThread, pyqtSignal
from ocr.easy_ocr import EasyOcr
from translator.base_translator import BaseTranslator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SubtitleProcessor(QThread):
    """
    A dedicated worker thread to process screenshots for subtitle translation.
    It watches a directory for new images, processes them sequentially,
    and emits translation results.
    """
    new_translation = pyqtSignal(list)
    no_text_detected = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, cache_dir: str, ocr_engine: EasyOcr, translator: BaseTranslator, config: dict):
        super().__init__()
        self.cache_dir = cache_dir
        self.ocr_engine = ocr_engine
        self.translator = translator
        self.config = config
        self._is_running = False
        self.last_recognized_text = ""

    def is_meaningful(self, text: str) -> bool:
        """
        A simple filter to check if the OCR text is likely to be meaningful.
        """
        # 1. Check for minimum length
        if len(text.strip()) < 2:
            return False
        
        # 2. Check for a decent ratio of alphanumeric characters
        alphanumeric_chars = sum(1 for char in text if char.isalnum())
        if alphanumeric_chars / len(text) < 0.5:
            return False
            
        return True

    def run(self):
        logging.info("Subtitle Processor thread started.")
        self._is_running = True
        
        while self._is_running:
            # Find the oldest image file to process
            image_files = glob.glob(os.path.join(self.cache_dir, '*.png'))
            if not image_files:
                time.sleep(0.1) # Wait a bit if no files are present
                continue

            oldest_file = min(image_files, key=os.path.getctime)
            
            try:
                # 1. Perform OCR
                ocr_results = self.ocr_engine.recognize(oldest_file, paragraph=True)
                
                # 2. If OCR is empty, emit signal to clear display, then skip and delete
                if not ocr_results:
                    logging.info(f"No text found in {os.path.basename(oldest_file)}, clearing display.")
                    self.no_text_detected.emit()
                    os.remove(oldest_file)
                    continue

                logging.info(f"Found {len(ocr_results)} text blocks in {os.path.basename(oldest_file)}.")
                
                # 3. Filter and translate meaningful text
                meaningful_results = []
                texts_to_translate = []
                
                # Combine all recognized text into one block for comparison
                current_text_block = " ".join([text for box, text in ocr_results if self.is_meaningful(text)])

                if not current_text_block:
                    logging.info("No meaningful text found after filtering.")
                    os.remove(oldest_file)
                    continue

                # Avoid re-translating similar subtitles using fuzzy matching
                similarity_ratio = fuzz.ratio(current_text_block, self.last_recognized_text)
                if similarity_ratio > 85:
                    logging.info(f"Skipping similar subtitle (Similarity: {similarity_ratio}%)")
                    os.remove(oldest_file)
                    continue
                
                self.last_recognized_text = current_text_block

                # Prepare for translation
                for box, text in ocr_results:
                    if self.is_meaningful(text):
                        meaningful_results.append((box, text))
                        texts_to_translate.append(text)

                if not texts_to_translate:
                    logging.info("No text left to translate after filtering.")
                    os.remove(oldest_file)
                    continue
                
                dest_lang = self.config.get("dest_lang", "vi")
                translated_texts = self.translator.translate_batch(texts_to_translate, dest_lang=dest_lang)

                # 4. Prepare results for display
                display_results = []
                for i, (box, original_text) in enumerate(meaningful_results):
                    display_results.append({
                        "box": box,
                        "original": original_text,
                        "translated": translated_texts[i],
                        "bg_color": (0, 0, 0),
                        "fg_color": (255, 255, 255)
                    })
                
                # 5. Emit the results
                self.new_translation.emit(display_results)

            except Exception as e:
                logging.error(f"Error processing {os.path.basename(oldest_file)}: {e}")
            finally:
                # 6. Clean up the processed file
                if os.path.exists(oldest_file):
                    os.remove(oldest_file)

        logging.info("Subtitle Processor thread finished.")
        self.finished.emit()

    def stop(self):
        logging.info("Stopping Subtitle Processor thread...")
        self._is_running = False
