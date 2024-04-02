import pyttsx4
import threading
import time
from queue import Queue

lines = Queue()


def thread_voice(_lines: Queue):
    engine = pyttsx4.init('sapi5')
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
    queue_say("тест1")
    queue_say("тест2")
    queue_say("тест3")
    queue_say("тест4")
    queue_say("тест5")
    input()
