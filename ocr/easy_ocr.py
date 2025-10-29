import easyocr
from ocr.base_ocr import BaseOcr

class EasyOcr(BaseOcr):
    def __init__(self, languages=['en'], model_storage_directory=None):
        # EasyOCR will automatically use GPU if a CUDA-enabled PyTorch is installed.
        self.reader = easyocr.Reader(languages, model_storage_directory=model_storage_directory)

    def recognize(self, image_input, detail=1, paragraph=False):
        """
        Recognize text from an image file or image object using EasyOCR.

        :param image_input: Path to the image file (str) or an image object (e.g., numpy array).
        :param detail: 0 for just text, 1 for text and bounding boxes.
        :param paragraph: Combine text into paragraphs.
        :return: The recognized text as a string or a list of results.
        """
        try:
            result = self.reader.readtext(image_input, detail=detail, paragraph=paragraph)
            if detail == 0:
                return " ".join(result)
            return result
        except Exception as e:
            print(f"Error during EasyOCR: {e}")
            return []
