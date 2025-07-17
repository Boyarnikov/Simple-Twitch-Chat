import asyncio
import datetime
from flask import Flask, render_template, request, jsonify, send_file
import base64
import random
import os
import logging
import threading
from lib import Module, Message, Communicator

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
pending_messages = []

current_dir = os.path.dirname(__file__)  # Location of modules/flask.py
root_dir = os.path.abspath(os.path.join(current_dir, '..'))  # Move up to project root
emotes_dir = os.path.join(root_dir, 'emotes')

@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/support")
def support():
    return render_template("support.html")


@app.route("/simple")
def simple():
    return render_template("simple.html")


@app.route('/data', methods=['FETCH'])
def data():
    answer = dict()
    answer["data"] = pending_messages[-10:]
    if "from_id" in request.json:
        _index = request.json["from_id"]
        answer["data"] = pending_messages[_index + 1:]
        if request.json["from_id"] >= len(pending_messages):
            answer["reset_index"] = max(len(pending_messages) - 10, -1)
            answer["data"] = pending_messages[answer["reset_index"]:]
    return answer


@app.route('/get_image/<filename>', methods=['GET'])
def get_image(filename):
    image_path = os.path.join(emotes_dir, filename + ".png")
    print(f"looking for {image_path}")
    if os.path.exists(image_path):
        print(f"sending {image_path}")
        return send_file(image_path, mimetype='image/png')
    else:
        return 'Image not found', 404


def add_message(username, text, emotes):
    pending_messages.append({
        "username": username,
        "text": text,
        "emotes": emotes,
        "time": datetime.datetime.now().strftime("%I:%M %p"),
        "id": len(pending_messages)
    })


class FlaskModule(Module):
    def __init__(self, cm: Communicator):
        super().__init__(cm, "Flask")

    async def _setup(self):
        self.cm.subscribe_to_tag(self.name, "twitch_chat")

    async def post(self, msg: Message):
        if "twitch_chat" in msg.tags:
            add_message(msg.body["user"] ,msg.body["msg"], msg.body["emotes"])

    async def _run(self):
        threading.Thread(target=lambda: app.run( debug=True, use_reloader=False)).start()
