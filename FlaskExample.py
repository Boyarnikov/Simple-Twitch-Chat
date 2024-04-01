import datetime
from flask import Flask, render_template, request
import random
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


@app.route('/data', methods=['FETCH'])
def data():
    #print(request.json)
    requested_messages = pending_messages[-10:]
    if "from_id" in request.json and type(request.json["from_id"]) is int and 0 <= request.json["from_id"] < len(
            pending_messages):
        requested_messages = pending_messages[request.json["from_id"] + 1:]

    """
        return [{
            "username": "User" + str(random.randint(1, 100)),
            "text": " ".join([str(random.randint(1, 10**10)) for i in range(random.randint(1, 10))]),
            "time": current_time
        } for _ in range(random.randint(1, 3))]
    """

    return requested_messages


def start_app():
    # app.run(debug=True)
    app.run(debug=False)


def add_message(username, text):
    pending_messages.append({
        "username": username,
        "text": text,
        "time": datetime.datetime.now().strftime("%I:%M %p"),
        "id": len(pending_messages)
    })


if __name__ == "__main__":
    start_app()
