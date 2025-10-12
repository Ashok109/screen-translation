from deep_translator import GoogleTranslator
from .base_translator import BaseTranslator

class GoogleTranslate(BaseTranslator):
    def __init__(self, **kwargs):
        # The GoogleTranslator from deep_translator doesn't need an API key
        pass

    def translate(self, text, dest_lang='vi'):
        if not text:
            return ""
        try:
            return GoogleTranslator(source='auto', target=dest_lang).translate(text)
        except Exception as e:
            print(f"Error during single Google translation: {e}")
            return "Translation Error"

    def translate_batch(self, texts, dest_lang='vi'):
        if not texts:
            return []
        try:
            translator = GoogleTranslator(source='auto', target=dest_lang)
            return translator.translate_batch(texts)
        except Exception as e:
            print(f"Error during batch Google translation: {e}")
            return ["Translation Error"] * len(texts)
