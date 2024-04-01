import pyttsx4
import threading
import time
from queue import Queue

lines = Queue()

def thread_voice(_lines: Queue):
    while True:
        if _lines.empty():
            time.sleep(1)
            continue
        text = _lines.get()
        print(f"saying {text}")
        engine = pyttsx4.init()
        engine.say(text)
        engine.runAndWait()
        engine.stop()
        print(f"done saying {text}")

threading.Thread(target=thread_voice, args=(lines,), daemon=True).start()

lines.put("Hello!")
lines.put("hi!")
lines.put("how it's going!")
time.sleep(4)
lines.put("я так больше не могу")

input()