import logging
import concurrent.futures
from langdetect import detect, LangDetectException
import cv2
import numpy as np
from sklearn.cluster import KMeans
from PyQt5.QtCore import QThread, pyqtSignal
from ocr.easy_ocr import EasyOcr
from translator.base_translator import BaseTranslator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Worker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, image_path: str, ocr_engine: EasyOcr, translator: BaseTranslator, config: dict):
        super().__init__()
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
        self.image_path = image_path # Keep for preprocessing if needed
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

            if self.config.get("upscale_enabled", False):
                scale_factor = self.config.get("upscale_factor", 1.0)
                if scale_factor > 1.0:
                    width = int(processed_img.shape[1] * scale_factor)
                    height = int(processed_img.shape[0] * scale_factor)
                    processed_img = cv2.resize(processed_img, (width, height), interpolation=cv2.INTER_CUBIC)

            if self.config.get("binarize_enabled", False):
                processed_img = cv2.adaptiveThreshold(processed_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                      cv2.THRESH_BINARY, 11, 2)

            return processed_img
        except Exception as e:
            logging.error(f"Error during image preprocessing: {e}")
            return None

    def analyze_colors(self, box):
        """Analyzes colors within a bounding box to find background and foreground colors."""
        try:
            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]
            x_min, x_max = int(min(x_coords)), int(max(x_coords))
            y_min, y_max = int(min(y_coords)), int(max(y_coords))

            cropped_image = self.image[y_min:y_max, x_min:x_max]
            if cropped_image.size == 0:
                return (0, 0, 0), (255, 255, 255)

            pixels = cropped_image.reshape(-1, 3)
            
            # Use a smaller sample for performance if the area is large
            if len(pixels) > 5000:
                pixels = pixels[np.random.choice(len(pixels), 5000, replace=False)]

            kmeans = KMeans(n_clusters=2, n_init=3, random_state=0).fit(pixels)
            
            # Count pixels in each cluster
            counts = np.bincount(kmeans.labels_)
            
            # The smaller cluster is the foreground (text), the larger is the background
            if counts[0] > counts[1]:
                bg_bgr = kmeans.cluster_centers_[0]
                fg_bgr = kmeans.cluster_centers_[1]
            else:
                bg_bgr = kmeans.cluster_centers_[1]
                fg_bgr = kmeans.cluster_centers_[0]

            # Convert BGR to RGB for Qt
            bg_rgb = (int(bg_bgr[2]), int(bg_bgr[1]), int(bg_bgr[0]))
            fg_rgb = (int(fg_bgr[2]), int(fg_bgr[1]), int(fg_bgr[0]))

            return bg_rgb, fg_rgb
        except Exception as e:
            logging.error(f"Color analysis failed: {e}")
            return (0, 0, 0), (255, 255, 255)

    def run(self):
        logging.info("Worker thread started.")
        try:
            ocr_image_input = self.image_path
            if self.config.get("preprocess_enabled", False):
                 preprocessed_image = self.preprocess_image_for_ocr(self.image_path)
                 if preprocessed_image is not None:
                     ocr_image_input = preprocessed_image
            
            ocr_results = self.ocr_engine.recognize(ocr_image_input, paragraph=True)
            logging.info(f"OCR found {len(ocr_results)} paragraphs/text boxes.")

            if not ocr_results:
                self.finished.emit([])
                return

            valid_ocr_results = []
            if self.config.get("language_filter_enabled", True):
                # Mapping from langdetect codes to EasyOCR codes
                lang_map = {
                    'zh-cn': 'ch_sim',
                    'zh-tw': 'ch_tra',
                    'ja': 'ja',
                    'ko': 'ko',
                    'vi': 'vi',
                    'en': 'en',
                    # Add other common mappings as needed
                }

                allowed_langs = self.config.get('ocr_languages', ['en'])
                for box, text in ocr_results:
                    try:
                        # Detect language and check if it's in the allowed list
                        detected_lang = detect(text)
                        # Convert to EasyOCR code before checking
                        easyocr_lang_code = lang_map.get(detected_lang, detected_lang)
                        
                        if easyocr_lang_code in allowed_langs:
                            valid_ocr_results.append((box, text))
                        else:
                            logging.warning(f"Skipping text due to language mismatch. Detected: {detected_lang} (mapped to {easyocr_lang_code}), Allowed: {allowed_langs}. Text: '{text}'")
                    except LangDetectException:
                        # Could not detect language (e.g., too short, symbols only), skip it
                        logging.warning(f"Could not detect language for text: '{text}'. Skipping.")
                        continue
            else:
                # If the filter is disabled, just use all the results from OCR
                valid_ocr_results = ocr_results
            
            if not valid_ocr_results:
                self.finished.emit([])
                return

            boxes = [box for box, text in valid_ocr_results]
            texts_to_translate = [text for box, text in valid_ocr_results]
            
            translated_texts = ["" for _ in texts_to_translate]
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_index = {executor.submit(self.translator.translate_batch, [text], dest_lang='vi'): i for i, text in enumerate(texts_to_translate)}
                
                for future in concurrent.futures.as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        translated_text_list = future.result()
                        if translated_text_list:
                            translated_texts[index] = translated_text_list[0]
                    except Exception as exc:
                        logging.error(f'Text at index {index} generated an exception: {exc}')
                        translated_texts[index] = "Translation Error"

            translation_results = []
            for i in range(len(boxes)):
                box = boxes[i]
                bg_color, fg_color = self.analyze_colors(box)
                translation_results.append({
                    "box": box,
                    "original": texts_to_translate[i],
                    "translated": translated_texts[i],
                    "bg_color": bg_color,
                    "fg_color": fg_color
                })
            
            logging.info("Parallel paragraph translation and color analysis complete.")
            self.finished.emit(translation_results)
        except Exception as e:
            logging.error(f"Error in worker thread: {e}")
            self.finished.emit([])
        logging.info("Worker thread finished.")
