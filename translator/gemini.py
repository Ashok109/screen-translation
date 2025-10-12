import google.generativeai as genai
from .base_translator import BaseTranslator

class GeminiTranslator(BaseTranslator):
    DEFAULT_PROMPT = "Translate the following text to {dest_lang}. Only output the translated text directly without any introductory phrases.\n\n{text}"

    def __init__(self, api_key, model, use_custom_prompt=False, custom_prompt=""):
        if not api_key:
            raise ValueError("Gemini API key is required.")
        if not model:
            raise ValueError("Gemini model name is required.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.use_custom_prompt = use_custom_prompt
        self.custom_prompt = custom_prompt

    def _translate_text_chunk(self, text_chunk, dest_lang='vi'):
        if not text_chunk.strip():
            return ""
        
        if self.use_custom_prompt and self.custom_prompt:
            prompt = self.custom_prompt.format(dest_lang=dest_lang, text=text_chunk)
        else:
            prompt = self.DEFAULT_PROMPT.format(dest_lang=dest_lang, text=text_chunk)

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error during Gemini translation: {e}")
            return "Translation Error"

    def translate(self, text, dest_lang='vi'):
        return self._translate_text_chunk(text, dest_lang)

    def translate_batch(self, texts, dest_lang='vi'):
        # Similar to OpenRouter, we rely on the Worker's parallel execution
        # for handling multiple texts efficiently.
        return [self.translate(text, dest_lang) for text in texts]
