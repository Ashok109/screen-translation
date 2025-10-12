import os
from openai import OpenAI
from .base_translator import BaseTranslator

class OpenRouterTranslator(BaseTranslator):
    DEFAULT_PROMPT = "You are a translation assistant. Translate the following text to {dest_lang}. Only output the translated text directly without any introductory phrases."

    def __init__(self, api_key, model, use_custom_prompt=False, custom_prompt=""):
        if not api_key:
            raise ValueError("OpenRouter API key is required.")
        if not model:
            raise ValueError("OpenRouter model name is required.")
            
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        self.use_custom_prompt = use_custom_prompt
        self.custom_prompt = custom_prompt

    def _translate_text_chunk(self, text_chunk, dest_lang='vi'):
        if not text_chunk.strip():
            return ""
        
        if self.use_custom_prompt and self.custom_prompt:
            system_prompt = self.custom_prompt.format(dest_lang=dest_lang, text=text_chunk)
            user_content = text_chunk # In custom mode, the user might just want the text in the user message
        else:
            system_prompt = self.DEFAULT_PROMPT.format(dest_lang=dest_lang)
            user_content = text_chunk

        # If the custom prompt already includes the text, the user message can be simplified.
        if '{text}' in self.custom_prompt:
             messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": system_prompt},
            ]
        else:
             messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error during OpenRouter translation: {e}")
            return "Translation Error"

    def translate(self, text, dest_lang='vi'):
        return self._translate_text_chunk(text, dest_lang)

    def translate_batch(self, texts, dest_lang='vi'):
        # For AI models, it's often better to join texts into a single prompt
        # with separators to maintain context, rather than many small API calls.
        # However, to keep the parallel processing simple, we'll translate one by one here.
        # The parallel execution is handled by the Worker.
        return [self.translate(text, dest_lang) for text in texts]
