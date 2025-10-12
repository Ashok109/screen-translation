from abc import ABC, abstractmethod

class BaseOcr(ABC):
    @abstractmethod
    def recognize(self, image):
        """
        Recognize text from an image.

        :param image: The image to process. This can be a file path or an image object
                      depending on the implementation.
        :return: The recognized text as a string.
        """
        pass
