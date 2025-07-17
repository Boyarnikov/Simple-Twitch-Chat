import datetime
from flask import Flask, render_template, request, jsonify, send_file
import base64
import random
import os
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
pending_messages = []

log = logging.getLogger('werkzeug')
log.disabled = True


@app.route("/")
def index():
    return render_template("chat.html")


@app.route("/support")
def support():
    return render_template("support.html")


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
    image_path = os.path.join('../emotes/', filename + ".png")
    print(f"looking for {image_path}")
    if os.path.exists(image_path):
        image_path = os.path.abspath(image_path)
        print(f"sending {image_path}")
        return send_file(image_path, mimetype='image/png')
    else:
        return 'Image not found', 404


def start_app():
    # app.run(debug=True)
    app.run(debug=True)


def add_message(username, text, emotes):
    pending_messages.append({
        "username": username,
        "text": text,
        "emotes": emotes,
        "time": datetime.datetime.now().strftime("%I:%M %p"),
        "id": len(pending_messages)
    })


if __name__ == "__main__":
    start_app()
