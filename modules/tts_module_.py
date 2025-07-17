
import logging

import pyttsx4
import threading
import time
from queue import Queue

from lib import Message, Module, Communicator

logger = logging.getLogger()

class TTSModuleSaiga(Module):
    lines = Queue()

    def __init__(self, cm: Communicator):
        super().__init__(cm, "TTS")

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
                text = _lines.get()
                engine.say(text)
                engine.runAndWait()
                engine.stop()

        threading.Thread(target=thread_voice, args=(self.lines,), daemon=True).start()
