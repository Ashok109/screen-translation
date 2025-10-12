from abc import ABC, abstractmethod

class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, text, dest_lang='vi'):
        """
        Translate a single string of text.

        :param text: The text to translate.
        :param dest_lang: The destination language.
        :return: The translated text as a string.
        """
        pass

    @abstractmethod
    def translate_batch(self, texts, dest_lang='vi'):
        """
        Translate a list of texts.

        :param texts: A list of strings to translate.
        :param dest_lang: The destination language.
        :return: A list of translated strings.
        """
        pass
