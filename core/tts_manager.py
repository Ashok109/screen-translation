import os
import tempfile
from gtts import gTTS
from playsound import playsound
import threading

class TTSManager:
    def __init__(self):
        self.is_playing = False
        self.lock = threading.Lock()

    def speak(self, text, lang):
        if not text:
            return

        with self.lock:
            if self.is_playing:
                return

            self.is_playing = True

        # Run TTS in a separate thread to avoid blocking the main UI
        threading.Thread(target=self._generate_and_play, args=(text, lang)).start()

    def _generate_and_play(self, text, lang):
        try:
            tts = gTTS(text=text, lang=lang)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                temp_filename = fp.name
            
            playsound(temp_filename)
            os.remove(temp_filename)

        except Exception as e:
            print(f"Error in TTS: {e}")
        finally:
            with self.lock:
                self.is_playing = False
