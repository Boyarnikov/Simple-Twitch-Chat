import pyttsx4
import threading
import time
from queue import Queue

lines = Queue()
engine = pyttsx4.init('sapi5')


def thread_voice(_lines: Queue):
    while True:
        if _lines.empty():
            time.sleep(1)
            continue
        text = _lines.get()
        print(f"saying {text}")
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        print(f"done saying {text}")


threading.Thread(target=thread_voice, args=(lines,), daemon=True).start()


def queue_say(text):
    lines.put(text)


if __name__ == "__main__":

    voices = engine.getProperty('voices')
    for voice in voices:
        print(voice, voice.id)
        engine.setProperty('voice', voice.id)
        engine.say("Hello!")
        engine.runAndWait()
        engine.stop()
    input()

