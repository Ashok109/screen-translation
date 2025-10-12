import logging
import concurrent.futures
import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from ocr.easy_ocr import EasyOcr
from translator.base_translator import BaseTranslator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Worker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, image_path: str, ocr_engine: EasyOcr, translator: BaseTranslator, config: dict):
        super().__init__()
        self.image_path = image_path
        self.ocr_engine = ocr_engine
        self.translator = translator
        self.config = config

    def preprocess_image_for_ocr(self, image_path):
        """
        Applies user-configured preprocessing steps to an image to improve OCR accuracy.
        """
        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                logging.error(f"Failed to read image from path: {image_path}")
                return None

            processed_img = img

            # 1. Upscale the image if enabled
            if self.config.get("upscale_enabled", False):
                scale_factor = self.config.get("upscale_factor", 1.0)
                if scale_factor > 1.0:
                    width = int(processed_img.shape[1] * scale_factor)
                    height = int(processed_img.shape[0] * scale_factor)
                    processed_img = cv2.resize(processed_img, (width, height), interpolation=cv2.INTER_CUBIC)
                    logging.info(f"Image upscaled by factor of {scale_factor}.")

            # 2. Binarize the image if enabled
            if self.config.get("binarize_enabled", False):
                # Using adaptive thresholding can be good for varied lighting
                processed_img = cv2.adaptiveThreshold(processed_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                      cv2.THRESH_BINARY, 11, 2)
                logging.info("Image binarized.")

            logging.info("Image preprocessing complete.")
            return processed_img
        except Exception as e:
            logging.error(f"Error during image preprocessing: {e}")
            return None

    def run(self):
        logging.info("Worker thread started.")
        try:
            image_to_process = self.image_path
            
            # Check if preprocessing is enabled
            if self.config.get("preprocess_enabled", False):
                preprocessed_image = self.preprocess_image_for_ocr(self.image_path)
                if preprocessed_image is not None:
                    image_to_process = preprocessed_image
                else:
                    logging.warning("Preprocessing failed. Falling back to original image.")
            
            # Enable paragraph mode to group lines of text
            ocr_results = self.ocr_engine.recognize(image_to_process, paragraph=True)
            logging.info(f"OCR found {len(ocr_results)} paragraphs/text boxes.")

            if not ocr_results:
                self.finished.emit([])
                logging.info("Worker thread finished: No text found.")
                return

            # When paragraph=True, the result is a list of (bounding_box, text)
            # The bounding box is a list of 4 points [top-left, top-right, bottom-right, bottom-left]
            
            # Parallel translation
            boxes = [box for box, text in ocr_results]
            texts_to_translate = [text for box, text in ocr_results]
            
            translated_texts = ["" for _ in texts_to_translate]
            
            # Use a ThreadPoolExecutor to parallelize translation
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Use the translator instance to translate a batch of one text
                future_to_index = {executor.submit(self.translator.translate_batch, [text], dest_lang='vi'): i for i, text in enumerate(texts_to_translate)}
                
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        # result is a list with one element
                        translated_text_list = future.result()
                        if translated_text_list:
                            translated_texts[index] = translated_text_list[0]
                    except Exception as exc:
                        logging.error(f'Text at index {index} generated an exception: {exc}')
                        translated_texts[index] = "Translation Error"

            translation_results = list(zip(boxes, translated_texts))
            
            logging.info("Parallel paragraph translation complete.")
            self.finished.emit(translation_results)
        except Exception as e:
            logging.error(f"Error in worker thread: {e}")
            self.finished.emit([]) # Emit empty list on error
        logging.info("Worker thread finished.")
