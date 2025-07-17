import logging

import pyttsx4
import threading
import time
from queue import Queue
from silero_tts.silero_tts import SileroTTS
from transliterate import translit
import pyglet
import time

from lib import Message, Module, Communicator

logger = logging.getLogger()


class TTSModule(Module):
    lines = Queue()
    tts = None

    def __init__(self, cm: Communicator):
        super().__init__(cm, "TTS")
        latest_model = SileroTTS.get_latest_model('ru')
        self.tts = SileroTTS(model_id='v4_ru', language='ru', speaker='baya', sample_rate=48000, device='cpu')
        speakers = self.tts .get_available_speakers()
        self.lines = Queue()

    async def _setup(self):
        self.cm.subscribe_to_tag(self.name, "TTS")

    async def post(self, msg: Message):
        if "TTS" in msg.tags:
            self.lines.put(msg.body.get('user_input'))

    async def _run(self):
        def thread_voice(_lines: Queue):
            engine = pyttsx4.init('sapi5')
            while True:
                if _lines.empty():
                    time.sleep(1)
                    continue
                text = translit(_lines.get(), "ru")

                self.tts.change_speaker("baya")
                # Synthesize speech from text
                print("Now talking:", "baya")

                # tts.tts(text, 'output.wav')
                self.tts.tts(text, 'output.wav')

                sound = pyglet.media.load("output.wav")
                sound.play()
                time.sleep(sound.duration + 1)

        threading.Thread(target=thread_voice, args=(self.lines,), daemon=True).start()
