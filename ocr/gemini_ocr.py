import google.generativeai as genai
from PIL import Image
from ocr.base_ocr import BaseOcr
import os

class GeminiOcr(BaseOcr):
    def __init__(self, api_key=None, model_name='gemini-1.5-flash'):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def recognize(self, image_input, detail=0, paragraph=False):
        """
        Recognize text from an image file or image object using Gemini Pro Vision.

        :param image_input: Path to the image file (str) or an image object (e.g., numpy array).
        :param detail: (Not used by Gemini) Included for compatibility with BaseOcr.
        :param paragraph: (Not used by Gemini) Included for compatibility with BaseOcr.
        :return: The recognized text as a string.
        """
        try:
            if isinstance(image_input, str):
                img = Image.open(image_input)
            else:
                # Assuming it's a numpy array (from cv2)
                img = Image.fromarray(image_input)

            response = self.model.generate_content(["Extract all text from this image.", img])
            
            # Check if the response has parts and text
            if response.parts and response.text.strip():
                text = response.text.strip()
                width, height = img.size
                # Create a bounding box covering the entire image
                full_box = [[0, 0], [width, 0], [width, height], [0, height]]
                # Return in the same format as EasyOCR: a list of (box, text) tuples
                return [(full_box, text)]
            else:
                # Handle cases where the response might be empty or blocked
                print("Gemini OCR: No text found or response was blocked.")
                return []

        except Exception as e:
            print(f"Error during Gemini OCR: {e}")
            return ""
