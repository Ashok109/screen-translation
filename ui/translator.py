import json
import os

class Translator:
    def __init__(self, language='en'):
        self.language = language
        self.translations = self.load_translations()

    def load_translations(self):
        # Correctly locate the translations.json file relative to this script's location
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, 'translations.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return a default structure to prevent crashes if the file is missing/corrupt
            return {"en": {}, "vi": {}}

    def set_language(self, language):
        if language in self.translations:
            self.language = language
        else:
            self.language = 'en' # Default to English if language not found

    def get_string(self, key):
        # Get the string from the current language, fall back to English if not found
        return self.translations.get(self.language, {}).get(key, self.translations.get('en', {}).get(key, key))
